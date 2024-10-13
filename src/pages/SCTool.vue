<template>
  <div>
    <el-space direction="vertical" :size="20" style="width: 100%">
      <h1>安全工具检测</h1>
      <h4>step1 上传合约</h4>
      <el-input
        v-model="contract_url"
        autocomplete="off"
        style="margin-right: 10px"
      ></el-input>
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
        :on-error="handleError"
      >
      <div class="center">
        <el-button class="center" type="primary" 
          >上传合约<el-icon class="el-icon--right"><Upload /></el-icon
        ></el-button>
      </div>
       
        <template #tip>
          <div class="el-upload__tip">
            contract files with a size less than 500KB.
          </div>
        </template>
     
      </el-upload>
      <div class="file-list-container">
        <div class="file" v-for="file in paginatedFiles" :key="file.name">
          {{ file }}
        </div>

      </div>
      
      <el-pagination
        :page-size="5"
        layout="prev, pager, next"
        :total="contract_list.length"
        @current-change="handlePageChange"
      ></el-pagination>
    
    </el-space>
    <br>
    <hr>
    <br>
    <br>
    <h4>step2 选择合约所用工具</h4>
    <br>
    <div class="select-button-container">
      <el-select v-model="selectedOption" :options="options" placeholder="工具">
        <el-option
          v-for="item in options"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      <el-select v-model="contract_name" :options="options" placeholder="合约">
        <el-option
          v-for="item in contract_list"
          :key="item"
          :label="item"
          :value="item"
        />
      </el-select>
      <el-button type="success" @click="handleButtonClick"
        >开始检测<el-icon><Share /></el-icon
      ></el-button>
    </div>
  </div>
  <br>
  <br>
  <hr>
  <br>
  <br>
  <div class="description-container">
    <el-descriptions
      class="margin-top"
      title="检测结果"
      :column="3"
      :size="size"
      :contentStyle="rowCenter" 
      :labelStyle="rowCenter"
      border
    >
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
      selectedOption: null, // Add this li
      options: [
        {
          value: "mythril",
          label: "Mythril",
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
  rowCenter:{
                    "text-align":"center"
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
.el-space {
  display: block;
}

.file-list-container {
  width: 300px;
  height: auto;
  overflow: auto;
  margin-left:500px;
  text-align: left;
}
.file
{
  text-align:left;
}
.description-container {
  max-width: 100%;
  overflow-x: auto;
}

::v-deep .el-descriptions-item-content {
  white-space: nowrap; /* Keep text on a single line */
  overflow-x: auto; /* Add scroll bar if necessary */
}

::v-deep .el-descriptions-title
{
  text-align:center;
}
.center
{
  text-align:center;
  margin-left:290px;
}

h4{
  text-align:center
}
h1
{
  text-align:center
}
hr {
    display: block;
    height: 0.5px;
    background: transparent;
    width: 100%;
    border: none;
    border-top: solid 0.5px #f0f0f0;
}
el-descriptions
{
  text-align:center
}
.select-button-container
{
  text-align:center
}

.load{
  text-align:center
}
.el-upload__tip
{
  text-align:center
}
.file-list-container
{
  text-align:center
}
.description-container
{
  text-align:center
}
.el-descriptions_title
{
  text-align:center;
}


</style>
