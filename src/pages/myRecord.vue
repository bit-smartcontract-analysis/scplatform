<template>
  <div>
    <select v-model="selectedLanguage">
      <option value="sol">Solidity</option>
      <option value="javascript">JavaScript</option>
      <option value="python">Python</option>
      <option value="html">HTML</option>
      <!-- Add more languages as needed -->
    </select>
    <select v-model="themeColor">
      <option value="vs-dark">Dark</option>
      <option value="vs-light">Light</option>
      <option value="hc-black">Black</option>
    </select>
    <div style="margin: 10px 0"></div>
    <MonacoEditor
    class="editor"
    :language="selectedLanguage"
    :theme="themeColor"
    :options="editorOptions"
    v-model="code"
    @editorDidMount="editorDidMount"
    ></MonacoEditor>
    <div style="margin: 10px 0"></div>
    <el-button type="primary" circle @click="handleSubmit"><el-icon><UploadFilled /></el-icon>
    </el-button>Submit Code 
  </div>
  <div class="container">
    <div class="file-list" v-for="file in contract_list" :key="file.name">
      <div class="file-info">
        <span class="file-name">{{ file.name }}</span>
        <span class="file-size">{{ file.size }} bytes</span>
      </div>
      <div class="file-actions">
        <el-button type="success" circle @click="checkContract(file.name)">
          <el-icon><search /></el-icon>
        </el-button>
        <el-button type="danger" circle @click="deleteContract(file.name)"
          ><el-icon><delete /></el-icon>
        </el-button>
      </div>
    </div>
  </div>
</template>
UploadFilled

<script>
import { Delete, Search, UploadFilled} from "@element-plus/icons";
import MonacoEditor from "vue-monaco";
import {h} from "vue";
MonacoEditor.render = () => h("div");

export default {
  name: "AppRecord",
  components: {
    Delete,
    Search,
    UploadFilled,
    MonacoEditor
  },
  data() {
    return {
      contract_list: [],
      code: '//write your code here',
      selectedLanguage: 'sol',
      themeColor: 'vs-dark',
    };
  },
  mounted() {
    this.fetchContractList();
  },
  methods: {
    fetchContractList() {
      this.$http
        .getLogsList()
        .then((response) => {
          this.contract_list = response.files; // Extract the 'files' array from the response
        })
        .catch((error) => {
          console.error("Failed to fetch contract list:", error);
        });
    },
    deleteContract(contract) {
      console.log(contract);
      this.$http
        .getContractDelete(contract)
        .then((response) => {
          console.log(response);
          // After successful deletion, fetch the updated list
          this.fetchContractList();
        })
        .catch((error) => {
          // Handle the error here
          console.error("Failed to delete contract:", error);
        });
    },
    checkContract(fileName) {
      // Your check logic here
      console.log(`Checked contract: ${fileName}`);
    },
    editorDidMount(editor) {
      // Listen to `scroll` event
      editor.onDidScrollChange(e => {
        console.log(e)
      })
    },
    handleSubmit() {
      // Here, 'this.code' contains the current value from the editor
      console.log('Submitted code:', this.code);
      // Call your function here and pass 'this.code'
    }
  },
};
</script>

<style scoped>
.container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.file-list {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  margin-bottom: 10px;
}

.file-info {
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 16px;
  font-weight: bold;
}

.file-size {
  font-size: 14px;
  color: #666;
}

.file-actions {
  display: flex;
  align-items: center;
}
.editor{
  height: 500px;
  border: 1px solid black;
}
</style>