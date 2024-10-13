module.exports = {
  productionSourceMap: false,
  publicPath: process.env.NODE_ENV === 'production'
    ? '/static/cms/'
    : '/',
  devServer: {
    proxy: 'http://localhost:5000'
  }
}