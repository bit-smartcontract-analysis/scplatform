package analyzer

import (
	"fmt"
	"go/ast"
	"go/build"
	"go/importer"
	"go/parser"
	"go/token"
	"go/types"
	"log"
	"reflect"
	"sort"
	"strings"

	"github.com/hyperledger-labs/chaincode-analyzer/util"
)

//
var logger *log.Logger

// An Analyzer analyzes Go source code
type Analyzer struct{}

// Analyze analyzes src
func (a *Analyzer) Analyze(logger *log.Logger, filename string, src []byte) ([]Problem, error) {
	return a.AnalyzeFiles(logger, map[string][]byte{filename: src})
}

// AnalyzeFiles analyzes a set of files.
// The argument is a map of filename to source.
func (a *Analyzer) AnalyzeFiles(l *log.Logger, files map[string][]byte) ([]Problem, error) {
	pkg := &pkg{
		fset:  token.NewFileSet(),
		files: make(map[string]*file),
	}
	logger = l
	var pkgName string
	for filename, src := range files {
		f, err := parser.ParseFile(pkg.fset, filename, src, 0)
		if err != nil {
			return nil, err
		}
		if pkgName == "" {
			pkgName = f.Name.Name
		} else if f.Name.Name != pkgName {
			return nil, fmt.Errorf("%s is the package %s, not %s", filename, f.Name.Name, pkgName)
		}

		pkg.files[filename] = &file{
			pkg:       pkg,
			f:         f,
			fset:      pkg.fset,
			src:       src,
			filename:  filename,
			functions: make(map[string]function),
		}
		if len(pkg.files) == 0 {
			return nil, nil
		}
	}

	return pkg.analyze(), nil
}

// Problem to keep nondet part
type Problem struct {
	Function         string
	VarName          string
	Position         token.Position // position in source file
	LineText         string         // the source line
	AffectedPosition token.Position
	AffectedLineText string
	Category         string // a short name for the general category of the problem
	Validity         bool
}

type byPosition []Problem

func (p byPosition) Len() int      { return len(p) }
func (p byPosition) Swap(i, j int) { p[i], p[j] = p[j], p[i] }
func (p byPosition) Less(i, j int) bool {
	pi, pj := p[i].Position, p[j].Position
	if pi.Filename != pj.Filename {
		return pi.Filename < pj.Filename
	}
	if pi.Line != pj.Line {
		return pi.Line < pj.Line
	}
	if pi.Column != pj.Column {
		return pi.Column < pj.Column
	}
	return p[i].LineText < p[j].LineText
}

// pkg represents a package
type pkg struct {
	fset      *token.FileSet
	files     map[string]*file
	typesPkg  *types.Package
	typesInfo *types.Info
	// sortable is the set of types in the package that implement sort.Interface
	sortable map[string]bool
	// main is whether this is a main package
	main     bool
	problems []Problem
}

func (p *pkg) analyze() []Problem {
	p.typeCheck()
	p.scanSortable()
	p.main = p.isMain()

	for _, f := range p.files {
		f.analyze()
	}
	sort.Sort(byPosition(p.problems))
	return p.problems
}

func (p *pkg) typeCheck() error {
	// go/types
	config := &types.Config{
		Error:    func(error) {},
		Importer: importer.Default(),
	}
	info := &types.Info{
		Types:      make(map[ast.Expr]types.TypeAndValue),
		Defs:       make(map[*ast.Ident]types.Object),
		Uses:       make(map[*ast.Ident]types.Object),
		Scopes:     make(map[ast.Node]*types.Scope),
		Selections: make(map[*ast.SelectorExpr]*types.Selection),
	}
	var anyFile *file
	var astFiles []*ast.File
	for _, f := range p.files {
		anyFile = f
		astFiles = append(astFiles, f.f)
	}
	pkg, err := config.Check(anyFile.f.Name.Name, p.fset, astFiles, info)
	p.typesPkg = pkg
	p.typesInfo = info
	return err
}

func (p *pkg) scanSortable() {
	p.sortable = make(map[string]bool)

	// bitfield for which method exist on each type
	const (
		Len = 1 << iota
		Less
		Swap
	)
	nmap := map[string]int{"Len": Len, "Less": Less, "Swap": Swap}
	has := make(map[string]int)
	for _, f := range p.files {
		f.walk(f.f, func(n ast.Node) bool {
			fn, ok := n.(*ast.FuncDecl)
			if !ok || fn.Recv == nil || len(fn.Recv.List) == 0 {
				return true
			}
			recv := receiverType(fn)
			if i, ok := nmap[fn.Name.Name]; ok {
				has[recv] |= i
			}
			return false
		})
	}
	for typ, ms := range has {
		if ms == Len|Less|Swap {
			p.sortable[typ] = true
		}
	}

}

func (p *pkg) isMain() bool {
	for _, f := range p.files {
		if f.isMain() {
			return true
		}
	}
	return false
}

func (f *file) isMain() bool {
	if f.f.Name.Name == "main" {
		return true
	}
	return false
}

