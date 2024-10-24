<template>
  <div class="container">
    <div class="file-list" v-for="file in contract_list" :key="file.name">
      <div class="file-info">
        <span class="file-name">{{ file.name }}</span>
        <span class="file-size">{{ file.size }} bytes</span>
      </div>
      <div class="file-actions">
        <el-button type="primary" circle @click="editContract(file.name)"
          ><el-icon><edit /></el-icon>
        </el-button>
        <el-button type="danger" circle @click="deleteContract(file.name)"
          ><el-icon><delete /></el-icon>
        </el-button>
      </div>
    </div>
  </div>

</template>

<script>
import { Delete, Edit } from "@element-plus/icons";
export default {
  name: "AppContractManage",
  components: {
    Delete,
    Edit,
  },
  data() {
    return {
      contract_list: [],
    };
  },
  mounted() {
    this.fetchContractList();
  },
  methods: {
    fetchContractList() {
      this.$http
        .getContractList()
        .then((response) => {
          this.contract_list = response.files; // Extract the 'files' array from the response
        })
        .catch((error) => {
          console.error("Failed to fetch contract list:", error);
        });
    },
    editContract(fileName) {
      console.log('editContract called with fileName:', fileName); 
      this.currentFileName = fileName;
      // You'll need to fetch the file content here
      this.currentFileContent = "The content of the file..."; // Replace with actual content
      this.editorVisible = true;
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

.editor-textarea {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 10px;
  box-sizing: border-box;
  font-family: monospace; /* Gives it a bit of a code editor feel */
}
</style>