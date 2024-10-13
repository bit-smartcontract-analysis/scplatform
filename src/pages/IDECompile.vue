<template>
  <div>
    <h5>启动remix ide</h5>
    <toggle-button v-model="value" color="#82C7EB" :sync="true" :labels="true" @change="toggleSwitch"/>
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
</style>
