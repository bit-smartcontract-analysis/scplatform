<template>
  <div>
    <el-space direction="vertical" :size="20">
      <h1>用户管理</h1>
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="join_time" label="加入时间" />
        <el-table-column label="员工">
          <template #default="scope">
            <el-tag v-if="scope.row.is_staff">是</el-tag>
            <el-tag v-else type="danger">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template #default="scope">
            <el-tag v-if="scope.row.is_active" type="success">是</el-tag>
            <el-tag v-else type="danger">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button
              type="danger"
              circle
              size="mini"
              @click="onActiveUserClick(scope.$index)"
            >
              <el-icon><delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-space>

    <!-- 删除用户确认对话框 -->
  <el-dialog
    v-model="confirmDialogVisible"
    title="提示"
    width="30%"
  >
    <span>{{message}}</span>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="confirmDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="onConfirmActiveUserClick">确定</el-button>
      </span>
    </template>
  </el-dialog>
  </div>
</template>

<script>
import {Delete} from "@element-plus/icons";
import { ElMessage } from 'element-plus';
export default {
    name: "AppUser",
    data(){
      return {
        confirmDialogVisible: false,
        users: [],
        activingIndex: 0,
        message: ""
      }
    },
    mounted(){
      this.getUserList(1);
    },
    methods: {
      getUserList(page){
        this.$http.getUserList(page).then(res => {
          this.users = res.data;
        });
      },
      onActiveUserClick(index){
        this.activingIndex = index;
        this.confirmDialogVisible = true;
        const user = this.users[index];
        if(user.is_active){
          this.message = "您确定要拉黑此用户吗？"
        }else{
          this.message = "您确定要取消拉黑此用户吗？"
        }
      },
      onConfirmActiveUserClick(){
        let user = this.users[this.activingIndex];
        let is_active = user.is_active?0:1;
        this.$http.activeUser(user.id, is_active).then(res => {
          if(res && res['code'] == 200){
            ElMessage.success("操作成功！");
            this.confirmDialogVisible = false;
            let user = res.data;
            this.users.splice(this.activingIndex, 1, user);
          }else{
            ElMessage.info("操作失败！");
            this.confirmDialogVisible = false;
          }
        })
      }
    },
    components: {
      Delete
    }
}
</script>

<style scoped>
.el-space {
  display: block;
}
</style>