// File represents a file being analyzed
type file struct {
	pkg       *pkg
	f         *ast.File
	fset      *token.FileSet
	src       []byte
	filename  string
	functions map[string]function
}

type function struct {
	funcname string
	// map[recvname]recvtype
	recv map[string]ast.Expr
	// map[paramname]paramtype
	params      map[string]ast.Expr
	putstates   []ast.Expr
	getstates   []ast.Expr
	isNondetRet bool
}

type mappings struct {
	// map[func][lhsVarName][]expr
	opMap        map[string]map[string][]ast.Expr
	dotImportMap map[string]bool
	importMap    map[string]string
	pointerMap   map[string]map[string]token.Pos
	// map[varName][Pos]bool
	resMap map[string]map[token.Pos]bool
}

// stored variables
type storedInfo struct {
	file
	// map[funcname]map[type][]expr
	targetVar map[string]map[string]map[token.Pos]ast.Expr
	mappings
	// map[funcname]map[varname]map[category]bool
	isValidProblem map[string]map[string]map[string]bool
	problems       []Problem
	currentFunc    string
	flagNonDet     map[string]bool
}

// initialize storedInfo of each function
func (si *storedInfo) init(funcName string) {
	si.opMap[funcName] = make(map[string][]ast.Expr)
	si.pointerMap[funcName] = make(map[string]token.Pos)
	si.isValidProblem[funcName] = make(map[string]map[string]bool)
	si.currentFunc = funcName

	si.targetVar[funcName] = make(map[string]map[token.Pos]ast.Expr)
	si.targetVar[funcName]["PutState"] = make(map[token.Pos]ast.Expr)
	si.targetVar[funcName]["GetState"] = make(map[token.Pos]ast.Expr)
	si.targetVar[funcName]["ForCond"] = make(map[token.Pos]ast.Expr)
	si.targetVar[funcName]["IfCond"] = make(map[token.Pos]ast.Expr)
	si.targetVar[funcName]["Return"] = make(map[token.Pos]ast.Expr)
	si.targetVar[funcName]["Switch"] = make(map[token.Pos]ast.Expr)
}

//
func createProblem(si *storedInfo, varName, targetFuncName, category string, pos token.Pos, origPos token.Pos) Problem {
	if _, ok := si.isValidProblem[targetFuncName][varName]; !ok {
		si.isValidProblem[targetFuncName][varName] = make(map[string]bool)
	}
	si.isValidProblem[targetFuncName][varName][category] = true
	return Problem{
		Function:         targetFuncName,
		VarName:          varName,
		Position:         si.fset.Position(pos),
		AffectedPosition: si.fset.Position(origPos),
		Category:         category,
		LineText:         util.SrcLine(si.src, si.fset.Position(pos)),
		AffectedLineText: util.SrcLine(si.src, si.fset.Position(origPos)),
		Validity:         true,
	}
}

// checkImports checks the existence of non det related imports
func (f *file) checkImports(si *storedInfo) {
	var abbrev string
	// i is ImportSpecs, f.f.Imports is []*ImportSpec
	for _, i := range f.f.Imports {
		// remove "
		fullpath := strings.Replace(i.Path.Value, "\"", "", -1)
		// i.Name is Ident and local package name (including ".") or nil
		if i.Name == nil {
			// e.g., import "github.com/.../shim" => shim.Success()
			if strings.Contains(fullpath, "/") {
				abbrev = strings.Split(fullpath, "/")[len(strings.Split(fullpath, "/"))-1]
			} else {
				abbrev = fullpath
			}
		} else {
			switch i.Name.Name {
			// e.g., "math/rand" & rand.Float32() => CallExpr: Fun: SelectorExpr: X: rand, Sel: Float32
			// e.g., . "math/rand" & Float32() => CallExpr: Fun: Ident  Float32
			case ".":
				si.dotImportMap[fullpath] = true
				abbrev = "."
			case "_":
				// nothing to do, since "_" is used for addressing dependency
			default:
				abbrev = i.Name.Name
			}
		}
		si.importMap[fullpath] = abbrev

		switch fullpath {
		case "math/rand":
			si.flagNonDet["Rand"] = true
		case "time":
			si.flagNonDet["Time"] = true
		case "net/http":
			si.flagNonDet["API"] = true
		case "os/exec":
			si.flagNonDet["SysCom"] = true
		case "os", "io/ioutil":
			si.flagNonDet["ReadFile"] = true
		case "github.com/hyperledger/fabric/core/chaincode/shim":
			si.flagNonDet["RangeQuery"] = true
			si.flagNonDet["CrossChan"] = true
		}

		// check External Library
		f.checkExternalLibrary(si, fullpath, abbrev, i.Pos())
	}
}

// check usage of global variable
func (f *file) checkGlobalVar(si *storedInfo) {
	for _, i := range f.f.Decls {
		if gd, ok := i.(*ast.GenDecl); ok {
			// Tok = IMPORT, CONST, TYPE, or VAR
			if gd.Tok == token.VAR {
				if _, ok := si.isValidProblem["Global Space"]; !ok {
					si.isValidProblem["Global Space"] = make(map[string]map[string]bool)
				}
				si.problems = append(si.problems, createProblem(si, "", "Global Space", "Global Variable", gd.TokPos, gd.TokPos))
			}
		}
	}
}

