<template>
  <div>
    <el-space direction="vertical" :size="20">
      <h1>评论管理</h1>
      <el-table :data="comments" style="width: 100%">
        <el-table-column prop="content" label="内容" />
        <el-table-column prop="author.username" label="作者" />
        <el-table-column label="帖子">
          <template #default="scope">
            <a :href="$http.server_host + '/post/detail/' + scope.row.post.id" target="_blank">{{ scope.row.post.title }}</a>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="发布时间" width="180" />
        <el-table-column label="操作">
          <template #default="scope">
            <el-button
              type="danger"
              circle
              size="mini"
              @click="onDeleteCommentClick(scope.$index)"
            >
              <el-icon><delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-space>

    <!-- 删除轮播图确认对话框 -->
    <el-dialog v-model="confirmDialogVisible" title="提示" width="30%">
      <span>您确定要删除这个评论吗？</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="confirmDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="onConfirmDeleteCommentClick"
            >确定</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus';
import {Delete} from "@element-plus/icons";
export default {
  name: "AppComment",
  data() {
    return {
      deletingIndex: 0,
      confirmDialogVisible: false,
      comments: [],
    };
  },
  mounted(){
    this.$http.getCommentList().then(res => {
      this.comments = res['data'];
    })
  },
  methods: {
    onDeleteCommentClick(index) {
      this.deletingIndex = index;
      this.confirmDialogVisible = true;
    },
    onConfirmDeleteCommentClick(){
      let comment = this.comments[this.deletingIndex];
      this.$http.deleteComment(comment.id).then(res => {
        if(res && res['code'] == 200){
          ElMessage.success("评论删除成功！");
          this.confirmDialogVisible = false;
          this.comments.splice(this.deletingIndex, 1);
        }else{
          ElMessage.info(res['message']);
        }
      });
    }
  },
  components: {
    Delete
  }
};
</script>

<style scoped>
.el-space {
  display: block;
}
</style>
