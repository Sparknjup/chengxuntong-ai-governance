Page({
  data: {
    items: [
      { icon: '▱', name: '道路出行', key: 'road', desc: '路面、井盖、交通设施', tone: 'blue' },
      { icon: '✦', name: '市政设施', key: 'facility', desc: '路灯、护栏、公共设备', tone: 'orange' },
      { icon: '♧', name: '环境卫生', key: 'sanitation', desc: '垃圾、保洁、公共环境', tone: 'green' },
      { icon: '⌂', name: '社区治理', key: 'community', desc: '噪音、秩序、公共服务', tone: 'purple' },
      { icon: '♜', name: '园林绿化', key: 'garden', desc: '树木、绿地、景观设施', tone: 'green' },
      { icon: '!', name: '应急安全', key: 'safety', desc: '紧急隐患与安全问题', tone: 'orange' }
    ]
  },
  report(e) {
    const { key, name } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/report/report?type=${key}&name=${encodeURIComponent(name)}` })
  }
})
