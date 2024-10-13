<template>
    <div class="result-container">
      <h4>检测日志:</h4>
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
  </style>