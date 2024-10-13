<template>
  <div class="frame">
    <el-container class="frame-container">
      <el-header class="header">
        <div class="menu-and-greet">
          <el-menu
            :default-active="activeIndex"
            class="el-menu-demo"
            mode="horizontal"
            @select="handleSelect"
          >
            <el-menu-item index="1">Processing Center</el-menu-item>
            <el-sub-menu index="2">
              <template #title>Workspace</template>
              <el-menu-item index="2-1" :route="{ name: 'contractManage' }" >item one</el-menu-item>
              <el-menu-item index="2-2">item two</el-menu-item>
              <el-menu-item index="2-3">item three</el-menu-item>
              <el-sub-menu index="2-4">
                <template #title>item four</template>
                <el-menu-item index="2-4-1">item one</el-menu-item>
                <el-menu-item index="2-4-2">item two</el-menu-item>
                <el-menu-item index="2-4-3">item three</el-menu-item>
              </el-sub-menu>
            </el-sub-menu>
            <el-menu-item index="3"
              >Info</el-menu-item
            >
            <el-menu-item index="4">Orders</el-menu-item>
          </el-menu>
          <div class="greet">欢迎，周杰伦</div>
        </div>
      </el-header>
      <el-container>
        <el-button
          class="collapse-toggle-button"
          type="primary"
          @click="toggleCollapse"
        >
          <el-icon class="el-icon--left"><Grid /></el-icon>
        </el-button>
        <el-menu
          default-active="2"
          class="el-menu-vertical-demo"
          :collapse="isCollapse"
          @open="handleOpen"
          @close="handleClose"
        >
          <el-sub-menu index="1">
            <template #title>
              <el-icon><location /></el-icon>
              <span>Navigator One</span>
            </template>
            <el-menu-item-group>
              <template #title><span>Group One</span></template>
              <el-menu-item index="1-1">item one</el-menu-item>
              <el-menu-item index="1-2">item two</el-menu-item>
            </el-menu-item-group>
            <el-menu-item-group title="Group Two">
              <el-menu-item index="1-3">item three</el-menu-item>
            </el-menu-item-group>
            <el-sub-menu index="1-4">
              <template #title><span>item four</span></template>
              <el-menu-item index="1-4-1">item one</el-menu-item>
            </el-sub-menu>
          </el-sub-menu>
          <el-menu-item index="2" :route="{ name: 'search' }">
            <el-icon><icon-menu /></el-icon>
            <template #title>Navigator Two</template>
          </el-menu-item>
          <el-menu-item index="3" :route="{ name: 'language' }">
            <el-icon><document /></el-icon>
            <template #title>Navigator Three</template>
          </el-menu-item>
          <el-menu-item index="4">
            <el-icon><setting /></el-icon>
            <template #title>Navigator Four</template>
          </el-menu-item>
        </el-menu>
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

<script >
import {
  // PictureRounded,
  // Postcard,
  // Comment,
  // User,
  Grid,
  // Search,
  Document,
  Location,
  Setting,
} from "@element-plus/icons";
export default {
  name: "App",
  components: {
    // PictureRounded,
    // Postcard,
    // Comment,
    // User,
    Grid,
    // Search,
    Document,
    Location,
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

.aside {
  background-color: #545c64;
}

.aside .el-menu .is-active {
  background-color: #434a50 !important;
}

.footer {
  background: gray;
}
</style>

<style scoped>
.el-menu {
  border-right: none;
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

.header .el-menu-demo {
  background-color: #ffffff; /* Change as per your color scheme */
  border-bottom: 1px solid #ebeef5; /* Adds a subtle border */
}

.header .el-menu-demo .el-menu-item,
.header .el-menu-demo .el-sub-menu__title {
  color: #303133; /* Text color */
  font-size: 16px; /* Adjust text size as needed */
}

.header .el-menu-demo .el-menu-item:hover,
.header .el-menu-demo .el-sub-menu__title:hover {
  background-color: #f5f5f5; /* Background color on hover */
  color: #409eff; /* Text color on hover */
}

/* Style for disabled menu items */
.header .el-menu-demo .el-menu-item.is-disabled {
  color: #c0c4cc;
}

/* Submenu specific styling */
.header .el-menu-demo .el-sub-menu {
  background-color: #ffffff; /* Adjust for submenu */
}

/* Additional styling for nested submenus if needed */
.header .el-menu-demo .el-sub-menu .el-sub-menu {
  background-color: #f9f9f9; /* Slightly different color for nested submenus */
}

.menu-and-greet {
  display: flex;
  align-items: center;
  width: 100%;
}

.header .el-menu-demo {
  flex: 0 0 90%;
}

.greet {
  flex: 1; /* Greet takes the remaining space */
  font-size: 16px; /* Adjust the font size as needed */
  color: #303133;
}

/* Responsive design adjustments if necessary */
@media (max-width: 768px) {
  /* Adjust menu styles for smaller screens */
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