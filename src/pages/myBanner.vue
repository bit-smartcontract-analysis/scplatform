
<template>
  <div>
    <h2 class="table-title">工具数据分析</h2>
    <el-table :data="tableData" border stripe row-style="rowStyleMethod">
      <el-table-column prop="name" label="工具名称" width="160" align="left">
      </el-table-column>
      <el-table-column prop="language" label="合约语言" width="120" align="left">
      </el-table-column>
      <el-table-column prop="bug" label="检测漏洞" width="120" align="left">
      </el-table-column>
      <el-table-column prop="intro" label="详情介绍" width="400" align="left">
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      tableData: [
        {
          name: "Mythril",
          language: "solidity",
          bug: "整数溢出、时间戳依赖、重入攻击等",
          intro:
            "Mythril是以太坊EVM字节码的安全分析工具。它使用符号执行、SMT方案来分析检测智能合约代码中的各种安全漏洞",
        },
        {
          name: "Oyente",
          language: "solidity",
          bug: "交易顺序依赖漏洞、时间戳依赖、异常障碍、重入漏洞",
          intro:
            "Oyente是一个智能合约自动审计工具，使用了一种基于符号执行的技术来检测合约中的漏洞",
        },
        {
          name: "Conkas",
          language: "solidity",
          bug: "*************",
          intro: "一种以太坊字节码的模块化和静态分析工具",
        },
        {
          name: "Slither",
          language: "solidity",
          bug: "重入漏洞、未初始化的存储变量、未使用的变量、不安全的委托调用、低级别调用等",
          intro: " Slither执行静态分析，它分析Solidity合约源代码以发现潜在的漏洞和问题",
        },
        {
          name: "Solhint",
          language: "solidity",
          bug: "不安全的数学操作、避免使用send方法、避免在合约构造函数中使用tx.origin等",
          intro: "Solhint执行静态代码分析，它会检查Solidity智能合约的源代码以发现潜在的编码错误、不规范的编程实践和安全问题",
        },
        {
          name: "confuzzius",
          language: "solidity",
          bug: "生成可能导致合约状态中可能隐藏错误的交易序列",
          intro: "一个具有数据依赖意识的以太坊智能合约混合模糊测试工具",
        },
        {
          name: "security",
          language: "solidity",
          bug: "*************",
          intro: "一个检测solidity智能合约漏洞的工具",
        },
        {
          name: "osiris",
          language: "solidity",
          bug: "重入漏洞、溢出漏洞、未初始化变量、函数可见性错误、Gas 空洞",
          intro: "Osiris 是一种智能合约安全工具，它是用于以太坊区块链上的 Solidity 智能合约的漏洞扫描器",
        },
        {
          name: "honeybadger",
          language: "solidity",
          bug: "*************",
          intro: "一个检测solidity智能合约漏洞的工具",
        },
        {
          name: "wana_cpp",
          language: "C++",
          bug: "块信息依赖漏洞、资产无限期冻结漏洞、委托调用漏洞、Block Information Dependency漏洞等",
          intro: "WANA是一款基于符号执行技术的智能合约漏洞检测工具，可以探索智能合约的程序执行分支，并在探索过程中寻找智能合约是否存在安全漏洞",
        },
        {
          name: "wana_rust",
          language: "Rust",
          bug: "块信息依赖漏洞、资产无限期冻结漏洞、委托调用漏洞、Block Information Dependency漏洞等",
          intro: "WANA是一款基于符号执行技术的智能合约漏洞检测工具，可以探索智能合约的程序执行分支，并在探索过程中寻找智能合约是否存在安全漏洞",
        },
        {
          name: "evulhunter",
          language: "Rust",
          bug: "Fake EOS Transfer漏洞",
          intro: "EVulHunter是基于Octopus项目的EOS智能合约二进制级漏洞检测器",
        },
        {
          name: "chaincode-analyzer",
          language: "Golang",
          bug: "Random value, Timestamp, Calling external API, Pointer",
          intro: "chaincode-analyzer是专门用于Fabric chaincode合约的漏洞检测。经过测试，也可以测试长安链go合约",
        },
      ],
    };
  },
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
