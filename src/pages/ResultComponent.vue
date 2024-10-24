<style>
div {
  white-space: pre-line;
}
</style>
<template>
    <div class="result-container">
      <br>
      <p class="line">检测日志结果：</p>
      <p>{{ detect_res }}</p>
    </div>
  </template>
  <script>
  export default {
    props: ['detect_res'],
  };
  </script>
  <style scoped>
.result-container {
  /* Add your styles here */
}
.result-content {
  max-width: 100%;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.line {
  border-right: 2px solid #000;
  border-right: 0.15em solid green;
  font-size: 120%; /* 字体大小 */
  text-align: center; /* 文字横向居中 */
  white-space: nowrap; /* 文字不换行 */
  overflow: hidden; /* 多余的文字内容隐藏 */
  animation: borders 0.1s infinite normal, widths 2s steps(13); /* 重点 steps() */
}
/* 边框闪烁动画 模拟指针闪烁 */
@keyframes broders {
  from {
    border-right-color: red;
  }
  to {
    border-right-color: #fff;
  }
}
/* 容器宽的改变动画 */
@keyframes widths {
  from {
    width: 0;
  }
  to {
    width: 40%;
  } /* 也可以是固定宽 */
}
</style>