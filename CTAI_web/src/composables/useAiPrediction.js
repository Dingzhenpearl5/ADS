import { ref, onUnmounted } from 'vue'
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
    // Socket.IO 为可选功能，当前使用 HTTP 轮询替代
    // 如需启用实时通信，请在后端集成 flask-socketio
    try {
      const socketUrl = process.env.VUE_APP_SOCKET_URL || 'http://127.0.0.1:5003'
      
      // 动态导入 socket.io-client，避免未安装时报错
      import('socket.io-client').then(({ io }) => {
        socket.value = io(socketUrl, {
          transports: ['websocket', 'polling'],
          reconnectionAttempts: 3,
          timeout: 5000
        })

        socket.value.on('connect', () => {
          console.log('[Socket] Connected to AI Engine')
        })

        socket.value.on('connect_error', (err) => {
          console.log('[Socket] 连接失败，使用 HTTP 模式:', err.message)
          socket.value.disconnect()
        })

        socket.value.on('progress', (data) => {
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
          resultData.value = {
            url2: data.url2,
            featureList: data.feature_list,
            area: data.area,
            perimeter: data.perimeter
          }
        })

        socket.value.on('error', (err) => {
          ElMessage.error('诊断过程出错: ' + err)
          isProcessing.value = false
        })
      }).catch(() => {
        console.log('[Socket] socket.io-client 未安装，使用 HTTP 模式')
      })
    } catch (e) {
      console.log('[Socket] 初始化失败，使用 HTTP 模式')
    }
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
