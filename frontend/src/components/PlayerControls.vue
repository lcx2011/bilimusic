<template>
  <div class="player-controls">
    <div class="track-info" v-if="playerStore.currentTrack">
      <div class="cover-wrapper">
        <img
          v-if="!imageError && playerStore.currentTrack.cover"
          :src="coverUrl"
          class="cover-image"
          @error="handleImageError"
          @load="handleImageLoad"
          @click="handleImagePreview"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"
        />
        <div v-else class="image-placeholder">
          <el-icon><Picture /></el-icon>
        </div>
      </div>
      <div class="track-text">
        <h3 class="title">{{ playerStore.currentTrack.title }}</h3>
        <p class="artist">{{ playerStore.currentTrack.artist }}</p>
      </div>
    </div>

    <div class="controls">
      <el-button
        circle
        :icon="playerStore.isPlaying ? VideoPause : VideoPlay"
        @click="playerStore.togglePlay"
        :disabled="!playerStore.currentTrack"
        class="play-button"
      />
    </div>

    <div class="progress-container">
      <div class="time current">{{ playerStore.currentTime }}</div>
      <div class="progress-bar">
        <el-slider
          v-model="progress"
          :max="playerStore.duration"
          @change="handleSeek"
          :disabled="!playerStore.currentTrack"
        />
      </div>
      <div class="time total">{{ playerStore.totalTime }}</div>
    </div>

    <div class="lyrics-container" v-if="currentTrack">
      <div class="lyrics-header" :class="{ hidden: lyrics.length > 0 }">
        <el-input
          v-model="originalTitle"
          placeholder="输入歌曲原名以获取歌词"
          class="title-input"
          size="small"
        >
          <template #append>
            <el-button @click="handleFetchLyrics" size="small">获取歌词</el-button>
          </template>
        </el-input>
      </div>
      
      <div class="lyrics-wrapper" :class="{ visible: lyrics.length > 0 }" ref="lyricsRef">
        <div v-if="lyrics.length === 0" class="empty-lyrics">
          <p>暂无歌词</p>
          <p class="tip">{{ needManualInput ? '请输入正确的歌曲原名' : '正在加载歌词...' }}</p>
        </div>
        <div 
          v-else
          v-for="(line, index) in visibleLyrics" 
          :key="index"
          class="lyric-line"
          :class="getLyricClass(index)"
        >
          {{ line.text }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick } from 'vue'
import { VideoPlay, VideoPause, Picture } from '@element-plus/icons-vue'
import { usePlayerStore } from '../store/player'
import { ElImage, ElMessage } from 'element-plus'

const playerStore = usePlayerStore()
const progress = ref(0)
const imageError = ref(false)
const coverUrl = ref('')
const currentTrack = computed(() => playerStore.currentTrack)
const lyrics = ref([])
const currentLyricIndex = ref(-1)
const lyricsRef = ref(null)
const originalTitle = ref('')
const needManualInput = ref(false)

// 立即检查 store 状态
;(() => {
  console.log('Initial playerStore state:', {
    currentTrack: playerStore.currentTrack,
    cover: playerStore.currentTrack?.cover,
    title: playerStore.currentTrack?.title,
  })
})()

// 监听整个 currentTrack 对象的变化
watch(currentTrack, (newTrack) => {
  console.log('Current track changed:', newTrack)
  if (newTrack?.cover) {
    const url = getProxyImageUrl(newTrack.cover)
    console.log('Setting cover URL:', url)
    coverUrl.value = url
    imageError.value = false
  } else {
    console.log('No track or cover')
    coverUrl.value = ''
    imageError.value = true
  }

  // 重置歌词状态
  if (newTrack?.title) {
    console.log('Track bvid:', newTrack.bvid)
    originalTitle.value = newTrack.title
    lyrics.value = []
    // 移除自动获取歌词
    // handleFetchLyrics()
    needManualInput.value = true
  } else {
    lyrics.value = []
    originalTitle.value = ''
    needManualInput.value = false
  }
}, { immediate: true, deep: true })

