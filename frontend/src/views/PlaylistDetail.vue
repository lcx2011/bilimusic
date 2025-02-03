<template>
  <div class="playlist-detail" v-loading="loading">
    <div v-if="playlist" class="content">
      <div class="header">
        <h2>{{ playlist.name }}</h2>
        <p class="description">{{ playlist.description || '暂无描述' }}</p>
        <p class="meta">
          创建时间：{{ formatDate(playlist.created_at) }}
          <span class="separator">|</span>
          {{ playlist.tracks.length }} 首歌曲
        </p>
      </div>

      <div class="tracks-list">
        <div v-if="playlist.tracks.length === 0" class="empty-state">
          <el-icon><Folder /></el-icon>
          <p>暂无歌曲</p>
          <el-button type="primary" @click="$router.push('/search')">
            去添加歌曲
          </el-button>
        </div>
        
        <div v-else class="track-items">
          <div v-for="(track, index) in playlist.tracks" :key="track.id" class="track-item">
            <span class="index">{{ index + 1 }}</span>
            <div class="cover">
              <img :src="getProxyImageUrl(track.cover)" @error="handleImageError" />
            </div>
            <div class="info">
              <h3 class="title">{{ track.title }}</h3>
              <p class="artist">{{ track.artist }}</p>
            </div>
            <div class="actions">
              <el-button circle :icon="VideoPlay" @click="handlePlay(track)" />
              <el-button 
                circle 
                :icon="Delete"
                @click="handleDelete(track)"
                type="danger"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, Delete, Folder } from '@element-plus/icons-vue'
import { usePlayerStore } from '../store/player'

const route = useRoute()
const router = useRouter()
const playerStore = usePlayerStore()
const playlist = ref(null)
const loading = ref(true)

const fetchPlaylist = async () => {
  loading.value = true
  try {
    console.log('Fetching playlist:', route.params.id)
    const response = await fetch(`/api/playlists/${route.params.id}`)
    if (response.ok) {
      const data = await response.json()
      console.log('Playlist data:', data)
      if (data.code === 0) {
        playlist.value = data.data
      } else {
        throw new Error(data.message || '获取播放列表失败')
      }
    } else {
      throw new Error('获取播放列表失败')
    }
  } catch (error) {
    console.error('Error fetching playlist:', error)
    ElMessage.error(error.message)
    router.push('/')
  } finally {
    loading.value = false
  }
}

const handlePlay = (track) => {
  console.log('Playing track:', track)
  const trackInfo = {
    id: track.id,
    title: track.title,
    artist: track.artist,
    cover: track.cover,
    duration: track.duration
  }
  console.log('Track info:', trackInfo)
  playerStore.play(trackInfo)
}

const handleDelete = async (track) => {
  try {
    await ElMessageBox.confirm('确定要删除这首歌吗？', '提示', {
      type: 'warning'
    })
    
    const response = await fetch(`/api/playlists/${route.params.id}/tracks/${track.id}`, {
      method: 'DELETE'
    })
    
    if (response.ok) {
      const data = await response.json()
      if (data.code === 0) {
        playlist.value = data.data
        ElMessage.success('删除成功')
      } else {
        throw new Error(data.message || '删除失败')
      }
    } else {
      throw new Error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.message)
    }
  }
}

const getProxyImageUrl = (url) => {
  if (!url) return ''
  
  console.log('处理图片URL:', url)
  let processedUrl = url
  
  // 如果已经是完整的URL，直接使用
  if (url.startsWith('http')) {
    processedUrl = url
  } 
  // 如果是相对路径，添加协议
  else if (url.startsWith('//')) {
    processedUrl = 'https:' + url
  }
  // 如果是完全的相对路径
  else {
    processedUrl = 'https://' + url.replace(/^\/+/, '')
  }
  
  console.log('处理后的URL:', processedUrl)
  return `/api/proxy/image?url=${encodeURIComponent(processedUrl)}`
}

const handleImageError = (e) => {
  console.error('图片加载失败:', e.target.src)
  e.target.src = ''
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchPlaylist()
})
</script>

<style scoped>
.playlist-detail {
  padding: 20px;
}

.header {
  margin-bottom: 24px;
}

.header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.description {
  margin: 0 0 16px 0;
  color: var(--el-text-color-secondary);
}

.meta {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.separator {
  margin: 0 8px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  color: var(--el-text-color-secondary);
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.track-items {
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

.track-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s;
}

.track-item:last-child {
  border-bottom: none;
}

.track-item:hover {
  background: var(--el-fill-color-light);
}

.index {
  width: 32px;
  text-align: center;
  color: var(--el-text-color-secondary);
}

.cover {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  background: var(--el-fill-color-lighter);
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info {
  flex: 1;
  min-width: 0;
}

.info .title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 500;
}

.info .artist {
  margin: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.actions {
  display: flex;
  gap: 8px;
}
</style> 