// for checking interface satisfaction, we directory check the methods' names and the signatures
// if the struct satisfies Chaincode interface, it must have the following methods
// Init(stub ChaincodeStubInterface) pb.Response
// Invoke(stub ChaincodeStubInterface) pb.Response
func (f *file) checkFieldDeclaration(si *storedInfo) {
	stMap := make(map[string]map[string]bool)
	stLoc := make(map[string]token.Pos)
	for _, i := range f.f.Decls {
		if gd, ok := i.(*ast.GenDecl); ok {
			if gd.Tok == token.TYPE {
				for _, spec := range gd.Specs {
					if typespec, ok := spec.(*ast.TypeSpec); ok {
						if st, ok := typespec.Type.(*ast.StructType); ok {
							if st.Fields.List != nil {
								stMap[typespec.Name.Name] = make(map[string]bool)
								stMap[typespec.Name.Name]["Init"] = false
								stMap[typespec.Name.Name]["Invoke"] = false
								stLoc[typespec.Name.Name] = gd.TokPos
							}
						}
					}
				}
			}
		}
	}

	for _, i := range f.f.Decls {
		if fd, ok := i.(*ast.FuncDecl); ok {
			// check the func is method?
			if fd.Recv != nil {
				if fd.Name.Name == "Init" || fd.Name.Name == "Invoke" {
					var recvname string
					if _, ok := fd.Recv.List[0].Type.(*ast.StarExpr); ok {
						recvname = fd.Recv.List[0].Type.(*ast.StarExpr).X.(*ast.Ident).Name
					} else {
						recvname = fd.Recv.List[0].Type.(*ast.Ident).Name
					}
					if _, ok := stMap[recvname]; ok {
						// check params (fd.Type.Params): params should include
						// shim.ChaincodeStubInterface (github.com/hyperledger/fabric/core/chaincode/shim)
						params := fd.Type.Params
						pkgName := si.importMap["github.com/hyperledger/fabric/core/chaincode/shim"]
						pflag := false
						for _, field := range params.List {
							if pkgName == "." {
								if id, ok := field.Type.(*ast.Ident); ok {
									if "ChaincodeStubInterface" == id.Name {
										pflag = true
									}
								}
							} else {
								if se, ok := field.Type.(*ast.SelectorExpr); ok {
									if pkgName == se.X.(*ast.Ident).Name && "ChaincodeStubInterface" == se.Sel.Name {
										pflag = true
									}
								}
							}
						}
						if pflag {
							// check returns (fd.Type.Results): return should be
							// peer.Response (github.com/hyperledger/fabric/peer)
							results := fd.Type.Results
							pkgName = si.importMap["github.com/hyperledger/fabric/protos/peer"]
							for _, field := range results.List {
								if pkgName == "." {
									if id, ok := field.Type.(*ast.Ident); ok {
										if "Response" == id.Name {
											stMap[recvname][fd.Name.Name] = true
										}
									}
								} else {
									if se, ok := field.Type.(*ast.SelectorExpr); ok {
										if pkgName == se.X.(*ast.Ident).Name && "Response" == se.Sel.Name {
											stMap[recvname][fd.Name.Name] = true
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
	for recvname, methmap := range stMap {
		if methmap["Init"] && methmap["Invoke"] {
			if _, ok := si.isValidProblem["Declaration"]; !ok {
				si.isValidProblem["Declaration"] = make(map[string]map[string]bool)
			}
			si.problems = append(si.problems, createProblem(si, recvname, "Declaration", "FieldDeclaration", stLoc[recvname], stLoc[recvname]))
		}
	}
}

// check the usage of library other than go standard library and fabric library
// isInStd
func (f *file) checkExternalLibrary(si *storedInfo, fullpath, abbrev string, pos token.Pos) {
	if !strings.Contains(fullpath, "github.com/hyperledger/fabric") {
		pkg, _ := build.Import(fullpath, "", 0)
		if !pkg.Goroot {
			if _, ok := si.isValidProblem["Imports"]; !ok {
				si.isValidProblem["Imports"] = make(map[string]map[string]bool)
			}
			si.problems = append(si.problems, createProblem(si, "", "Imports", "External Library", pos, pos))
		}
	}
}

// checkShim is to check the selectorexpr's X is from shim.ChaincodeStubInterface or not
func checkShim(si *storedInfo, id *ast.Ident) bool {
	if field, ok := id.Obj.Decl.(*ast.Field); ok {
		if fieldType, ok := field.Type.(*ast.SelectorExpr); ok {
			x := fieldType.X.(*ast.Ident).Name
			sel := fieldType.Sel.Name
			if x == si.importMap["github.com/hyperledger/fabric/core/chaincode/shim"] && sel == "ChaincodeStubInterface" {
				return true
			}
		}
	}
	return false
}

// pickup target var
func pickUpTargetVar(si *storedInfo, n ast.Node) {
	switch t := n.(type) {
	case *ast.CallExpr:
		if se, ok := t.Fun.(*ast.SelectorExpr); ok {
			if se.Sel.Name == "PutState" {
				if checkShim(si, se.X.(*ast.Ident)) {
					fc := si.file.functions[si.currentFunc]
					for _, expr := range t.Args {
						si.targetVar[si.currentFunc]["PutState"][expr.Pos()] = expr
					}
					// pick up key
					fc.putstates = append(fc.putstates, t.Args[0])
					si.file.functions[si.currentFunc] = fc
				}
			} else if se.Sel.Name == "GetState" {
				if checkShim(si, se.X.(*ast.Ident)) {
					fc := si.file.functions[si.currentFunc]
					fc.getstates = append(fc.getstates, t.Args[0])
					si.file.functions[si.currentFunc] = fc
				}
			}
		}
	case *ast.ForStmt:
		// t.Init => i := 0 (AssignStmt); t.Cond => i < 10 (BinaryExpr); t.Post => i++ (IncDecStmt)
		if t.Init != nil {
			walkStmt(si, t.Init)
		}
		if t.Cond != nil {
			si.targetVar[si.currentFunc]["ForCond"][t.Cond.Pos()] = t.Cond
		}
		if t.Post != nil {
			walkStmt(si, t.Post)
		}
	case *ast.IfStmt:
		if t.Cond != nil {
			si.targetVar[si.currentFunc]["IfCond"][t.Cond.Pos()] = t.Cond
		}
	case *ast.ReturnStmt:
		// TODO: need to reconsider
		/*
			for _, expr := range t.Results {
				si.targetVar[si.currentFunc]["Return"][expr.Pos()] = expr
			}
		*/
	case *ast.SwitchStmt:
		// Init: switch i := 1; i {} => i := 1
		if t.Init != nil {
			walkStmt(si, t.Init)
		}
		if t.Tag != nil {
			si.targetVar[si.currentFunc]["Switch"][t.Pos()] = t.Tag
		}
	case *ast.TypeSwitchStmt:
		// switch v := value.(type) {}
		if t.Init != nil {
			walkStmt(si, t.Init)
		}
		if t.Assign != nil {
			walkStmt(si, t.Init)
		}
	default:
		// Nothing to do
	}
}

// walk assignstmt and store op mapings
// AssignStmt { Lhs []Expr, TokPos token.Pos, Tok token.Token, Rhs []Expr}
// token.DEFINE => ':=', token.ASSIGN => '=', token.ADD_ASSIGN => '+=', and other assignment token?
func walkAssignStmt(si *storedInfo, n *ast.AssignStmt) {
	for i, lh := range n.Lhs {
		var varName string
		switch t := lh.(type) {
		case *ast.Ident:
			varName = t.Name
		case *ast.IndexExpr:
			varName = util.IdName(t)
		case *ast.SelectorExpr:
			// X(expr).Sel(ident) => X_Sel
			// This only expects accesses to the member of structs
			varName = util.IdName(t)
		default:
			logger.Println("[WARN][walkAssignStmt] Currently, the following type is not supported at walkAssignStmt", reflect.TypeOf(t), si.fset.Position(t.Pos()))
			// Need to consider?
			// ArrayType, BadExpr, BasicLit, BinaryExpr, CallExpr, ChanType, CompositeLit,
			// Ellipsis, FuncType, FuncLit, IndexExpr, InterfaceType, KeyValueExpr, MapType,
			// ParenExpr, SliceExpr, StarExpr, TypeAssertExpr, UnaryExpr
		}
		if varName != "_" && varName != "" { //&& varName != "err" {
			// e.g., a, b, c := 10, 20, 30
			if len(n.Lhs) == len(n.Rhs) {
				if varName != "err" {
					si.opMap[si.currentFunc][varName] = append(si.opMap[si.currentFunc][varName], n.Rhs[i])
				}
				pickUpTargetVar(si, n.Rhs[i])
				// picking up pointer declaration
				if n.Tok == token.DEFINE {
					switch t := n.Rhs[i].(type) {
					case *ast.UnaryExpr:
						// e.g., var p := &Hoge{}
						if t.Op.String() == "&" {
							si.pointerMap[si.currentFunc][varName] = n.Pos()
						}
					case *ast.CallExpr:
						if id, ok := t.Fun.(*ast.Ident); ok {
							if id.Name == "new" {
								si.pointerMap[si.currentFunc][varName] = n.Pos()
							}
						}
					}
				}
				// e.g., a, b := callFunc()
			} else if len(n.Lhs) > len(n.Rhs) {
				if varName != "err" {
					si.opMap[si.currentFunc][varName] = append(si.opMap[si.currentFunc][varName], n.Rhs[0])
				}
				if len(n.Rhs) == 1 {
					pickUpTargetVar(si, n.Rhs[0])
				} else {
					logger.Println("[WARN][walkAssignStmt] Currently, the case (len(Lhs) > len(Rhs) && len(Rhs) > 1) is not considered ", si.fset.Position(lh.Pos()))
				}
			} else {
				// this ( len(n.Lhs) < len(n.Rhs) ) will not be happened?
				logger.Println("[WARN][walkAssignStmt] Currently, the case (len(Lhs) < len(Rhs)) is not considered ", si.fset.Position(lh.Pos()))
			}
		}
	}
}

// walk declstmt
// at this function, we want to capture following information
// - vars which declared as pointer
// - declared vars
// DeclStmt { Decl // *GenDecl with CONST, TYPE, VAR or IMPORT }
func walkDeclStmt(si *storedInfo, n *ast.DeclStmt) {
	gd := n.Decl.(*ast.GenDecl)
	switch gd.Tok {
	case token.VAR:
		for _, spec := range gd.Specs {
			// the spec should be ValueSpec (for CONST and VAR), not ImportSpec (IMPORT) or TypeSpec (TYPE)
			// NOTE: if this declaration does not assign any value to the var, the valSpec.Values[i] is nil
			if valSpec, ok := spec.(*ast.ValueSpec); ok {
				// this is the case that declaration with value assign, i.e., var k = rnd % 2
				for i, varName := range valSpec.Names {
					if len(valSpec.Values) > 0 {
						si.opMap[si.currentFunc][varName.Name] = append(si.opMap[si.currentFunc][varName.Name], valSpec.Values[i])
					} else {
						si.opMap[si.currentFunc][varName.Name] = append(si.opMap[si.currentFunc][varName.Name], nil)
					}
					if _, ok := valSpec.Type.(*ast.StarExpr); ok {
						si.pointerMap[si.currentFunc][varName.Name] = gd.Pos()
					}
				}
			}
		}
	default:
		// nothing to do (i.e., the cases of IMPORT and TYPE)
	}
}

// ExprStmt is a statement which just call some function?
// e.g., logger.Info("### example_cc0 Init ###")
func walkExprStmt(si *storedInfo, n *ast.ExprStmt) {
	pickUpTargetVar(si, n.X)
}

// ForStmt (this stmt is not include for range statement)
// e.g., for i := 0; i < 10; i++ { Body }
func walkForStmt(si *storedInfo, n *ast.ForStmt) {
	pickUpTargetVar(si, n)
	walkStmt(si, n.Body)
}

// GoStmt
func walkGoStmt(si *storedInfo, n *ast.GoStmt) {
	si.problems = append(si.problems, createProblem(si, "", si.currentFunc, "Goroutine", n.Go, n.Go))
}

// IfStmt
// pick up condition statements and walk body inside ifstmt
func walkIfStmt(si *storedInfo, n *ast.IfStmt) {
	pickUpTargetVar(si, n)
	walkStmt(si, n.Body)
}

// RangeStmt
// for key, value := range X { Body }
func walkRangeStmt(si *storedInfo, n *ast.RangeStmt) {
	pickUpTargetVar(si, n)
	walkStmt(si, n.Body)
	checkMapIter(si, n)
}

func walkReturnStmt(si *storedInfo, n *ast.ReturnStmt) {
	pickUpTargetVar(si, n)
}

func walkSwitchStmt(si *storedInfo, n *ast.SwitchStmt) {
	pickUpTargetVar(si, n)
	// n.Body is CaseClause only
	walkCaseClause(si, n.Body.List[0].(*ast.CaseClause))
}

func walkTypeSwitchStmt(si *storedInfo, n *ast.TypeSwitchStmt) {
	pickUpTargetVar(si, n)
	// n.Body is CaseClause only
	walkCaseClause(si, n.Body.List[0].(*ast.CaseClause))
}

func walkCaseClause(si *storedInfo, c *ast.CaseClause) {
	for _, stmt := range c.Body {
		walkStmt(si, stmt)
	}
}

func walkStmt(si *storedInfo, n ast.Stmt) {
	if n != nil {
		switch t := n.(type) {
		case *ast.AssignStmt:
			walkAssignStmt(si, t)
		case *ast.BlockStmt:
			for _, stmt := range t.List {
				walkStmt(si, stmt)
			}
		case *ast.DeclStmt:
			walkDeclStmt(si, t)
		case *ast.ExprStmt:
			walkExprStmt(si, t)
		case *ast.ForStmt:
			walkForStmt(si, t)
		case *ast.GoStmt:
			walkGoStmt(si, t)
		case *ast.IfStmt:
			walkIfStmt(si, t)
		case *ast.RangeStmt:
			// range statement with map object will occur non-determination due to random output of map object
			walkRangeStmt(si, t)
		case *ast.ReturnStmt:
			walkReturnStmt(si, t)
		case *ast.SwitchStmt:
			walkSwitchStmt(si, t)
		case *ast.TypeSwitchStmt:
			walkTypeSwitchStmt(si, t)
		default:
			// n.List is []ast.Stmt
			// NOTE: Currently, we do not consider the following statements
			// BadStmt, BranchStmt (break, continue, goto, fallthrough), DeferStmt
			// EmptyStmt, IncDecStmt, LabeledStmt, SendStmt, SelectStmt,
			logger.Println("[WARN][walkStmt] Currently, the following type is not supported at walkStmt", reflect.TypeOf(t), si.fset.Position(t.Pos()))
		}
	}
}

// walk funcdecl to extract information about the func
func (f *file) walkFuncDecl(si *storedInfo, n *ast.FuncDecl) {
	recv := make(map[string]ast.Expr)
	params := make(map[string]ast.Expr)
	funcname := n.Name.Name

	// if method
	if n.Recv != nil {
		recv[n.Recv.List[0].Names[0].Name] = n.Recv.List[0].Type
	}

	// params
	for _, field := range n.Type.Params.List {
		for _, name := range field.Names {
			params[name.Name] = field.Type
		}
	}

	// return
	si.file.functions[funcname] = function{funcname: funcname, recv: recv, params: params, isNondetRet: false}
}

// storeInfo is storing nodes in the function by walking the body
func (f *file) storeInfo(si *storedInfo) {
	f.walk(f.f, func(n ast.Node) bool {
		if n != nil {
			switch t := n.(type) {
			case *ast.FuncDecl:
				si.init(t.Name.Name)
				f.walkFuncDecl(si, t)
				walkStmt(si, t.Body)
				return false
			default:
				return true
			}
		}
		return false
	})
}

// entry point of detecting problems
func (f *file) detectProblems(si *storedInfo) {
	for funcName := range si.targetVar {
		for varPlace := range si.targetVar[funcName] {
			for targetPos, varExpr := range si.targetVar[funcName][varPlace] {
				for category, flag := range si.flagNonDet {
					si.resMap = make(map[string]map[token.Pos]bool)
					if flag {
						f.checkNonDetermin(si, funcName, varPlace, category, "", varExpr, targetPos)
					}
				}
			}
		}
	}
	f.checkReadYourWrite(si)
}

// checkReadYourWrite detect an usage of GetState after calling PutState
// It is difficult to ensure that the keys of GetState and PutState are the same.
// Hence, currently, we just check the operations between GetState and PutState
func (f *file) checkReadYourWrite(si *storedInfo) {
	for fcname, fc := range si.file.functions {
		if len(fc.getstates) > 0 {
			// in same func
			if len(fc.putstates) > 0 {
				for _, gsarg := range fc.getstates {
					for _, psarg := range fc.putstates {
						if gsarg.Pos() > psarg.Pos() {
							if isSameKey(si, gsarg, psarg, fcname) {
								si.problems = append(si.problems, createProblem(si, "", fcname, "ReadYourWrite", psarg.Pos(), gsarg.Pos()))
							}
						}
					}
				}
			} else {
				// TODO
				logger.Println("[WARN][checkReadYourWrite] For now, this tool does not support the case that PutState and GetState are in different functions.")
			}
		}
	}
}

// For now this just checks the two vars names (of GetState and PutState) are same or not
// Maybe there are better ways to do such things
func isSameKey(si *storedInfo, a, b ast.Expr, fcname string) bool {
	if reflect.TypeOf(a) == reflect.TypeOf(b) {
		switch t := a.(type) {
		case *ast.BasicLit:
			if t.Value == b.(*ast.BasicLit).Value {
				return true
			}
		case *ast.Ident:
			if t.Name == b.(*ast.Ident).Name {
				if ops, ok := si.opMap[fcname][t.Name]; ok {
					for _, op := range ops {
						// in this case, value of the Identifier might be changed after PutState and before GetState
						if op != nil && a.Pos() > op.Pos() && b.Pos() < op.Pos() {
							return false
						}
					}
				}
				return true
			}
			return false
		default:
			logger.Println("[WARN][isSameKey] For now, this tool does not support the following types", reflect.TypeOf(a), reflect.TypeOf(b))
			return false
		}
	} else {
		logger.Println("[WARN][isSameKey] For now, this tool does not support the case that compared keys have different types", reflect.TypeOf(a), reflect.TypeOf(b))
	}

	return false
}

// checkMapIter checks the usage of map iteration
func checkMapIter(si *storedInfo, n *ast.RangeStmt) {
	typesInfo := si.pkg.typesInfo
	switch t := n.X.(type) {
	case *ast.Ident, *ast.IndexExpr, *ast.SelectorExpr:
		// n.X is value to range over
		targetVarType := typesInfo.TypeOf(t)
		targetVarName := util.IdName(t)
		if targetVarName == "" || targetVarType == nil {
			logger.Println("[WARN][checkMapIter] Weird case is happened at checkMapIter. Please check")
		} else {
			// check the targetVarType is map or not
			if strings.HasPrefix(targetVarType.String(), "map") {
				si.problems = append(si.problems, createProblem(si, targetVarName, si.currentFunc, "MapIter", n.Pos(), n.Pos()))
			}
		}
	default:
		// NOTE: Do we need consider other cases?
		logger.Println("[WARN][checkMapIter] It happened that we did not considered: ", reflect.TypeOf(n.X))
	}

}

//
func checkAPI(si *storedInfo, t *ast.SelectorExpr, targetFuncName, targetVarName, name string, origPos token.Pos) (ret bool) {
	if exprs, ok := si.opMap[targetFuncName][name]; ok {
		if len(exprs) == 1 {
			if _, ok := exprs[0].(*ast.UnaryExpr); ok {
				if exprs[0].(*ast.UnaryExpr).Op.String() == "&" && exprs[0].(*ast.UnaryExpr).X.(*ast.CompositeLit).Type.(*ast.SelectorExpr).Sel.Name == "Client" {
					si.problems = append(si.problems, createProblem(si, targetVarName, targetFuncName, "API", t.Sel.NamePos, origPos))
					ret = true
				}
			}
		} else {
			logger.Println("[WARN][checkNonDetermin] NEED TO CONSIDER?: This is the case that client := &http.Client might be reassigned")
		}
	}
	return ret
}

//
func (f *file) checkAssignOps(si *storedInfo, targetFuncName, name, category string, origPos token.Pos) (ret bool) {
	if ops, ok := si.opMap[targetFuncName][name]; ok {
		for _, op := range ops {
			if op != nil {
				if op.Pos() <= origPos {
					if res, ok := si.resMap[name][op.Pos()]; ok {
						ret = res
					} else {
						ret = f.checkNonDetermin(si, targetFuncName, name, category, "AssignStmt", op, origPos)
						si.resMap[name] = make(map[token.Pos]bool)
						si.resMap[name][op.Pos()] = ret
					}
					if res, ok := si.isValidProblem[targetFuncName][name][category]; ok {
						if res != ret {
							si.isValidProblem[targetFuncName][name][category] = ret
						}
					}
				}
			}
		}
	}
	return ret
}

func (f *file) checkSelectorExprInCallExpr(si *storedInfo, t *ast.SelectorExpr, targetFuncName, targetVarName, category string, origPos token.Pos) (ret bool) {
	switch x := t.X.(type) {
	case *ast.Ident:
		switch category {
		case "API":
			// for client, e.g., client = &http.Client{}; client.Get()
			ret = checkAPI(si, t, targetFuncName, targetVarName, x.Name, origPos)
		case "RangeQuery", "CrossChan":
			if expr, ok := si.functions[targetFuncName].params[x.Name]; ok {
				if se, ok := expr.(*ast.SelectorExpr); ok {
					if se.X.(*ast.Ident).Name == si.importMap[util.LibFullPath[category][0]] {
						if util.Keywords[category][t.Sel.Name] {
							si.problems = append(si.problems, createProblem(si, targetVarName, targetFuncName, category, t.Sel.NamePos, origPos))
							ret = true
						}
					}
				}
			}
		default:
			// is the library Go Standard Libs?
			// if the pacakge declared with abbrev convert to original package name
			for _, libFullPath := range util.LibFullPath[category] {
				if util.Keywords[category][t.Sel.Name] && si.importMap[libFullPath] == x.Name {
					si.problems = append(si.problems, createProblem(si, targetVarName, targetFuncName, category, t.Sel.NamePos, origPos))
					ret = true
				}
			}
		}
		// e.g., t := time.Now(); a := t.Format()
		ret = ret || f.checkAssignOps(si, targetFuncName, x.Name, category, origPos)
	case *ast.CallExpr:
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "SelectorExpr", x, origPos)
	default:
		name := util.IdName(x)
		ret = f.checkAssignOps(si, targetFuncName, name, category, origPos)
	}
	return ret
}

// trace operations and find non-determinism
func (f *file) checkNonDetermin(si *storedInfo, targetFuncName, targetVarName, category, parentNodeType string, targetVarExpr ast.Expr, origPos token.Pos) (ret bool) {
	switch t := targetVarExpr.(type) {
	case *ast.ArrayType:
		// e.g., [3]int
		return ret
	case *ast.BasicLit:
		// e.g., 0
		return ret
	case *ast.BinaryExpr:
		// e.g., X + Y, X > Y
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "BinaryExpr", t.X, origPos)
		ret = ret || f.checkNonDetermin(si, targetFuncName, targetVarName, category, "BinaryExpr", t.Y, origPos)
		return ret
	case *ast.CallExpr:
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "CallExpr", t.Fun, origPos)
		if t.Args != nil {
			for _, expr := range t.Args {
				ret = ret || f.checkNonDetermin(si, targetFuncName, targetVarName, category, "CallExpr", expr, origPos)
			}
		}
		return ret
	case *ast.CompositeLit:
		// e.g., fuga{1} and []int{1, 2, 3}
		for _, o := range t.Elts {
			if o != nil {
				ret = ret || f.checkNonDetermin(si, targetFuncName, targetVarName, category, "CompositeLit", o, origPos)
			}
		}
		return ret
	case *ast.Ident:
		// e.g., A
		name := t.Name
		if name == "err" || name == "nil" {
			return ret
		}

		// checking memos of results to avoid infinite loop
		if _, ok := si.resMap[name]; ok {
			var p = token.NoPos
			if res, ok := si.resMap[name][t.Pos()]; ok {
				return res
			}
			for pos, res := range si.resMap[name] {
				if p < pos && pos < t.Pos() {
					p = pos
					ret = res
				}
			}
			return ret
		}
		si.resMap[name] = make(map[token.Pos]bool)

		// is the Identifier pointer?
		if category == "Pointer" {
			// for the case of pointer
			if pos, ok := si.pointerMap[targetFuncName][name]; ok {
				si.problems = append(si.problems, createProblem(si, name, targetFuncName, "Pointer", pos, origPos))
				ret = true
			}
			return ret
		}

		// is the package declared with dot? && is it in target keywords?
		if util.Keywords[category][name] {
			si.problems = append(si.problems, createProblem(si, name, targetFuncName, category, t.NamePos, origPos))
			return true
		}

		// check assign operations of the variable
		ret = f.checkAssignOps(si, targetFuncName, name, category, origPos)
		return ret
	case *ast.IndexExpr:
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "IndexExpr", t.X, origPos)
		ret = ret || f.checkNonDetermin(si, targetFuncName, targetVarName, category, "IndexExpr", t.Index, origPos)
		return ret

	case *ast.SelectorExpr:
		// e.g., shim.Error()
		if parentNodeType == "CallExpr" {
			ret = f.checkSelectorExprInCallExpr(si, t, targetFuncName, targetVarName, category, origPos)
		} else {
			// e.g., access to a member of the structure
			// check assign operations of the variable
			name := util.IdName(t)
			ret = f.checkAssignOps(si, targetFuncName, name, category, origPos)
		}
		return ret
	case *ast.KeyValueExpr:
		ret = ret || f.checkNonDetermin(si, targetFuncName, targetVarName, category, "KeyValueExpr", t.Key, origPos)
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "KeyValueExpr", t.Value, origPos)
		return ret
	case *ast.ParenExpr:
		// e.g., (1 + 2)/3, Lparen, X Expr, Rparen.
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "ParenExpr", t.X, origPos)
		return ret
	case *ast.UnaryExpr:
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "UnaryExpr", t.X, origPos)
		return ret
	case *ast.StarExpr:
		ret = f.checkNonDetermin(si, targetFuncName, targetVarName, category, "StarExpr", t.X, origPos)
		return ret
	default:
		// NEED TO CONSIDER?:
		// ChanType, Ellipsis (i.e., "..."), FuncType, FuncLit, InterfaceType, MapType, SliceExpr, StructType, TypeAssertExpr
		logger.Println("[WARN][checkNonDetermin] This is not considered type of expr", reflect.TypeOf(t), si.fset.Position(t.Pos()))
		return ret
	}
}

// output is function to output problems for debugging
func output(si *storedInfo) {
	fmt.Println("!!! OUTPUT FOR DEBUG !!!")
	sort.Sort(byPosition(si.problems))
	fmt.Println("# Result")
	for _, p := range si.problems {
		fmt.Println("## Category ", p.Category)
		fmt.Println("## Function ", p.Function)
		fmt.Println("## VarName ", p.VarName)
		fmt.Println("## Position ", p.Position)
		fmt.Println("## Validity ", p.Validity)
		fmt.Println(p.LineText)
	}
}

func isValid(si *storedInfo) {
	for _, p := range si.problems {
		if si.isValidProblem[p.Function][p.VarName][p.Category] {
			p.Validity = true
		} else {
			p.Validity = false
		}
	}
}

// siInit() initialize structure to store information
func (f *file) siInit() *storedInfo {
	return &storedInfo{
		file:      *f,
		targetVar: make(map[string]map[string]map[token.Pos]ast.Expr),
		mappings: mappings{
			opMap:        make(map[string]map[string][]ast.Expr),
			dotImportMap: make(map[string]bool),
			importMap:    make(map[string]string),
			pointerMap:   make(map[string]map[string]token.Pos),
		},
		isValidProblem: make(map[string]map[string]map[string]bool),
		// Pointer is always true
		flagNonDet: map[string]bool{"Rand": false, "Time": false, "API": false,
			"SysCom": false, "ReadFile": false, "RangeQuery": false, "CrossChan": false, "Pointer": true},
	}
}

func (f *file) analyze() {
	si := f.siInit()
	f.checkImports(si)
	f.checkGlobalVar(si)
	f.checkFieldDeclaration(si)
	f.storeInfo(si)
	f.detectProblems(si)
	isValid(si)
	f.pkg.problems = append(f.pkg.problems, si.problems...)
}

// receiverType returns the named type of the method receiver, sans "*",
// or "invalid-type" if fn.Recv is ill formed
func receiverType(fn *ast.FuncDecl) string {
	switch t := fn.Recv.List[0].Type.(type) {
	case *ast.Ident:
		return t.Name
	case *ast.StarExpr:
		if id, ok := t.X.(*ast.Ident); ok {
			return id.Name
		}
	}
	return "invalid-type"
}

func (f *file) walk(n ast.Node, fn func(ast.Node) bool) {
	ast.Walk(walker(fn), n)
}

// walker adapts a function to satisfy the ast.Visitor interface
// The function returns whether the walk should proceed into the node's children
type walker func(ast.Node) bool

func (w walker) Visit(n ast.Node) ast.Visitor {
	if w(n) {
		return w
	}
	return nil
}
