Page({
  data: {
    location: '杭州市 · 西湖区',
    categories: [
      { icon: '💡', name: '市政设施', color: 'mint' },
      { icon: '🛣️', name: '道路交通', color: 'yellow' },
      { icon: '♻️', name: '环境卫生', color: 'blue' },
      { icon: '🌳', name: '园林绿化', color: 'green' },
      { icon: '🛡️', name: '公共安全', color: 'purple' },
      { icon: '更多', name: '全部问题', color: 'plain' }
    ]
  },
  goReport() { wx.navigateTo({ url: '/pages/report/report' }) }
})
