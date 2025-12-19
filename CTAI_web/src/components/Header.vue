<template>
    <div id="Header">
        <div class="header-container">
            <!-- 左侧标题 -->
            <div class="logo-title">
                <h1>{{msg}}</h1>
            </div>

            <!-- 中间导航栏 -->
            <div class="nav-menu">
                <el-menu 
                    :default-active="activeIndex" 
                    class="el-menu-demo" 
                    mode="horizontal" 
                    :ellipsis="false"
                    @select="handleSelect"
                    style="border-bottom: none; background-color: transparent;"
                >
                    <el-menu-item index="1">首页</el-menu-item>
                    <el-menu-item index="2">历史记录</el-menu-item>
                    <el-menu-item index="3">数据分析</el-menu-item>
                    <el-menu-item index="4">系统设置</el-menu-item>
                </el-menu>
                
                <!-- 操作按钮 -->
                <div class="action-buttons" style="margin-left: 20px; display: flex; align-items: center;">
                    <el-button type="primary" plain size="small" @click="$emit('download-template')">
                        <el-icon style="margin-right: 5px"><Download /></el-icon>下载测试数据
                    </el-button>
                    <el-button type="primary" size="small" @click="triggerUpload" style="margin-left: 10px;">
                        <el-icon style="margin-right: 5px"><Upload /></el-icon>上传CT图像
                    </el-button>
                    <input 
                        type="file" 
                        ref="fileInput" 
                        style="display: none" 
                        accept=".dcm"
                        @change="handleFileChange"
                    >
                </div>
            </div>
            
            <!-- 右侧用户信息区域 -->
            <div class="user-info">
                <el-dropdown @command="handleCommand">
                    <span class="el-dropdown-link">
                        <el-avatar :size="32" :icon="UserFilled"></el-avatar>
                        <span class="username">{{ userInfo.name || '用户' }}</span>
                        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                    </span>
                    <template #dropdown>
                        <el-dropdown-menu>
                            <el-dropdown-item :icon="User" disabled>
                                {{ userInfo.role === 'admin' ? '管理员' : '医生' }}
                            </el-dropdown-item>
                            <el-dropdown-item :icon="Setting" divided>个人设置</el-dropdown-item>
                            <el-dropdown-item :icon="SwitchButton" command="logout">退出登录</el-dropdown-item>
                        </el-dropdown-menu>
                    </template>
                </el-dropdown>
            </div>
        </div>
    </div>
</template>
<script>
    import { UserFilled, ArrowDown, User, Setting, SwitchButton, Download, Upload } from '@element-plus/icons-vue'

    export default {
        name: "AppHeader",
        emits: ['download-template', 'upload-file'],
        data() {
            return {
                msg: "肿瘤辅助诊断系统",
                activeIndex: "1",
                userInfo: {},
                UserFilled,
                User,
                Setting,
                SwitchButton,
                Download,
                Upload
            };
        },
        components: {
            ArrowDown,
            Download,
            Upload
        },
        created() {
            // 获取用户信息
            const userInfoStr = localStorage.getItem('userInfo');
            if (userInfoStr) {
                try {
                    this.userInfo = JSON.parse(userInfoStr);
                } catch (e) {
                    console.error('解析用户信息失败', e);
                }
            }
        },
        methods: {
            handleSelect(key, keyPath) {
                console.log(key, keyPath);
            },
            handleCommand(command) {
                if (command === 'logout') {
                    this.handleLogout();
                }
            },
            async handleLogout() {
                try {
                    const token = localStorage.getItem('token');
                    await this.$http.post('http://127.0.0.1:5003/api/logout', {}, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                } catch (e) {
                    console.error('登出请求失败', e);
                }
                
                // 清除本地存储
                localStorage.removeItem('token');
                localStorage.removeItem('userInfo');
                
                this.$message.success('已退出登录');
                this.$router.push('/login');
            },
            triggerUpload() {
                this.$refs.fileInput.click();
            },
            handleFileChange(e) {
                const file = e.target.files[0];
                if (file) {
                    this.$emit('upload-file', file);
                    // 清空input，允许重复上传同名文件
                    e.target.value = '';
                }
            }
        }
    };
</script>
<style scoped>
    #Header {
        width: 100%;
        background-color: #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        padding: 0 20px;
        box-sizing: border-box;
    }

    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 60px;
        max-width: 1400px;
        margin: 0 auto;
    }

    .logo-title h1 {
        margin: 0;
        color: #21b3b9;
        font-size: 24px;
        letter-spacing: 2px;
        white-space: nowrap;
    }

    .nav-menu {
        flex: 1;
        margin: 0 40px;
        display: flex;
        justify-content: flex-end; /* 导航栏靠右显示 */
    }

    .el-menu-demo {
        border-bottom: none !important;
    }

    .user-info {
        display: flex;
        align-items: center;
    }
    
    .el-dropdown-link {
        cursor: pointer;
        color: #409EFF;
        display: flex;
        align-items: center;
    }
    
    .username {
        margin-left: 8px;
        font-size: 14px;
        color: #606266;
    }
</style>


