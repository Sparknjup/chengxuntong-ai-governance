Page({ data: { active: '全部', tabs: ['全部', '处理中', '已完成'] }, selectTab(e) { this.setData({ active: e.currentTarget.dataset.tab }) } })
