module.exports = {
  publicPath: '/',
  // 启用并行构建，加快构建速度（多核 CPU 默认为 true）
  parallel: true,
  // 生产环境关闭 source map，减小包体积
  productionSourceMap: false,
  devServer: {
    historyApiFallback: true,
    port: 8080
  }
}
