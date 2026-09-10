const categoryProfiles = {
  road: { name: '道路出行', icon: '▱', department: '道路管理部门', types: ['路面破损', '井盖异常', '交通标线', '道路积水'], hint: '请拍摄道路全景和具体破损位置', placeholder: '例如：文一路东向西车道出现明显坑洼，影响车辆通行。' },
  facility: { name: '市政设施', icon: '✦', department: '市政设施部门', types: ['路灯故障', '护栏损坏', '公共座椅', '其他设施'], hint: '请拍摄设施编号或周边明显参照物', placeholder: '例如：小区北门路灯不亮，编号为 XH-028。' },
  sanitation: { name: '环境卫生', icon: '♧', department: '环境卫生部门', types: ['垃圾堆放', '清运延迟', '污水外溢', '公共保洁'], hint: '请描述污染范围和持续时间', placeholder: '例如：垃圾投放点两天未清运，已有明显异味。' },
  community: { name: '社区治理', icon: '⌂', department: '属地街道与社区', types: ['噪音扰民', '占道经营', '公共秩序', '物业服务'], hint: '请说明发生时段及对居民的影响', placeholder: '例如：沿街商铺连续多晚施工，持续至晚上十一点。' },
  garden: { name: '园林绿化', icon: '♜', department: '园林绿化部门', types: ['树木倒伏', '绿地损坏', '枝叶遮挡', '景观设施'], hint: '请拍摄树木、绿地与道路的位置关系', placeholder: '例如：行道树枝叶遮挡交通标志，存在安全隐患。' },
  safety: { name: '应急安全', icon: '!', department: '城市应急联动中心', types: ['消防隐患', '燃气异常', '坠落风险', '其他险情'], hint: '如有人身危险请先拨打 110、119 或 120', placeholder: '例如：外墙构件松动，有坠落风险，请尽快排查。' }
}

Page({
  data: { profile: categoryProfiles.facility, selected: '路灯故障' },
  onLoad(options) {
    const profile = categoryProfiles[options.type] || categoryProfiles.facility
    this.setData({ profile, selected: profile.types[0] })
    wx.setNavigationBarTitle({ title: `${profile.name}上报` })
  },
  choose(e) { this.setData({ selected: e.currentTarget.dataset.value }) },
  submit() { wx.navigateTo({ url: `/pages/report-success/report-success?type=${encodeURIComponent(this.data.profile.name)}` }) }
})
