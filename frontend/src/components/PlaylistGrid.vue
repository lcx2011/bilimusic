<template>
  <div class="playlist-grid">
    <div v-if="playlists.length === 0" class="empty-state">
      <el-icon><Document /></el-icon>
      <p>还没有创建任何专辑</p>
    </div>
    <div v-else class="grid">
      <div 
        v-for="playlist in playlists" 
        :key="playlist.id" 
        class="playlist-card"
        @click="router.push(`/playlist/${playlist.id}`)"
      >
        <div class="cover">
          <div class="placeholder">
            <el-icon><Headset /></el-icon>
          </div>
        </div>
        <div class="info">
          <h3 class="name">{{ playlist.name }}</h3>
          <p class="description">{{ playlist.description || '暂无描述' }}</p>
          <p class="meta">
            <span>{{ playlist.tracks.length }}首歌曲</span>
            <span>{{ formatDate(playlist.created_at) }}</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Document, Headset } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()
const playlists = ref([])

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

const fetchPlaylists = async () => {
  try {
    const response = await fetch('/api/playlists')
    if (response.ok) {
      playlists.value = await response.json()
    } else {
      throw new Error('获取专辑列表失败')
    }
  } catch (error) {
    ElMessage.error(error.message)
  }
}

onMounted(() => {
  fetchPlaylists()
})

defineExpose({
  fetchPlaylists
})
</script>

<style scoped>
.playlist-grid {
  padding: 20px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--el-text-color-secondary);
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 24px;
}

.playlist-card {
  background: var(--el-bg-color-overlay);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  cursor: pointer;
  border: 1px solid var(--el-border-color-lighter);
}

.playlist-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--el-border-color);
}

.cover {
  aspect-ratio: 1;
  background: var(--el-fill-color-lighter);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder {
  color: var(--el-text-color-secondary);
}

.placeholder .el-icon {
  font-size: 48px;
  opacity: 0.5;
}

.info {
  padding: 16px;
}

.name {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.description {
  margin: 8px 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 40px;
}

.meta {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: flex;
  justify-content: space-between;
}
</style> 