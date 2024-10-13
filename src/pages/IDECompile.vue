<template>
  <div>
    <p class="line">使用IDE编写你的合约吧！</p>
    <br>
    <button class="button" @click="toggleSwitch">启动remix ide</button>
    <br>
    <toggle-button v-model="value"  :sync="true" :labels="true" @change="toggleSwitch"/>
  </div>
  <br />
  <div class="iframe-container">
    <iframe :src="remixSrc" frameborder="0" class="responsive-iframe"></iframe>
  </div>
</template>

<script>
import ToggleButton  from "@vueform/toggle";

export default {
  name: "AppIde",
  components: {
    ToggleButton,
  },
  data: () => ({
    remixSrc: "http://" + window.location.hostname + ":3000/",
    value: false,
    isUserInitiated: false,
  }),
  mounted() {
    this.getIdeState(); 
  },
  watch: {
    value(newValue) {
        if (this.isUserInitiated) {
        if (newValue === true) {
          this.getIdeStart(); // Call getIdeStart when the switch is turned on
        } else {
          this.getIdeStop(); // Call getIdeStop when the switch is turned off
        }
      }
      this.isUserInitiated = false; // Reset the flag after handling the change
    }
  },
  methods: {
    toggleSwitch(newValue) {
      this.isUserInitiated = true; // Set the flag when the user toggles the switch
      this.value = newValue;
    },
    getIdeStart() {
      this.$http.getRemixIDEStart().then((response) => {
        // Handle the response or perform additional actions
        if(response.message=="successfully"){
            console.log("docker start")
        }
      });
    },
    getIdeState() {
      this.$http.getRemixIDEState().then((response) => {
        // Handle the response or perform additional actions
        console.log(response)
        if(response.status=="Running"){
            this.value = true
            console.log("docker running")
        }else{
            this.value = false
            console.log("docker not running")
        }
      });
    },
    getIdeStop() {
      this.$http.getRemixIDEStop().then((response) => {
        if(response.message=="successfully"){
            console.log("docker stop")
        }
      });
    },
    }
};
</script>

<style src="@vueform/toggle/themes/default.css"></style>
<style scoped>


.iframe-container {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* Adjust this to change the aspect ratio */
  height: 0;
}

.responsive-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.line {
    border-right: 2px solid #000;
    border-right: .15em solid green;
    font-size: 200%; /* 字体大小 */
    text-align: center; /* 文字横向居中 */
    white-space: nowrap; /* 文字不换行 */
    overflow: hidden; /* 多余的文字内容隐藏 */
    animation: borders 0.7s infinite normal,
    widths 2s steps(13); /* 重点 steps() */
}
   /* 边框闪烁动画 模拟指针闪烁 */
@keyframes broders {
    from {border-right-color:red;}
    to {border-right-color: #fff;}
}
/* 容器宽的改变动画 */
@keyframes widths {
    from {width: 0;}
    to {width: 40%;} /* 也可以是固定宽 */
}
.button {
  padding: 15px 25px;
  font-size: 24px;
  text-align: center;
  cursor: pointer;
  outline: none;
  color: #fff;
  background-color: #4CAF50;
  border: none;
  border-radius: 15px;
  box-shadow: 0 9px #999;
  margin-left:520px;
}

.button:hover {background-color: #3e8e41}

.button:active {
  background-color: #3e8e41;
  box-shadow: 0 5px #666;
  transform: translateY(4px);
}


 

</style>
