<template>
  <br>
  <div class="container">
    <div class="top">合约检测</div>
       <ol class="rounded-list">
        <li><a href="">上传合约</a></li>      
    <!-- 第一个卡片 -->
    <div class="card1 card">
      <div class="content">
         <el-input
          v-model="contract_url"
          autocomplete="off"
          style="margin-right: 10px"></el-input>
        <el-upload
          :file-list="fileList"
          class="upload-demo"
          :action="$http.server_host + '/toolFunc/contracts/upload'"
          :headers="{ Authorization: 'Bearer ' + $auth.token }"
          multiple
          :on-preview="handlePreview"
          :on-remove="handleRemove"
          :before-remove="beforeRemove"
          :limit="3"
          :on-exceed="handleExceed"
          :on-success="handleSuccess"
          :on-error="handleError">
          <el-button class="mybutton1" type="primary"
            >上传合约<el-icon class="el-icon--right"><Upload /></el-icon
          ></el-button>
          <div class="el-upload__tip">
            contract files with a size less than 500KB.
          </div>
          <br />
        </el-upload>
      </div>
    </div>
    <hr>
    <br>
        <li><a href="">选择工具</a></li>
    <!-- 第二个卡片 -->
    <div class="card1 card">
      <div class="content">
        <el-select
          v-model="selectedOption"
          :options="options"
          placeholder="工具">
          <el-option
            v-for="item in options"
            :key="item.value"
            :label="item.label"
            :value="item.value" />
        </el-select>
        <el-select
          v-model="contract_name"
          :options="options"
          placeholder="合约">
          <el-option
            v-for="item in contract_list"
            :key="item"
            :label="item"
            :value="item" />
        </el-select>
        <el-button class="mybutton2" type="success" @click="handleButtonClick"
          >开始检测<el-icon><Share /></el-icon
        ></el-button>
      </div>
    </div>
    <br>
    <hr>
    <br>
    <li><a href="">检测结果</a></li>
    </ol>
   
    <!-- 第三个卡片 -->
    <div class="card2 card">
      <div class="content">
        <div class="description-container">
          <el-descriptions
            class="margin-top"
            :column="3"
            :size="size"
            :contentStyle="rowCenter"
            :labelStyle="rowCenter"
            border>
            <el-descriptions-item label="工具名称" width="10%">
              {{ selectedOption }}
            </el-descriptions-item>
            <el-descriptions-item label="是否成功" width="10%">
              {{ message }}</el-descriptions-item
            >
            <el-descriptions-item label="所用时间" width="10%">
              {{ execution_time }}
            </el-descriptions-item>
          </el-descriptions>
          <result-component :detect_res="detect_res"></result-component>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { ElMessage, ElMessageBox } from "element-plus";
import { Upload, Share } from "@element-plus/icons";
import ResultComponent from "./ResultComponent.vue";

export default {
  name: "AppSCTool",
  components: {
    Upload,
    Share,
    ResultComponent,
  },
  data() {
    return {
      fileList: [],
      currentPage: 1,
      uploadError: "",
      contract_url: "",
      selectedOption: "", // Add this li
      options: [
        {
          value: "mythril",
          label: "All",
        },
        {
          value: "oyente",
          label: "Oyente",
        },
        {
          value: "conkas",
          label: "Conkas",
        },
        {
          value: "slither",
          label: "Slither",
        },
        {
          value: "solhint",
          label: "solhint",
        },
        {
          value: "confuzzius",
          label: "confuzzius",
        },
        {
          value: "security",
          label: "security",
        },
        {
          value: "osiris",
          label: "osiris",
        },
        {
          value: "honeybadger",
          label: "honeybadger",
        },
        {
          value: "wana_cpp",
          label: "wana_cpp",
        },
        {
          value: "wana_rust",
          label: "wana_rust",
        },
        {
          value: "evulhunter",
          label: "evulhunter",
        },
      ],
      message: "",
      detect_res: "",
      contract_name: "",
      contracts_files: [],
      contract_list: [],
      execution_time: "",
    };
  },
  rowCenter: {
    "text-align": "center",
  },
  computed: {
    paginatedFiles() {
      const start = (this.currentPage - 1) * 5;
      const end = this.currentPage * 5;
      return this.contract_list.slice(start, end);
    },
  },
  mounted() {
    this.fetchContractList(); // Call the method when component is mounted
  },
  methods: {
    handleRemove(file) {
      const index = this.fileList.indexOf(file);
      if (index !== -1) {
        this.fileList.splice(index, 1);
      }
    },

    handlePreview(uploadFile) {
      console.log(uploadFile);
    },

    handleExceed(files) {
      ElMessage.warning(
        `The limit is 3, you selected ${files.length} files this time, add up to ${files.length} totally`
      );
    },

    beforeRemove(uploadFile) {
      return ElMessageBox.confirm(
        `Cancel the transfer of ${uploadFile.name} ?`
      ).then(
        () => true,
        () => false
      );
    },
    handleSuccess(response, file) {
      if (response["code"] == 200) {
        var file_name = response["data"]["contract_url"];
        this.contract_url = "/media/contracts/" + file_name;
        this.fileList.push({ name: file.name });
      } else {
        // Don't add to fileList
        ElMessage.error(response["message"]);
      }
    },
    handleError(err) {
      ElMessage.error(err.message);
    },
    handlePageChange(newPage) {
      this.currentPage = newPage;
    },
    handleButtonClick() {
      if (this.selectedOption) {
        console.log("You selected:", this.selectedOption);
        this.$http
          .getToolAnalysis(this.selectedOption, this.contract_name)
          .then((res) => {
            this.message = res["message"];
            if ("logs" in res) {
              this.detect_res = res["logs"];
            } else if ("output" in res) {
              this.detect_res = res["output"];
            }
            this.execution_time = res["time"];
          });
        // Perform your action here
      } else {
        console.log("No option selected.");
      }
    },
    fetchContractList() {
      this.$http
        .getContractList()
        .then((response) => {
          this.contracts_files = response.files; // Extract the 'files' array from the response
          this.contract_list = this.contracts_files.map((file) => file.name);
        })
        .catch((error) => {
          console.error("Failed to fetch contract list:", error);
        });
    },
    deleteContract(contract) {
      console.log("Delete button clicked for contract:", contract);
      this.$http
        .getContractDelete(contract)
        .then((response) => {
          // Remove the deleted file from paginatedFiles
          const index = this.paginatedFiles.indexOf(contract);
          console.log(response);
          if (index !== -1) {
            this.paginatedFiles.splice(index, 1);
          }
          // Handle any additional success logic here
        })
        .catch((error) => {
          // Handle the error here
          console.error("Failed to delete contract:", error);
        });
    },
  },
};
</script>