const getProxyImageUrl = (url) => {
  if (!url) return ''
  
  console.log('Processing URL:', url)
  let processedUrl = url
  
  // 如果已经是完整的 URL，直接使用
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
  
  console.log('Processed URL:', processedUrl)
  return `/api/proxy/image?url=${encodeURIComponent(processedUrl)}`
}

const handleImageLoad = (e) => {
  console.log('Image loaded successfully:', e.target.src)
  imageError.value = false
}

const handleImageError = (e) => {
  console.error('Image load failed:', e.target.src)
  // 如果是代理 URL 失败，尝试直接加载原始 URL
  if (e.target.src.includes('/api/proxy/image')) {
    const originalUrl = currentTrack.value?.cover
    if (originalUrl) {
      console.log('Trying original URL:', originalUrl)
      // 确保原始 URL 有 https 前缀
      const secureUrl = originalUrl.startsWith('//') ? 'https:' + originalUrl : originalUrl
      e.target.src = secureUrl
      return // 不要立即设置 imageError
    }
  }
  imageError.value = true
}

const handleImagePreview = () => {
  if (!coverUrl.value) return
  ElImage.preview({
    urls: [coverUrl.value],
    initialIndex: 0,
  })
}

watch(() => playerStore.progress, (newValue) => {
  progress.value = newValue
})

const handleSeek = (value) => {
  playerStore.seek(value)
}

// 监听当前播放时间，更新歌词
watch(() => playerStore.progress, (newTime) => {
  if (!lyrics.value.length) return
  
  const currentTime = Math.floor(newTime)
  const index = lyrics.value.findIndex((line, i) => {
    const nextLine = lyrics.value[i + 1]
    return line.time <= currentTime && (!nextLine || nextLine.time > currentTime)
  })
  
  if (index !== -1) {
    currentLyricIndex.value = index
  }
})

// 添加计算属性来控制显示的歌词行数
const visibleLyrics = computed(() => {
  if (!lyrics.value || lyrics.value.length === 0) return [];
  
  if (currentLyricIndex.value === -1) {
    // 如果还没有当前行，显示前两行
    return lyrics.value.slice(0, 2);
  }
  
  // 只显示当前行和下一行
  return lyrics.value.slice(currentLyricIndex.value, currentLyricIndex.value + 2);
});

// 修改歌词行的样式类
const getLyricClass = (index) => {
  return { current: index === 0 };
};

// 修改获取歌词的处理函数
const handleFetchLyrics = async () => {
  if (!originalTitle.value.trim()) {
    ElMessage.warning('请输入歌曲原名')
    return
  }

  console.log('Current track:', currentTrack.value)
  console.log('Attempting to get id:', currentTrack.value?.id)

  if (!currentTrack.value?.id) {
    ElMessage.warning('无法获取视频ID')
    return
  }
  
  try {
    const url = `/api/lyrics?id=${currentTrack.value.id}&title=${encodeURIComponent(originalTitle.value.trim())}`
    console.log('Fetching lyrics with URL:', url)
    
    const response = await fetch(url)
    if (response.ok) {
      const data = await response.json()
      console.log('Lyrics response:', data)
      if (data.code === 0) {
        if (data.data.lyrics.length > 0) {
          lyrics.value = data.data.lyrics
          // 如果是从缓存获取的歌词，不需要显示搜索框
          needManualInput.value = !data.data.from_cache
          ElMessage.success(data.data.from_cache ? '已加载缓存歌词' : '已获取歌词')
        } else {
          ElMessage.warning('未找到歌词，请检查歌曲名称是否正确')
          lyrics.value = []
          needManualInput.value = true
        }
      } else {
        throw new Error(data.message || '获取歌词失败')
      }
    } else {
      throw new Error('获取歌词失败')
    }
  } catch (error) {
    console.error('Error fetching lyrics:', error)
    ElMessage.error(error.message)
    lyrics.value = []
    needManualInput.value = true
  }
}
</script>

<style scoped>
.player-controls {
  height: 100%;
  display: grid;
  grid-template-columns: 280px 80px minmax(300px, 1fr) 250px;
  align-items: center;
  padding: 0 20px;
  background: var(--el-bg-color);
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.08);
}

