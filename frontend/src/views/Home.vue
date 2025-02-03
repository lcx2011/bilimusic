<template>
  <div class="home">
    <div class="header">
      <h2 class="title">我的专辑</h2>
      <el-button type="primary" @click="showCreatePlaylistDialog">
        <el-icon><Plus /></el-icon>
        创建专辑
      </el-button>
    </div>
    <playlist-grid ref="playlistGrid" />

    <!-- 创建专辑对话框 -->
    <el-dialog
      v-model="createPlaylistDialogVisible"
      title="创建新专辑"
      width="30%"
      :close-on-click-modal="false"
    >
      <el-form :model="playlistForm" label-width="80px">
        <el-form-item label="专辑名称">
          <el-input v-model="playlistForm.name" placeholder="请输入专辑名称"></el-input>
        </el-form-item>
        <el-form-item label="专辑描述">
          <el-input
            v-model="playlistForm.description"
            type="textarea"
            placeholder="请输入专辑描述"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="createPlaylistDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="createPlaylist">创建</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import PlaylistGrid from '../components/PlaylistGrid.vue'

const playlistGrid = ref(null)
const createPlaylistDialogVisible = ref(false)
const playlistForm = ref({
  name: '',
  description: ''
})

const showCreatePlaylistDialog = () => {
  createPlaylistDialogVisible.value = true
}

const createPlaylist = async () => {
  if (!playlistForm.value.name.trim()) {
    ElMessage.warning('请输入专辑名称')
    return
  }
  
  try {
    const response = await fetch('/api/playlists', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(playlistForm.value)
    })
    
    if (response.ok) {
      ElMessage.success('专辑创建成功')
      createPlaylistDialogVisible.value = false
      playlistForm.value = { name: '', description: '' }
      playlistGrid.value?.fetchPlaylists()
    } else {
      throw new Error('创建失败')
    }
  } catch (error) {
    ElMessage.error('创建专辑失败')
  }
}

// 提供刷新方法给父组件
defineExpose({
  refresh: () => {
    playlistGrid.value?.fetchPlaylists()
  }
})
</script>

<style scoped>
.home {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style> 