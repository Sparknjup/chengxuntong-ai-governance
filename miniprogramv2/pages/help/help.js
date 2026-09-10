Page({ navigate(e) { wx.navigateTo({ url: e.currentTarget.dataset.url }) }, service() { wx.showToast({ title: '在线客服为静态预览', icon: 'none' }) } })
