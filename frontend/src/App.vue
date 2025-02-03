<template>
  <div class="app-container">
    <div class="sidebar">
      <div class="logo">
        <h1>BiliNew</h1>
      </div>
      <nav>
        <router-link to="/" class="nav-item">
          <el-icon><House /></el-icon>
          首页
        </router-link>
        <router-link to="/search" class="nav-item">
          <el-icon><Search /></el-icon>
          搜索
        </router-link>
      </nav>
    </div>
    <div class="main-content">
      <router-view></router-view>
    </div>
    <div class="player-bar">
      <player-controls />
    </div>
  </div>
</template>

<script setup>
import { House, Search } from '@element-plus/icons-vue'
import PlayerControls from './components/PlayerControls.vue'
</script>

<style scoped>
.app-container {
  display: grid;
  grid-template-areas:
    "sidebar main"
    "player player";
  grid-template-columns: 250px 1fr;
  grid-template-rows: 1fr 80px;
  height: 100vh;
}

.sidebar {
  grid-area: sidebar;
  background: var(--el-bg-color-overlay);
  border-right: 1px solid var(--el-border-color-light);
  padding: 20px;
}

.logo {
  margin-bottom: 30px;
  text-align: center;
}

.logo h1 {
  font-size: 24px;
  color: var(--el-color-primary);
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  text-decoration: none;
  color: var(--el-text-color-primary);
  border-radius: 8px;
  transition: all 0.3s;
}

.nav-item:hover {
  background: var(--el-color-primary-light-9);
}

.nav-item .el-icon {
  margin-right: 12px;
}

.main-content {
  grid-area: main;
  padding: 20px;
  overflow-y: auto;
}

.player-bar {
  grid-area: player;
  background: var(--el-bg-color-overlay);
  border-top: 1px solid var(--el-border-color-light);
}
</style> 