<style scoped>
ol{
        counter-reset: li; /* 创建一个计数器 */
        list-style: true; /* 清除列表默认的编码*/
        *list-style: decimal; /* 让IE6/7具有默认的编码 */
        font: 15px 'trebuchet MS', 'lucida sans';
        padding: 0;
        margin-bottom: 4em;
        text-shadow: 0 1px 0 rgba(255,255,255,.5);
        margin-left: -200px;
			}
.rounded-list a {
      width:90px;
			position: relative;
			display: block;
			padding: 0.4em 0.4em 0.4em 2em;
			*padding: 0.4em;/*for ie6/7*/
			margin: 0.5em 0;
			background: #fff;
			color: #444;
			text-decoration: none;
			/*CSS3属性*/
			border-radius: 0.3em;/*制作圆角*/
			/* transition动画效果*/
			-moz-transition: all 0.3s ease-out;
			-webkit-transition: all 0.3s ease-out;
			-o-transition: all 0.3s ease-out;
			-ms-transition: all 0.3s ease-out;
			transition: all 0.3s ease-out;
      
		}
		.rounded-list a:hover {
			background: #eee;
		}
		.rounded-list a:hover::before {
			/*悬停时旋转编码*/
			-moz-transform: rotate(360deg);
			-webkit-transform: rotate(360deg);
			-o-transform: rotate(360deg);
			-ms-transform: rotate(360deg);
			transform: rotate(360deg);
		}
		.rounded-list a::before {
			
			content: counter(li);
			counter-increment: li;
			
			position: absolute;
			left: -1.3em;
			top: 50%;
			margin-top: -1.3em;
			background: #8fbc8f;
			height: 2em;
			width: 2em;
			line-height: 2em;
			border: 0.3em solid #fff;
			text-align: center;
			font-weight: bold;
			border-radius: 2em;
			-webkit-transition: all 0.3s ease-out;
			-moz-transition: all 0.3s ease-out;
			-ms-transition: all 0.3s ease-out;
			-o-transition: all 0.3s ease-out;
			transition: all 0.3s ease-out;
		}
.el-space {
  display: block;
}
.aaaaa {
  margin-left: -350px;
}
.file-list-container {
  width: 300px;
  height: auto;
  overflow: auto;
  margin-left: -11500px;
  text-align: left;
}

.description-container {
  max-width: 100%;
  overflow-x: auto;
}

::v-deep .el-descriptions-item-content {
  white-space: nowrap; /* Keep text on a single line */
  overflow-x: auto; /* Add scroll bar if necessary */
}

::v-deep .el-descriptions-title {
  text-align: center;
}
.center {
  text-align: center;
  margin-left: 290px;
}

h4 {
  text-align: center;
}
h1 {
  text-align: center;
}
hr {
  display: block;
  height: 0.5px;
  background: transparent;
  width: 100%;
  border: none;
  border-top: solid 0.5px #f0f0f0;
}
el-descriptions {
  text-align: center;
}
.select-button-container {
  text-align: center;
}

