Page({
  data: { activeType: '市政设施', types: ['市政设施', '道路交通', '环境卫生', '园林绿化', '公共安全'] },
  selectType(e) { this.setData({ activeType: e.currentTarget.dataset.type }) },
  showSoon() { wx.showToast({ title: '提交功能即将开放', icon: 'none' }) }
})
