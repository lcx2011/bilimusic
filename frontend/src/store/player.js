import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

export const usePlayerStore = defineStore('player', () => {
  const currentTrack = ref(null)
  const isPlaying = ref(false)
  const audio = ref(new Audio())
  const progress = ref(0)
  const duration = ref(0)
  const volume = ref(1)

  console.log('Initial playerStore state:', { currentTrack: currentTrack.value, isPlaying: isPlaying.value })

  const currentTime = computed(() => {
    return formatTime(progress.value)
  })

  const totalTime = computed(() => {
    return formatTime(duration.value)
  })

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  // 初始化音频事件监听
  audio.value.ontimeupdate = () => {
    progress.value = audio.value.currentTime
    duration.value = audio.value.duration
  }

  audio.value.onended = () => {
    isPlaying.value = false
    progress.value = 0
    // TODO: 播放下一首
  }

  audio.value.onerror = (e) => {
    console.error('音频播放错误:', e)
    ElMessage.error('播放失败，请稍后重试')
    isPlaying.value = false
  }

  audio.value.volume = volume.value

  // 播放音乐
  async function play(track) {
    console.log('Current track changed:', track)
    if (!track) {
      console.log('No track or cover')
      return
    }

    if (currentTrack.value?.id === track.id) {
      if (isPlaying.value) {
        console.log('Pausing current track')
        audio.value.pause()
        isPlaying.value = false
        return
      }
      try {
        console.log('Resuming current track')
        await audio.value.play()
        isPlaying.value = true
        return
      } catch (error) {
        console.error('播放失败:', error)
        ElMessage.error('播放失败，请稍后重试')
        return
      }
    }

    try {
      console.log('Getting audio URL for:', track.id)
      const response = await axios.get(`/api/play/${track.id}`)
      console.log('API response:', response.data)
      
      if (response.data.code === 0) {
        currentTrack.value = track
        console.log('Setting audio source:', response.data.data.url)
        audio.value.src = response.data.data.url
        console.log('Starting playback')
        await audio.value.play()
        isPlaying.value = true
        console.log('Playback started successfully')
      } else {
        throw new Error(response.data.msg || '获取音频失败')
      }
    } catch (error) {
      console.error('播放失败:', error)
      ElMessage.error('播放失败，请稍后重试')
      throw error
    }
  }

  // 暂停
  function pause() {
    console.log('Pausing playback')
    audio.value.pause()
    isPlaying.value = false
  }

  // 切换播放状态
  function togglePlay() {
    if (isPlaying.value) {
      pause()
    } else if (currentTrack.value) {
      play(currentTrack.value)
    }
  }

  // 跳转到指定时间
  function seek(time) {
    if (audio.value.src) {
      audio.value.currentTime = time
      progress.value = time
    }
  }

  // 设置音量
  function setVolume(value) {
    volume.value = value
    audio.value.volume = value
  }

  return {
    currentTrack,
    isPlaying,
    progress,
    duration,
    currentTime,
    totalTime,
    volume,
    play,
    pause,
    togglePlay,
    seek,
    setVolume
  }
}) 