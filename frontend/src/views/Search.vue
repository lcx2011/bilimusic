<template>
  <div class="search-page">
    <div class="search-bar">
      <el-input
        v-model="keyword"
        placeholder="搜索音乐..."
        :prefix-icon="Search"
        @keyup.enter="handleSearch"
        clearable
      >
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>
    </div>

    <div class="search-results" v-loading="loading">
      <div v-if="results.length === 0 && !loading" class="empty-state">
        <el-icon><Search /></el-icon>
        <p>{{ keyword ? '未找到相关歌曲' : '输入关键词开始搜索' }}</p>
      </div>
      
      <div v-else class="results-list">
        <div v-for="item in results" :key="item.bvid" class="result-item">
          <div class="cover">
            <img :src="getProxyImageUrl(item.pic)" @error="handleImageError" />
          </div>
          <div class="info">
            <div class="title-row">
              <h3 class="title">{{ item.title }}</h3>
              <div class="actions">
                <el-button type="primary" @click="handlePlay(item)" :icon="VideoPlay">
                  播放
                </el-button>
                <el-dropdown @command="(id) => handleAddToPlaylist(id, item)">
                  <el-button :icon="Plus">
                    添加到专辑
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                        v-for="playlist in playlists"
                        :key="playlist.id"
                        :command="playlist.id"
                      >
                        {{ playlist.name }}
                      </el-dropdown-item>
                      <el-dropdown-item v-if="playlists.length === 0" disabled>
                        暂无专辑
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>
            <p class="author">UP主：{{ item.author }}</p>
            <p class="stats">
              <span>播放：{{ item.play }}</span>
              <span>弹幕：{{ item.danmaku }}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, VideoPlay, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { usePlayerStore } from '../store/player'

const playerStore = usePlayerStore()
const keyword = ref('')
const results = ref([])
const loading = ref(false)
const playlists = ref([])

const handleSearch = async () => {
  if (!keyword.value.trim()) return
  
  loading.value = true
  try {
    const response = await fetch(`/api/search?keyword=${encodeURIComponent(keyword.value)}`)
    if (response.ok) {
      const data = await response.json()
      if (data.code === 0) {
        results.value = data.data
      } else {
        throw new Error(data.message || '搜索失败')
      }
    } else {
      throw new Error('搜索失败')
    }
  } catch (error) {
    ElMessage.error(error.message)
  } finally {
    loading.value = false
  }
}

const handlePlay = (track) => {
  console.log('Playing track:', track)
  const trackInfo = {
    id: track.id,
    title: track.title,
    artist: track.author,
    cover: track.pic,
    duration: track.duration
  }
  console.log('Track info:', trackInfo)
  playerStore.play(trackInfo)
}

const getProxyImageUrl = (url) => {
  if (!url) return ''
  return `/api/proxy/image?url=${encodeURIComponent(url)}`
}

const handleImageError = (e) => {
  e.target.src = ''
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

const handleAddToPlaylist = async (playlistId, track) => {
  try {
    const trackInfo = {
      id: track.id,
      title: track.title,
      artist: track.author,
      cover: track.pic,
      duration: track.duration
    }
    
    const response = await fetch(`/api/playlists/${playlistId}/tracks`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ track: trackInfo })
    })
    
    if (response.ok) {
      ElMessage.success('已添加到专辑')
    } else {
      const data = await response.json()
      throw new Error(data.message || '添加失败')
    }
  } catch (error) {
    ElMessage.error(error.message)
  }
}

onMounted(() => {
  fetchPlaylists()
})
</script>

<style scoped>
.search-page {
  padding: 20px;
}

.search-bar {
  margin-bottom: 24px;
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

.results-list {
  background: var(--el-bg-color-overlay);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

.result-item {
  display: flex;
  padding: 16px;
  gap: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  transition: all 0.3s;
}

.result-item:last-child {
  border-bottom: none;
}

.result-item:hover {
  background: var(--el-fill-color-light);
}

.cover {
  width: 80px;
  height: 80px;
  flex-shrink: 0;
  border-radius: 4px;
  overflow: hidden;
  background: var(--el-fill-color-lighter);
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.result-item:hover .cover img {
  transform: scale(1.05);
}

.info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.author {
  margin: 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.stats {
  margin: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: flex;
  gap: 16px;
}

:deep(.el-button) {
  padding: 6px 12px;
  font-size: 13px;
}

:deep(.el-button .el-icon) {
  font-size: 14px;
}
</style> 