.load {
  text-align: center;
}
.el-upload__tip {
  text-align: center;
}
.file-list-container {
  text-align: center;
}
.description-container {
  text-align: center;
}
.el-descriptions_title {
  text-align: center;
}

.el-descriptions {
  width: 800px;
}

.el-input {
  width: 220px;
}
.mybutton1 {
  margin-left: -20px;
  background-color: #8fbc8f;
}
.mybutton1:hover {
    
    transition:0.7s;
    filter: brightness(1.25);

}

.mybutton2 {
  background-color: #8fbc8f;
}
.mybutton2:hover {
    
    transition:0.7s;
    filter: brightness(1.25);

}
.card .content {
  display: flex;
  justify-content: center;
  gap: 30px;
}
.card h3 {
  font-size: 1.8em;
  z-index: 1;
}
.container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  max-width: 1000px;
  flex-wrap: wrap;
  z-index: 1;
  border: 1px solid #ccc;
  background: #f9f9fb;
  border-radius: 3%;
  overflow: hidden;
  margin: 0 auto;
}
.top {
  height: 60px;
  background: #419f60;
  color: #fff;
  font-size: 20px;
  line-height: 60px;
  padding: 0px 20px;
  box-sizing: border-box;
}

.container > div {
  width: 100% !important;
}
.container .card1 {
  position: relative;
  margin: 30px;
  /* box-shadow: 20px 20px 50px rgba(0, 0, 0, 0.5); */
  border-radius: 15px;
  /* background: rgba(255, 255, 255, 0.1); */
  overflow: hidden;
  /* display: flex; */
  justify-content: center;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  border-left: 1px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(5px);
  margin-top:-5px;
}
.container .card1 .content {
  padding: 20px;
  text-align: center;
  transform: translateY(100px);
  opacity: 0;
  transition: 0.5s;
}
.container .card1 .content {
  transform: translateY(0px);
  opacity: 1;
}
.container .card1 .content h2 {
  position: absolute;
  top: -60px;
  right: 1px;
  font-size: 10em;
  color: rgba(255, 255, 255, 0.05);
  pointer-events: none;
}
.container .card1 .content h3 {
  font-size: 1.8em;
  color: #black;
  z-index: 1;
}
.container .card1 .content p {
  font-size: 1em;
  color: #black;
  font-weight: 300;
}
.container .card1 .content a {
  position: relative;
  display: inline-block;
  padding: 8px 20px;
  margin-top: 15px;
  background: #black;
  color: #000;
  border-radius: 20px;
  text-decoration: none;
  font-weight: 500;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}
.container .card2 {
  position: relative;
  /* width: 1030px; */
  /* height: 750px; */
  margin: 30px;
  /* box-shadow: 20px 20px 50px rgba(0, 0, 0, 0.5); */
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
  /* display: flex; */
  justify-content: center;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  border-left: 1px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(5px);
  margin-top:-65px;
}
.container .card2 .content {
  padding: 20px;
  text-align: center;
  transform: translateY(100px);
  opacity: 0;
  transition: 0.5s;
}
.container .card2 .content {
  transform: translateY(0px);
  opacity: 1;
}
.container .card2 .content h2 {
  position: absolute;
  top: -60px;
  right: 1px;
  font-size: 10em;
  color: rgba(255, 255, 255, 0.05);
  pointer-events: none;
}
.container .card2 .content h3 {
  font-size: 1.8em;
  color: #black;
  z-index: 1;
}
.container .card2 .content p {
  font-size: 1em;
  color: #black;
  font-weight: 300;
}
.container .card2 .content a {
  position: relative;
  display: inline-block;
  padding: 8px 20px;
  margin-top: 15px;
  background: #black;
  color: #000;
  border-radius: 20px;
  text-decoration: none;
  font-weight: 500;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}
.el-space {
  display: block;
}

.file-list-container {
  width: 300px;
  height: auto;
  overflow: auto;
  margin-left: 500px;
  text-align: left;
}
.file {
  text-align: left;
}
.description-container {
  max-width: 100%;
  overflow-x: auto;
}

::v-deep .el-descriptions-item-content {
  white-space: nowrap; /* Keep text on a single line */
  overflow-x: auto; /* Add scroll bar if necessary */
}

::v-deep .el-descriptions-title {
  text-align: center;
}
.center {
  text-align: center;
  margin-left: 290px;
}

h4 {
  text-align: center;
}
h1 {
  text-align: center;
}
hr {
  display: block;
  height: 0.5px;
  background: transparent;
  width: 100%;
  border: none;
  border-top: solid 0.5px #f0f0f0;
}
el-descriptions {
  text-align: center;
}
.select-button-container {
  text-align: center;
}

.load {
  text-align: center;
}
.el-upload__tip {
  text-align: center;
}
.file-list-container {
  text-align: center;
}
.description-container {
  text-align: center;
}
.el-descriptions_title {
  text-align: center;
}

</style>
