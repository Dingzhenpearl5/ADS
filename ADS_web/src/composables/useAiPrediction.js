import { ref, onUnmounted } from 'vue'
import { io } from 'socket.io-client'
import { ElMessage, ElNotification } from 'element-plus'

export function useAiPrediction() {
  const socket = ref(null)
  const percentage = ref(0)
  const progressStatus = ref('等待任务启动...')
  const isProcessing = ref(false)
  
  // 结果数据
  const resultData = ref({
    url2: '',
    featureList: [],
    area: 0,
    perimeter: 0
  })

  const initSocket = () => {
    const socketUrl = process.env.VUE_APP_SOCKET_URL || 'http://127.0.0.1:5003'
    
    socket.value = io(socketUrl, {
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 5,
      timeout: 10000
    })

    socket.value.on('connect', () => {
      console.log('[Socket] ✅ 已连接到后端服务')
    })

    socket.value.on('connected', (data) => {
      console.log('[Socket] 服务器确认连接:', data)
    })

    socket.value.on('connect_error', (err) => {
      console.log('[Socket] ⚠️ 连接失败:', err.message)
    })

    socket.value.on('progress', (data) => {
      console.log('[Socket] 收到进度:', data)
      isProcessing.value = true
      percentage.value = data.percentage
      progressStatus.value = data.message
      
      if (data.percentage === 100) {
        setTimeout(() => {
          isProcessing.value = false
          ElNotification({
            title: '诊断完成',
            message: 'AI 辅助诊断已成功完成，请查看结果。',
            type: 'success',
          })
        }, 1000)
      }
    })

    socket.value.on('result', (data) => {
      console.log('[Socket] 收到结果:', data)
      resultData.value = {
        url2: data.url2,
        featureList: data.feature_list,
        area: data.area,
        perimeter: data.perimeter
      }
    })

    socket.value.on('error', (err) => {
      console.error('[Socket] 错误:', err)
      ElMessage.error('诊断过程出错: ' + err)
      isProcessing.value = false
    })
  }

  const disconnectSocket = () => {
    if (socket.value) {
      socket.value.disconnect()
    }
  }

  onUnmounted(() => {
    disconnectSocket()
  })

  return {
    percentage,
    progressStatus,
    isProcessing,
    resultData,
    initSocket,
    disconnectSocket
  }
}
