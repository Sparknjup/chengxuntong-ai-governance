Page({
  data: { problems: [{icon:'▱',name:'道路出行',key:'road',tone:'blue'}, {icon:'✦',name:'市政设施',key:'facility',tone:'orange'}, {icon:'♧',name:'环境卫生',key:'sanitation',tone:'green'}, {icon:'⌂',name:'社区治理',key:'community',tone:'purple'}] },
  report(e) { const item = e.currentTarget.dataset.item || {}; wx.navigateTo({ url: `/pages/report/report?type=${item.key || 'facility'}` }) },
  goCategories() { wx.navigateTo({ url: '/pages/categories/categories' }) },
  goFeed() { wx.navigateTo({ url: '/pages/feed/feed' }) },
  goPoints() { wx.navigateTo({ url: '/pages/points/points' }) }
})
