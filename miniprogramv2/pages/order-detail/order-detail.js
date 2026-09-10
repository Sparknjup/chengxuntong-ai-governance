const details = {
  1: { no: 'CT2026081601', title: '文一路路灯损坏', status: '部门处理中', note: '已受理，预计 1 - 3 个工作日内处理', type: '市政设施 · 路灯故障', address: '西湖区文一路 100 号', time: '今天 09:42', department: '市政设施部门', step: '工作人员正在现场核查' },
  2: { no: 'CT2026081206', title: '小区垃圾清运不及时', status: '处理完成', note: '垃圾已完成清运并消毒', type: '环境卫生 · 清运延迟', address: '西湖区玉古路 12 号', time: '8 月 12 日 08:30', department: '环境卫生部门', step: '工单已完成并结案' },
  3: { no: 'CT2026081503', title: '人行道井盖松动', status: '已转交部门', note: '已设置临时警示标识', type: '道路出行 · 井盖异常', address: '西湖区学院路 68 号', time: '8 月 15 日 17:20', department: '道路管理部门', step: '维修人员已安排处理' },
  4: { no: 'CT2026081008', title: '社区绿化带枝叶遮挡', status: '处理完成', note: '遮挡枝叶已修剪', type: '园林绿化 · 枝叶遮挡', address: '西湖区教工路 32 号', time: '8 月 10 日 14:15', department: '园林绿化部门', step: '工单已完成并结案' }
}

Page({
  data: { detail: details[1] },
  onLoad(options) { this.setData({ detail: details[options.id] || details[1] }) },
  action() { wx.showToast({ title: this.data.detail.status === '处理完成' ? '感谢你的参与' : '催办提醒已记录', icon: 'none' }) }
})