.track-info {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-right: 24px;
  border-right: 1px solid var(--el-border-color-lighter);
  min-width: 0;
  overflow: hidden;
}

.cover-wrapper {
  position: relative;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  background: var(--el-fill-color-lighter);
  cursor: pointer;
}

.cover-wrapper:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
  display: block;
  background-color: var(--el-fill-color-lighter);
  transition: opacity 0.3s ease;
}

.cover-image:not([src]), 
.cover-image[src=""], 
.cover-image[src="null"], 
.cover-image[src="undefined"] {
  display: none;
}

.image-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-secondary);
  border-radius: 12px;
}

.image-placeholder .el-icon {
  font-size: 24px;
  opacity: 0.5;
}

.track-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}

.track-text .title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.4;
  color: var(--el-text-color-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.track-text .artist {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
}

.play-button {
  width: 40px;
  height: 40px;
  font-size: 20px;
  border: none;
  background: var(--el-color-primary);
  color: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 0;
}

.play-button:not(:disabled):hover {
  transform: scale(1.1);
  box-shadow: 0 6px 18px rgba(var(--el-color-primary-rgb), 0.35);
}

.play-button:disabled {
  background: var(--el-fill-color-lighter);
  color: var(--el-text-color-placeholder);
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 24px;
  min-width: 0;
  width: 100%;
  justify-content: center;
  flex: 1;
}

.progress-bar {
  flex: 1;
  padding: 0 8px;
  min-width: 500px;
  max-width: 1000px;
}

.time {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  width: 48px;
  text-align: center;
  font-family: 'JetBrains Mono', monospace;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}

:deep(.el-slider) {
  --el-slider-button-size: 12px;
  --el-slider-height: 4px;
  margin: 0;
  width: 100%;
}

:deep(.el-slider__runway) {
  height: var(--el-slider-height);
  background-color: var(--el-fill-color-darker);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width: 100%;
}

:deep(.el-slider__bar) {
  height: var(--el-slider-height);
  background-color: var(--el-color-primary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-slider__button-wrapper) {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-slider__button) {
  width: var(--el-slider-button-size);
  height: var(--el-slider-button-size);
  border: 2px solid var(--el-color-primary);
  background-color: var(--el-color-white);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.el-slider:hover .el-slider__runway),
:deep(.el-slider:hover .el-slider__bar) {
  height: 6px;
}

:deep(.el-slider:hover .el-slider__button) {
  transform: scale(1.2);
}

@media (max-width: 1200px) {
  .player-controls {
    grid-template-columns: 240px 60px minmax(300px, 1fr) 200px;
  }
  
  .progress-bar {
    min-width: 200px;
  }

  .play-button {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .lyrics-container {
    width: 200px;
  }
}

@media (max-width: 768px) {
  .player-controls {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto auto;
    gap: 16px;
    padding: 16px;
    height: auto;
  }

  .track-info {
    border-right: none;
    padding-right: 0;
  }

  .progress-container {
    padding: 0;
  }

  .progress-bar {
    min-width: 200px;
  }

  .lyrics-container {
    width: 100%;
    height: 120px;
    border-left: none;
    border-top: 1px solid var(--el-border-color-lighter);
    padding-top: 12px;
  }

  .play-button {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}

:deep(.el-image) {
  width: 100%;
  height: 100%;
  display: block;
}

.lyrics-container {
  height: 100%;
  width: 250px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
  border-left: 1px solid var(--el-border-color-lighter);
  padding: 0 12px;
}

.lyrics-header {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  opacity: 1;
  transition: opacity 0.3s, transform 0.3s;
  z-index: 1;
}

.lyrics-header.hidden {
  opacity: 0;
  transform: translate(-50%, -100%);
  pointer-events: none;
}

.lyrics-wrapper {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 60px; /* 限制高度只显示两行 */
}

.lyrics-wrapper.visible {
  opacity: 1;
}

.empty-lyrics {
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.empty-lyrics .tip {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.7;
}

.lyric-line {
  font-size: 14px;
  line-height: 24px;
  color: #666;
  transition: all 0.3s ease;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lyric-line.current {
  color: #409EFF; /* 使用蓝色突出显示当前歌词 */
  font-weight: 500;
}
</style> 