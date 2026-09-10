const demoOrders = [
  { id: 1, status: '处理中', stateText: '部门处理中', date: '今天 09:42', title: '文一路路灯损坏', address: '西湖区文一路 100 号', icon: '✦', tone: 'light', progress: 58 },
  { id: 2, status: '已完成', stateText: '处理完成', date: '8 月 12 日', title: '小区垃圾清运不及时', address: '西湖区玉古路 12 号', icon: '♧', tone: 'clean', reward: 8 },
  { id: 3, status: '处理中', stateText: '已转交部门', date: '8 月 15 日', title: '人行道井盖松动', address: '西湖区学院路 68 号', icon: '▱', tone: 'road', progress: 34 },
  { id: 4, status: '已完成', stateText: '处理完成', date: '8 月 10 日', title: '社区绿化带枝叶遮挡', address: '西湖区教工路 32 号', icon: '♜', tone: 'clean', reward: 8 }
]

Page({
  data: { active: '全部', tabs: ['全部', '处理中', '已完成'], visibleOrders: demoOrders },
  filter(e) {
    const active = e.currentTarget.dataset.tab
    const visibleOrders = active === '全部' ? demoOrders : demoOrders.filter(item => item.status === active)
    this.setData({ active, visibleOrders })
  },
  detail(e) { wx.navigateTo({ url: `/pages/order-detail/order-detail?id=${e.currentTarget.dataset.id}` }) }
})
