<template>
    <div class="container">
      <h1>长安链漏洞检测平台</h1>
      <img src="@/assets/constructure.jpg" alt="Platform Image" class="platform-image"/>
      <div class="section">
        <h2>核心组件</h2>
        <p>整个长安链漏洞检测平台由四大核心组件组成：前端界面，后端服务器，分析工具，安全和隐私模块。</p>
      </div>
      <div class="section">
        <h2>前端界面</h2>
        <p>前端界面主要为用户提供与系统交互的平台。首先，它包括一个用户认证模块，使用户能够注册、登录并进行双因素身份验证，确保账户的安全。为了方便用户提交智能合约代码，设计了合约上传模块，允许用户上传文件或直接在在线文本编辑器中编写。一旦分析完成，结果将在结果显示模块中呈现，包括概览和详细报告，使用户能过快速了解潜在的问题和建议。此外，用户历史查询模块允许用户查看和回顾他们过去上传的合约和分析结果。</p>
      </div>
      <div class="section">
        <h2>后端服务器</h2>
        <p>后端服务器是系统核心，处理所有的数据和请求。它包括多个API终端，用于处理用户认证、合约上传、分析和历史数据查询。为了有效存储用户信息、合约和分析结果，系统设置了专门的数据存储区域。另外，分析任务调度器确保系统能够高效地处理大量的分析请求，根据系统的资源和任务的优先级来调度。</p>
      </div>
      <div class="section">
        <h2>分析工具部分</h2>
        <p>分析工具部分是系统的核心，它负责对上传的智能合约进行深入的检查。对于Solidity合约，我们使用了Oyente，Mythril, Slither, conkas，Osiris。对于C/C++合约，我们选择了wana作为分析工具，并考虑使用自定义工具进行动态分析。对于Rust合约，我们选择了EvlHunter。对于Golang合约，我们选择了chaincode-analyzer, revive-cc。对于以上合约语言，我们将根据其特性选择或开发合适的分析工具。</p>
      </div>
      <div class="section"> 
        <p>最后，安全隐私部分也很重要。所有传输和存储的数据都将被加密，确保他们不会被未经授权的第三方访问。此外，我们计划定期对系统进行安全审计，确保没有潜在的安全漏洞。</p>
        </div>
    </div>
</template>

<script>
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

.platform-image {
  display: block;
  max-width: 80%;
  height: auto;
  margin: 0 auto 20px;
}
.section {
  margin-bottom: 20px;
}

h1 {
  color: #333;
  text-align: center;
  margin-bottom: 30px;
  font-size: 30px;
}

h2 {
  color: #555;
  font-size: 18px;
}

p {
  line-height: 1.6;
  color: #666;
}
</style>