<template>
  <div class="frame">
    <el-container class="frame-container">
      <el-header class="header">
        <a href="/" class="brand"><strong>长安链</strong>合约检测平台</a>
        <div class="header-content">
          <!-- <div class="greet">欢迎，{{$auth.user.username}}[{{$auth.user.role.name}}]</div> -->
          <div class="greet">欢迎</div>
          <div class="signout" href="/">回到首页</div>
        </div>
      </el-header>
      <el-container>
        <div class="sidebar">
          <el-button
            class="collapse-toggle-button"
            type="primary"
            @click="toggleCollapse"
          >
            <el-icon class="el-icon--left"><Grid /></el-icon>
          </el-button>
          <el-menu
            default-active="defaultIndex"
            class="el-menu-vertical-demo"
            :router="true"
            :collapse="isCollapse"
            @open="handleOpen"
            @close="handleClose"
          >
            <el-sub-menu index="0">
              <template #title>
                <el-icon><Document /></el-icon>
                <span>详情介绍</span>
              </template>
              <el-menu-item-group>
                <el-menu-item index="0-1" :route="{ name: 'intro' }"
                  >项目介绍</el-menu-item
                >
                <el-menu-item index="0-2" :route="{ name: 'language' }"
                  >合约介绍</el-menu-item
                >
              </el-menu-item-group>
              <el-menu-item index="0-3" :route="{ name: 'banner' }"
                >工具介绍</el-menu-item
              >
              <!-- <el-sub-menu index="0-4">
                <template #title><span>item four</span></template>
                <el-menu-item index="0-4-1">item one</el-menu-item>
              </el-sub-menu> -->
            </el-sub-menu>
            <el-sub-menu index="1">
              <template #title>
                <el-icon><Comment /></el-icon>
                <span>Dashboard</span>
              </template>
              <el-menu-item-group>
                <el-menu-item index="1-1" :route="{ name: 'tool' }"
                  >合约分析</el-menu-item
                >
                <el-menu-item index="1-2" :route="{ name: 'contractManage' }"
                  >合约管理</el-menu-item
                >
                <el-menu-item index="1-3" :route="{ name: 'record' }"
                  >日志管理</el-menu-item
                >
              </el-menu-item-group>
            </el-sub-menu>
            <el-menu-item index="2" :route="{ name: 'ide' }">
              <template #title>
                <el-icon><User /></el-icon>
                <span>IDE</span>
              </template>
            </el-menu-item>
            <el-menu-item index="3" >
              <template #title>
                <el-icon><Setting /></el-icon>
                <span>设置</span>
              </template>
            </el-menu-item>
          </el-menu>
        </div>
        <el-container>
          <el-main class="main">
            <router-view></router-view>
          </el-main>
          <el-footer class="footer">Footer</el-footer>
        </el-container>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import {
  Comment,
  User,
  // Search,
  Grid,
  Document,
  // Location,
  Setting,
} from "@element-plus/icons";
export default {
  name: "App",
  components: {
    Comment,
    User,
    // Search,
    Grid,
    Document,
    // Location,
    Setting,
  },
  data() {
    return {
      isCollapse: false,
    };
  },
  computed: {
    defaultIndex() {
      // http://127.0.0.1:8080/#/post
      const path = this.$route.path;
      let index = "1";
      if (path.indexOf("banner") >= 0) {
        index = "2";
      } else if (path.indexOf("post") >= 0) {
        index = "3";
      } else if (path.indexOf("comment") >= 0) {
        index = "4";
      } else if (path.indexOf("user") >= 0) {
        index = "5";
      } else if (path.indexOf("language") >= 0) {
        index = "9";
      } else {
        index = "1";
      }
      return index;
    },
  },
  mounted() {
    if (!this.$auth.is_staff) {
      //window.location = this.$http.server_host;
    }
  },
  methods: {
    has_permission(permissions) {
      console.log(permissions);
      console.log(this.$auth.user);
      return false;
    },
    toggleCollapse() {
      this.isCollapse = !this.isCollapse; // Toggle the collapse state
    },
    handleOpen(key, keyPath) {
      console.log("Menu opened:", key, keyPath);
      // Handle menu open logic here
    },
    handleClose(key, keyPath) {
      console.log("Menu closed:", key, keyPath);
      // Handle menu close logic here
    },
  },
};
</script>

<style scoped>
.frame-container {
  height: 100vh;
}
.header {
  height: 60px;
  background: #00a65a;
  display: flex;
}

.header .brand {
  width: 200px;
  margin-left: -20px;
  background-color: #008d4c;
  font-size: 20px;
  color: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
}
.header .header-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-left: 20px;
  color: #fff;
}

.header-content .signout {
  cursor: pointer;
}

.aside {
  background-color: #545c64;
}

.aside .el-menu .is-active {
  background-color: #434a50 !important;
}

.footer {
  background: gray;
}

.collapse-toggle-button {
  width: 40px;
  height: 20px;
  margin-top: 10px;
  margin-bottom: 10px;
  margin-left: 20px;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}
</style>

<style scoped>
.el-menu {
  border-right: none;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  border: 0;
  text-decoration: none;
  vertical-align: baseline;
}
</style>