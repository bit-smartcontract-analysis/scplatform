
<template>
  <div>
    <h2 class="table-title">合约语言介绍</h2>
    <el-table :data="tableData"  :span-method="objectSpanMethod" border stripe row-style="rowStyleMethod">
      <el-table-column prop="name" label="合约语言" width="150" align="left" >
      </el-table-column>
      <el-table-column prop="language" label="主要漏洞" width="120" align="left">
      </el-table-column>
      <el-table-column prop="intro" label="详情介绍" width="1020" align="left">
      </el-table-column>
    </el-table>
  </div>
</template>


<script>
export default {
  name: "AppLanguage",
  data() {
    return {
      tableArr: [],
      pos:0,
     
      tableData: [
        {
          name: "Solidity",
          language: "整数上溢和下溢",
          intro:
            "整数上溢和下溢，也被称为算数问题，SWC-101。Solidity智能合约支持的无符号整数变量步长以8递增，从uint8一直到uint256；同样带符号数也是从int8到int256。如果一个数字存储在uint8类型中，这意味着该数字存储在一个8位无符号数中，范围从0到255。此时若将一个超过该范围的算术运算的结果存入uint8，以太坊虚拟机并不会报错而回滚状态，而是简单截断运算结果的高位后将该数存入uint8类型变量中。此时运算结果异常，产生整数溢出的错误。整数上溢和下溢在智能合约中尤其危险，在Solidity合约中使用整型数据类型的情况非常普遍，而且大多数开发人员不选择使用SafeMath安全库。一旦存在溢出漏洞，代码的一些不起眼的算数运算部分都可能成为攻击者为了转移以太币或阻止程序正常运行的攻击目标。",
        },
        {
          name: "Solidity",
          language: "未检查调用返回值",
          intro:
            "也被称为异常处理漏洞、静默失败调用等，SWC-104。其实质上也是源于Solidity提供的底层函数如call()、delegatecall()和send()这些被称为低级别调用的函数。一般情况下，合约会终止执行并回滚至前一状态以面对执行过程中抛出的异常。但是当使用低级别调用函数调用其他合约时被调用合约抛出异常，作为调用者的原合约执行仍会继续，低级别调用函数会返回一个flase的布尔值。这也导致若合约编写人员未检查这种低级别调用的返回值，无法确定调用是否成功，进而后续的代码逻辑可能将陷入巨大的问题当中。",
        },
        {
          name: "Solidity",
          language: "不受保护的自毁指令",
          intro: "也称意外自杀漏洞，以太冻结漏洞，被认为是访问控制漏洞的一种形式，SWC-106。由于Solidity语言提供了合约自毁的接口selfdestruct()，若是在编写合约中提供了该接口，使用过程中却由于访问控制缺失或不足，恶意方可以自毁合同。合约自毁和以太币冻结是一体两面，合约自毁是因，以太币被冻结是果。当一个合约自毁后，合约持有的以太币和之后向该合约地址发送的以太币（实际上相当于给空地址发送以太币）都将永久冻结，无法追回。",
        },
        {
          name: "Solidity",
          language: "重入",
          intro: "也被称为递归调用或调用未知，SWC-107。漏洞的产生本质上源于Solidity语言为合约提供的fallback()函数。当使用Solidity常见的转账方式transfer()、send()和call.vale()()将以太币发送到一个地址时，若该地址是用户账户，则其余额会增加相应的以太币数量；若该地址属于一个合约账户，会触发其fallback()函数。恶意设置的fallback()函数能在转账结束前再次回调发起转账的合约之中，导致其他调用以不被期望的方法进行。",
        },
        {
          name: "Solidity",
          language: "不安全的Delegatecall",
          intro: "被认为是访问控制漏洞的一种，SWC-112。从漏洞名字上不难看出，该漏洞与Solidity语言提供的一种调用模式delegatecall有关。该调用的特点是目标代码的执行环境是调用者合约，并且保证msg.sender与msg.value的值不变。这意味着智能合约通过delegatecall可以在运行时从不同地址动态加载其他合约代码，同时存储、当前地址和余额信息仍然依赖于调用合约。因此调用不受信任的合约是非常危险的，因为目标地址处的代码可以更改调用者的任何存储值，并完全控制调用者的余额。",
        },
        {
          name: "Solidity",
          language: "时间顺序依赖",
          intro: "也被称为抢先执行、竞争条件漏洞，SWC-114。这个漏洞往往被认为是以太坊区块链系统层上的漏洞([19])。以太坊网络中的矿工可以决定发布到全网络上的交易执行的顺序，当然绝大部分情况下交易中包含的汽油费越多，矿工会以更快的速度挖掘。加上以太坊网络的公开透明性质，所有人都可以观察到所有发布到网上等待矿工处理的交易内容。某些情况下合约的交易顺序存在重要意义，例如一个智能合约会给予第一个解谜的用户以太币作为奖励，恶意用户守候在区块链网络中监听相应的解谜合约，在观察到之后以更高的汽油费复制解谜合约，抢先交易以获得以太币奖励，从而达到不劳而获的可怕结果。",
        },
        {
          name: "Solidity",
          language: "通过tx.origin授权",
          intro: "被认为是访问控制漏洞的一种，SWC-115。tx.origin是Solidity语言中的一个全局变量，它能遍历整个调用栈并返回最初发送调用的账户地址。在合约中如果使用tx.origin权限检查，恶意用户可以构造fallback函数，再通过网络钓鱼等手段诱使被害者合约进行转账操作，从而造成以太币损失。",
        },
        {
          name: "Solidity",
          language: "区块变量作为时间代理",
          intro: "也被称作时间操纵漏洞，包含时间戳依赖漏洞，SWC-116。智能合约承载的业务经常需要依赖于时间值，而一些区块变量如block.timestamp和block.number可以大致体现时间与时间增量。但是在很大程度上，使用它们并不安全。block.timestamp常被用作触发某些合约事件的变量，但是由于以太坊的性质，其存在一定的不准确性。以太坊的去中心化导致各个节点智能在一定程度上同步时间，并且矿工可以在一定范围内微调block.timestamp，特别是调整block.timestamp有利可图时。block.number同样也只能提供大致的时间情况。它是通过以太坊上挖出两个区块的时间差大致为14s来进行的估算。然而，挖抗间隔时间并不是恒定的，并且会因各种原因而改变。时间的精确计算也不应该依赖于block.number。",
        },
        {
          name: "Solidity",
          language: "差随机源",
          intro: "也被称为坏随机性、无秘密漏洞，部分包含时间戳依赖漏洞，SEC-120。智能合约业务中对随机数的需求非常大，尤其是许多带有赌博性质的合约。在以太坊中，随机性很难得到正确处理。Solidity提供的函数和变量可以访问看上去似乎是难以预测的值，如blockhash、block.difficulty，但它们都可以由矿工控制。block.timestamp也被经常用作随机数种子，但正如上一节所述，由于这些随机性的来源在一定程度上是可预测的并且可调整的。",
        },
        {
          name: "Solidity",
          language: "区块汽油费限制引起的拒绝服务",
          intro: "拒绝服务漏洞的一种形式，SWC-128。在2.1.2节中曾介绍过以太坊的汽油费机制，当部署智能合约或调用智能合约中的函数时，这些操作的执行总是需要一定数量的汽油费。以太坊网络规定了一个区块总汽油费的上限，即一个区块中包含的所有交易中的汽油费的总和不能超过该阈值。当超过这个阈值时，在集中式应用程序中无害的编程模式就会导致智能合约中拒绝服务漏洞。",
        },
        {
          name: "C++",
          language: "虚假EOS Transfer",
          intro: "由于eosio.token源代码完全公开的，所以任何人都能复制其源代码，并发布一个token（相同的名字、符号和代码），虚假的EOS和官方的唯一不同就是具有不同的发布人。或者直接调用漏洞合约的transfer函数进行转账。",
        },
        {
          name: "C++",
          language: "伪造Transfer通告",
          intro: "攻击者在 EOS 网络中控制两个账户 A 和 B，通过账户 A 向账户 B 发送真正的 EOS，eosio.token 合约在转账成功后会向 B 发送 notification。当账户 B 收到 notification后随即转发到受害者智能合约 C。",
        },
        {
          name: "C++",
          language: "区块信息依赖",
          intro: "在区块链平台上很难获得可靠的随机性来源。开发人员可能想使用区块信息(如tapos_block_prefix和tapos_block_num)来生成随机数。这些随机数可能被用来确定EOS的转移或彩票的中奖者。遗憾的是，tapos_block_prefix和tapos_block_num不是可靠的随机性来源，因为它们可以直接从ref_block_num计算出来，默认情况下ref_block_num是最后一个不可逆块的id。赌博合同可以使用延迟操作来确定彩票的赢家。在这种情况下，引用块是下注块之前的块。因此，当智能合约直接使用tapos_block_prefix和tapos_block_num进行随机数生成时，可以预测生成的随机数。",
        },
        {
          name: "Rust",
          language: "随机数依赖漏洞",
          intro: "共识是区块链平台的基础，一个区块链系统所依赖的共识协议往往是硬编码的，由此共识协议所构建的信任模型也是静态的。这就导致了区块链系统的正常运行需要依赖于确定性的准则。而智能合约中的不确定性会为区块链系统引入极大的安全风险。在长安链区块链平台中智能合约的执行不仅需要共识主节点的预执行，同样需要大量普通共识节点的执行与验证。如果智能合约中引入了不确定性，导致多个节点执行结果不一致，可能导致最终无法达成共识，智能合约调用无法真正完成。随机数的生成与使用是最常见的软件功能之一，开发者不仅可以利用随机数开发简单的应用程序，还可以利用随机数进行复杂的安全领域的软件开发。然而随机数在智能合约领域是需要极力避免的软件功能。随机数的使用会为智能合约引入极大的不确定性，不仅影响智能合约的正常执行，还影响共识的最终达成。",
        },
        {
          name: "Rust",
          language: "时间戳依赖漏洞",
          intro: "时间戳是指格林威治时间1970年01月01日00时00分00秒到当前时间的总秒数。时间戳在软件工程中经常使用，只要软件功能与现实时间有关系，均需借助时间戳来实现。然而在分布式区块链系统中，无法保证各个节点的机器时间是一致的，也无法保证各个节点同时执行获取时间戳的函数。因此使用时间戳来完成相应的业务逻辑会为系统引入极大的不确定性，影响智能合约的执行。"
    },{
          name: "Rust",
          language: "Map结构迭代漏洞",
          intro: "HashMap是一种键值型的存储结构，因其高效的查找更新效率而常被用于软件工程中。然而对于Rust语言而言，HashMap结构的迭代顺序并不是确定性的。同样数据的HashMap结构迭代的结果是不确定性的。如果HashMap迭代的不确定性影响了后续业务逻辑的执行，那么可能影响智能合约的执行，影响共识的最终一致。"
    },{
          name: "Rust",
          language: "整数溢出错误",
          intro: "整数溢出是常见的程序错误，当算数运算的结果超过当前数据类型的最大值或者最小值时，将会发生上溢或者下溢。对于一个无符号8位int类型的数而言，其数值范围在0到127之间，如果智能合约中的算术计算结果超过了这个范围，则会发生溢出。一般而言，一个算数计算的结果存在两种溢出的情况。若结果上溢，则其值会变为一个较小的值；若结果下溢，则其结果会变为一个较大的值。"
    },{
          name: "Rust",
          language: "除0错误",
          intro: "在数学领域零无法作为除数出现于除法运算中，同样的，当算数表达式中出现除零或者模零等操作时，程序无法正常执行，会导致程序执行崩溃。Rust的编译检查可以有效的检测出已知数据的算数表达式是否存在除零问题。但是编译检查属于静态检查，对于从链上读取的数据是无法进行预测的，如果智能合约中隐藏着除零漏洞，可能导致智能合约执行失败。"
    },{
          name: "Rust",
          language: "未处理错误漏洞",
          intro: "在长安链中，智能合约可以调用另一个智能合约。长安链不止支持同类型虚拟机内的跨合约调用，也支持不同类型虚拟机间的跨合约调用。然而如果被调用的智能合约出现了异常，那么虚拟机将终止被调用的智能合约的执行工作，区块链系统会回滚其状态并返回错误值。调用者合约如果没有对返回值进行检查以验证该调用是否成功执行，则可能导致执行意外的业务逻辑，导致严重的损失。"
    },{
          name: "Golang",
          language: "全局变量依赖",
          intro: "不仅在链码开发中，在一般的开发中，开发人员都需要考虑全局变量。全局变量可以天生地改变。因此，使用全局变量可能会导致链代码的不确定性。"
    },{
          name: "Golang",
          language: "映射结构迭代",
          intro: "由于Go的规范，开发人员在使用map结构进行迭代时，键值的顺序不是唯一的。因此，使用map结构迭代可能会造成不确定性。与随机数生成和时间戳不同，Go的行为具有隐藏实现细节的特点。"
    },{
          name: "Golang",
          language: "随机数生成",
          intro: "随机数生成是一类典型的不确定代码。在背书阶段，背书节点独立模拟链码，如第三节所述。因此，认可节点的模拟结果可能不一致。"
    },{
          name: "Golang",
          language: "调用外部API",
          intro: "通过调用应用程序编程接口(Application Programming Interface, API)来复用第三方开发的功能是一种常见的方法。此外，微服务，即通过消息[10]进行交互的内聚的、独立的流程，是最近出现的一种趋势。然而，在区块链环境中，开发人员在使用web服务时需要特别注意。如果服务向每一端返回不同的结果，则会导致分类账不一致。"
    }],
    };
  },
  methods:{
    objectSpanMethod({ row, column, rowIndex, columnIndex }) {
  if (columnIndex === 0) {  //定位到维度列
    // 获取当前单元格的值
    const currentValue = row[column.property];
    // 获取上一行相同列的值
    const preRow = this.tableData[rowIndex - 1];
    const preValue = preRow ? preRow[column.property] : null;
    // 如果当前值和上一行的值相同，则将当前单元格隐藏
    if (currentValue === preValue) {
      return { rowspan: 0, colspan: 0 };
    } else {
      // 否则计算当前单元格应该跨越多少行
      let rowspan = 1;
      for (let i = rowIndex + 1; i < this.tableData.length; i++) {
        const nextRow = this.tableData[i];
        const nextValue = nextRow[column.property];
        if (nextValue === currentValue) {
          rowspan++;
        } else {
          break;
        }
      }
      return { rowspan, colspan: 1 };
    }
  }
  }
  }
};
</script>

<style scoped>
.table-title {
  font-size: 20px;
  margin-bottom: 20px;
  font-weight: 600;
  text-align: center;

}

.el-table .el-table__row:first-child {
  background-color: #f0dbdb;  /* Adjust color as needed */
}
</style>
