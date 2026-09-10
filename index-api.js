(() => {
  'use strict'

  const API_BASE = location.protocol.startsWith('http') && location.port === '9000'
    ? location.origin
    : 'http://127.0.0.1:9000'
  const state = { role: null, adminOrders: [], citizenOrders: [] }

  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[char])
  const tokenKey = role => `cxt_${role}_token`
  const getToken = role => localStorage.getItem(tokenKey(role)) || ''
  const formatDate = value => value
    ? new Intl.DateTimeFormat('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }).format(new Date(value))
    : '—'

  async function api(path, { method = 'GET', body, role = state.role, auth = true } = {}) {
    const headers = { Accept: 'application/json' }
    if (auth && getToken(role)) headers.Authorization = `Bearer ${getToken(role)}`
    if (body && !(body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
      body = JSON.stringify(body)
    }
    const response = await fetch(`${API_BASE}${path}`, { method, headers, body })
    let payload
    try { payload = await response.json() } catch { payload = null }
    if (!response.ok || !payload?.success) {
      if (response.status === 401 && role) localStorage.removeItem(tokenKey(role))
      const details = Array.isArray(payload?.data) ? payload.data.map(item => item.msg).join('；') : ''
      throw new Error(details || payload?.message || `请求失败（${response.status}）`)
    }
    return payload.data
  }

  const toast = document.getElementById('toast')
  let toastTimer
  function showToast(message) {
    toast.textContent = message
    toast.classList.add('show')
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => toast.classList.remove('show'), 3200)
  }

  function installStyles() {
    const style = document.createElement('style')
    style.textContent = `
      .auth-backdrop{position:fixed;inset:0;z-index:100;background:rgba(10,32,36,.72);display:grid;place-items:center;padding:20px;backdrop-filter:blur(8px)}
      .auth-card{width:min(430px,100%);background:#fff;border-radius:22px;padding:27px;box-shadow:0 28px 80px rgba(0,0,0,.28)}
      .auth-card h2{margin:7px 0 5px;font-size:23px}.auth-card>p{margin:0 0 20px;color:var(--muted);font-size:12px;line-height:1.6}
      .auth-tabs{display:flex;gap:8px;margin-bottom:15px}.auth-tabs button{flex:1;border:1px solid var(--line);background:#f6f8f5;padding:9px;border-radius:10px;color:var(--muted)}
      .auth-tabs button.active{color:#fff;background:var(--teal);border-color:var(--teal)}.auth-form{display:grid;gap:12px}.auth-form .btn{padding:12px}
      .auth-error{min-height:18px;color:var(--red);font-size:11px}.auth-hint{margin-top:14px;color:var(--muted);font-size:10px;line-height:1.6}
      .session-action{margin-left:auto;border:0;background:transparent;color:var(--teal);font-size:10px;padding:6px}.live-empty{padding:28px;text-align:center;color:var(--muted);font-size:11px}
      .live-orders{display:grid;gap:10px}.live-order{cursor:pointer}.live-order:hover{border-color:#92b8ad}.live-order .journey{margin-top:12px}
      .upload-zone input{display:block;width:100%;margin-top:9px;font-size:10px}.api-badge{display:inline-flex;align-items:center;gap:5px;color:var(--green);font-size:10px}
      .api-badge:before{content:'';width:6px;height:6px;border-radius:50%;background:currentColor}.point-history{display:grid;gap:0}.point-item{display:flex;justify-content:space-between;gap:16px;padding:11px 0;border-bottom:1px solid var(--line)}
      .point-item:last-child{border:0}.point-item b{font-size:10px}.point-item small{display:block;color:var(--muted);font-size:9px;margin-top:4px}.point-item strong{color:var(--teal);font-size:12px}
      .drawer textarea,.drawer select{width:100%;border:1px solid var(--line);border-radius:10px;padding:10px;margin-top:7px;font:inherit}.drawer .field{margin-top:12px}
      @media(max-width:760px){.auth-card{padding:21px}.live-order .journey{grid-template-columns:repeat(2,1fr)}}
    `
    document.head.appendChild(style)
  }

  function installAuthModal() {
    const modal = document.createElement('div')
    modal.id = 'auth-modal'
    modal.className = 'auth-backdrop hidden'
    modal.innerHTML = `
      <div class="auth-card">
        <div class="kicker">SECURE ACCESS</div>
        <h2 id="auth-title">登录城讯通</h2>
        <p id="auth-copy">登录后使用真实后端数据。</p>
        <div class="auth-tabs" id="auth-tabs"><button type="button" data-mode="login" class="active">登录</button><button type="button" data-mode="register">注册</button></div>
        <form class="auth-form" id="auth-form">
          <div class="field hidden" id="auth-name-wrap"><label for="auth-name">姓名</label><input id="auth-name" autocomplete="name" placeholder="请输入姓名"></div>
          <div class="field"><label for="auth-account" id="auth-account-label">手机号</label><input id="auth-account" autocomplete="username" required placeholder="请输入手机号"></div>
          <div class="field"><label for="auth-password">密码</label><input id="auth-password" type="password" autocomplete="current-password" minlength="6" required placeholder="至少 6 位"></div>
          <div class="auth-error" id="auth-error"></div>
          <button class="btn primary" id="auth-submit" type="submit">登录</button>
        </form>
        <div class="auth-hint" id="auth-hint"></div>
      </div>`
    document.body.appendChild(modal)
    modal.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => setAuthMode(button.dataset.mode)))
    modal.querySelector('#auth-form').addEventListener('submit', submitAuth)
  }

  function setAuthMode(mode) {
    const citizen = state.role === 'citizen'
    const actualMode = citizen ? mode : 'login'
    document.querySelectorAll('#auth-tabs [data-mode]').forEach(button => button.classList.toggle('active', button.dataset.mode === actualMode))
    document.getElementById('auth-name-wrap').classList.toggle('hidden', actualMode !== 'register')
    document.getElementById('auth-submit').textContent = actualMode === 'register' ? '注册并登录' : '登录'
    document.getElementById('auth-form').dataset.mode = actualMode
    document.getElementById('auth-error').textContent = ''
  }

  function showAuth(role, message = '') {
    state.role = role
    const citizen = role === 'citizen'
    document.getElementById('auth-title').textContent = citizen ? '市民登录' : '管理员登录'
    document.getElementById('auth-copy').textContent = citizen ? '登录后可上报问题、查看进度和文明积分。' : '登录后加载真实治理统计和工单队列。'
    document.getElementById('auth-tabs').classList.toggle('hidden', !citizen)
    document.getElementById('auth-account-label').textContent = citizen ? '手机号' : '管理员用户名'
    document.getElementById('auth-account').placeholder = citizen ? '请输入手机号' : '请输入管理员用户名'
    document.getElementById('auth-account').value = citizen ? '' : 'admin'
    document.getElementById('auth-password').value = ''
    document.getElementById('auth-error').textContent = message
    document.getElementById('auth-hint').textContent = citizen ? '首次使用请点击“注册”。' : '默认初始化管理员用户名为 admin；密码请使用初始化时设置的密码。'
    setAuthMode('login')
    document.getElementById('auth-modal').classList.remove('hidden')
    setTimeout(() => document.getElementById('auth-account').focus(), 50)
  }

  function closeAuth() { document.getElementById('auth-modal').classList.add('hidden') }

  async function submitAuth(event) {
    event.preventDefault()
    const button = document.getElementById('auth-submit')
    const error = document.getElementById('auth-error')
    const account = document.getElementById('auth-account').value.trim()
    const password = document.getElementById('auth-password').value
    const mode = event.currentTarget.dataset.mode || 'login'
    error.textContent = ''
    button.disabled = true
    button.textContent = '正在连接…'
    try {
      if (state.role === 'admin') {
        const data = await api('/api/admins/login', { method: 'POST', body: { username: account, password }, auth: false, role: 'admin' })
        localStorage.setItem(tokenKey('admin'), data.access_token)
      } else {
        if (mode === 'register') {
          const name = document.getElementById('auth-name').value.trim()
          if (name.length < 2) throw new Error('姓名至少需要 2 个字符')
          await api('/api/users/register', { method: 'POST', body: { name, phone: account, password }, auth: false, role: 'citizen' })
        }
        const data = await api('/api/users/login', { method: 'POST', body: { phone: account, password }, auth: false, role: 'citizen' })
        localStorage.setItem(tokenKey('citizen'), data.access_token)
      }
      closeAuth()
      showToast('登录成功，已连接真实后端')
      await loadRole(state.role)
    } catch (err) {
      error.textContent = err.message
    } finally {
      button.disabled = false
      button.textContent = mode === 'register' && state.role === 'citizen' ? '注册并登录' : '登录'
    }
  }

  function installSessionActions() {
    document.querySelectorAll('.side-foot').forEach(footer => {
      const button = document.createElement('button')
      button.className = 'session-action'
      button.textContent = '退出'
      button.addEventListener('click', () => {
        localStorage.removeItem(tokenKey(state.role))
        showAuth(state.role, '已退出当前账号')
      })
      footer.appendChild(button)
    })
  }

  async function switchRole(role, smooth = true) {
    state.role = role
    document.querySelectorAll('[data-role-switch]').forEach(button => button.classList.toggle('active', button.dataset.roleSwitch === role))
    document.querySelectorAll('[data-role]').forEach(shell => shell.classList.toggle('hidden', shell.dataset.role !== role))
    if (smooth) window.scrollTo({ top: 0, behavior: 'smooth' })
    if (!getToken(role)) {
      showAuth(role)
      return
    }
    try { await loadRole(role) } catch (err) { showAuth(role, err.message) }
  }

  const statusLabel = status => ({ '待处理': '等待受理', '处理中': '现场处理中', '已结案': '处理完成', '已驳回': '已驳回' })[status] || status
  const statusClass = status => status === '已结案' ? 'good' : status === '已驳回' ? 'risk' : 'warn'

  async function loadRole(role) {
    if (role === 'admin') return loadAdmin()
    return loadCitizen()
  }

  async function loadAdmin() {
    const [overview, orders, me] = await Promise.all([
      api('/api/stats/overview', { role: 'admin' }),
      api('/api/orders/?page_size=20', { role: 'admin' }),
      api('/api/admins/me', { role: 'admin' })
    ])
    state.adminOrders = orders.items
    const metrics = [
      ['工单总量', overview.total_orders, `${overview.pending} 条待处理 · ${overview.processing} 条处理中`],
      ['办结率', overview.close_rate, `${overview.closed} 条已结案`],
      ['紧急事项', overview.urgent, '需优先核查与处置'],
      ['平均评分', overview.avg_rating || '—', `${overview.total_users} 位注册市民`]
    ]
    document.querySelectorAll('#admin-overview .metric').forEach((card, index) => {
      card.querySelector('.metric-label').textContent = metrics[index][0]
      card.querySelector('.metric-value').textContent = metrics[index][1]
      card.querySelector('.metric-foot').textContent = metrics[index][2]
    })
    const account = document.querySelector('.admin-shell .side-foot')
    account.querySelector('b').textContent = me.real_name || me.username
    account.querySelector('small').textContent = `${me.role} · API 在线`
    account.querySelector('.avatar').textContent = (me.real_name || me.username).slice(0, 1)
    renderAdminOrders(orders.items, orders.total)
    const quality = document.querySelector('#admin-quality .score-ring strong')
    if (quality) quality.textContent = overview.avg_rating ? (overview.avg_rating * 20).toFixed(1) : '—'
  }

  function adminOrderCard(order) {
    return `<div class="case" data-live-order-id="${order.id}"><div class="case-icon">${order.urgency === '紧急' ? '急' : '单'}</div><div><b>${escapeHtml(order.problem_type)} · ${escapeHtml(order.location)}</b><p>${escapeHtml(order.order_no)} · ${escapeHtml(order.department_name || '待分派')} · ${formatDate(order.created_at)}</p></div><div class="case-meta"><strong>${escapeHtml(statusLabel(order.status))}</strong><small>${escapeHtml(order.urgency)}</small></div></div>`
  }

  function renderAdminOrders(orders, total) {
    const list = document.querySelector('#admin-cases .case-list')
    const primary = orders.find(item => item.urgency === '紧急' && item.status !== '已结案') || orders[0]
    const priority = document.querySelector('#admin-cases .priority')
    document.querySelector('#admin-cases .link-btn').textContent = `全部 ${total} 条 →`
    if (!primary) {
      priority.innerHTML = '<div class="live-empty">暂无工单，等待市民上报。</div>'
      list.innerHTML = ''
      return
    }
    priority.dataset.liveOrderId = primary.id
    priority.innerHTML = `<div class="priority-top"><span class="pill ${statusClass(primary.status)}">${escapeHtml(primary.urgency)}</span><h3>${escapeHtml(primary.problem_type)} · ${escapeHtml(primary.location)}</h3></div><p>${escapeHtml(primary.order_no)} · ${escapeHtml(primary.department_name || '待分派')} · ${escapeHtml(statusLabel(primary.status))}</p><div class="evidence"><span>真实数据库工单</span><span>${formatDate(primary.created_at)}</span><span>${escapeHtml(primary.urgency)}优先级</span></div><div class="head-actions" style="margin-top:13px"><button class="btn primary sm" data-live-order-id="${primary.id}">查看并处理</button></div>`
    list.innerHTML = orders.filter(item => item.id !== primary.id).slice(0, 6).map(adminOrderCard).join('')
  }

  async function openAdminOrder(id) {
    try {
      const order = await api(`/api/orders/${id}`, { role: 'admin' })
      const drawer = document.getElementById('drawer-backdrop')
      drawer.querySelector('.drawer').innerHTML = `
        <div class="drawer-head"><div><div class="kicker">LIVE ORDER</div><h2>工单处理</h2></div><button class="close" id="drawer-close">×</button></div>
        <div class="detail-block"><h3>${escapeHtml(order.problem_type)} · ${escapeHtml(order.location)}</h3><div class="detail-grid"><div>工单编号<b>${escapeHtml(order.order_no)}</b></div><div>紧急程度<b>${escapeHtml(order.urgency)}</b></div><div>当前状态<b>${escapeHtml(statusLabel(order.status))}</b></div><div>受理部门<b>${escapeHtml(order.department_name || '待分派')}</b></div></div></div>
        <div class="detail-block"><h3>市民描述</h3><div class="reasoning">${escapeHtml(order.description || '未提供文字说明')}</div></div>
        <form id="status-form"><div class="field"><label for="order-status">更新状态</label><select id="order-status"><option value="处理中">处理中</option><option value="已结案">已结案</option><option value="已驳回">已驳回</option></select></div><div class="field"><label for="order-result">处理结果说明</label><textarea id="order-result" rows="4" placeholder="填写现场处理情况">${escapeHtml(order.result_description || '')}</textarea></div><div class="head-actions" style="margin-top:16px"><button class="btn primary" type="submit">保存处理结果</button></div></form>`
      drawer.classList.add('open')
      document.getElementById('drawer-close').addEventListener('click', () => drawer.classList.remove('open'))
      document.getElementById('status-form').addEventListener('submit', async event => {
        event.preventDefault()
        const data = { status: document.getElementById('order-status').value, result_description: document.getElementById('order-result').value.trim() || null }
        try {
          await api(`/api/orders/${id}/status`, { method: 'PUT', body: data, role: 'admin' })
          drawer.classList.remove('open')
          showToast('工单状态已更新')
          await loadAdmin()
        } catch (err) { showToast(err.message) }
      })
    } catch (err) { showToast(err.message) }
  }

  async function loadCitizen() {
    const [me, orders, points] = await Promise.all([
      api('/api/users/me', { role: 'citizen' }),
      api('/api/orders/my?page_size=20', { role: 'citizen' }),
      api('/api/points/my?page_size=20', { role: 'citizen' })
    ])
    state.citizenOrders = orders.items
    document.querySelector('.citizen-shell .side-context b').textContent = `你好，${me.name}`
    const account = document.querySelector('.citizen-shell .side-foot')
    account.querySelector('b').textContent = me.name
    account.querySelector('small').textContent = `${me.level} · ${me.points} 分`
    account.querySelector('.avatar').textContent = me.name.slice(0, 1)
    document.querySelector('.citizen-score strong').textContent = me.points.toLocaleString('zh-CN')
    document.querySelector('.citizen-score small:last-child').textContent = `累计提交 ${orders.total} 条共治事项`
    renderCitizenOrders(orders.items)
    renderCitizenPoints(points)
  }

  function renderCitizenOrders(orders) {
    const section = document.getElementById('citizen-orders')
    section.innerHTML = `<div class="card-head"><div><div class="card-title">我的问题正在怎样处理</div><div class="card-sub">以下内容来自真实后端工单数据</div></div><span class="api-badge">已连接 API</span></div><div class="live-orders">${orders.length ? orders.slice(0, 6).map(order => `
      <div class="priority live-order" data-citizen-order-id="${order.id}" style="border-left-color:${order.urgency === '紧急' ? '#c65348' : '#e5a836'}"><div class="priority-top"><span class="pill ${statusClass(order.status)}">${escapeHtml(statusLabel(order.status))}</span><h3>${escapeHtml(order.order_no)} · ${escapeHtml(order.problem_type)}</h3></div><p>${escapeHtml(order.location)} · ${escapeHtml(order.department_name || '等待分派')} · ${formatDate(order.created_at)}</p><div class="journey"><div class="journey-step done"><b>已提交</b><small>${formatDate(order.created_at)}<br>基础积分 +5</small></div><div class="journey-step done"><b>AI 已识别</b><small>${escapeHtml(order.problem_type)}<br>${escapeHtml(order.urgency)}</small></div><div class="journey-step ${order.status !== '待处理' ? 'done' : 'current'}"><b>部门受理</b><small>${escapeHtml(order.department_name || '等待匹配')}</small></div><div class="journey-step ${order.status === '处理中' ? 'current' : order.status === '已结案' ? 'done' : ''}"><b>现场处理</b><small>${escapeHtml(statusLabel(order.status))}</small></div><div class="journey-step ${order.status === '已结案' ? 'done' : ''}"><b>处理完成</b><small>${order.status === '已结案' ? '结果已反馈' : '等待办理'}</small></div><div class="journey-step ${order.rating ? 'done' : ''}"><b>我的评价</b><small>${order.rating ? `${order.rating} 星` : '结案后可评价'}</small></div></div></div>`).join('') : '<div class="live-empty">暂无工单。填写上方信息，提交第一条城市问题。</div>'}</div>`
  }

  function renderCitizenPoints(points) {
    const section = document.getElementById('citizen-points')
    section.innerHTML = `
      <div class="card reward-card"><div class="card-head"><div><div class="card-title">我的文明贡献</div><div class="card-sub">积分和等级来自后端账户</div></div><span class="pill good">${escapeHtml(points.level)}</span></div><div class="points">${Number(points.total_points).toLocaleString('zh-CN')} <small style="font-size:11px">分</small></div><div class="result-note" style="margin-top:20px">有效上报、工单结案与五星评价会自动写入积分明细。</div></div>
      <div class="card"><div class="card-head"><div><div class="card-title">最近积分明细</div><div class="card-sub">共 ${points.total} 条记录</div></div><span class="api-badge">实时</span></div><div class="point-history">${points.items.length ? points.items.slice(0, 8).map(item => `<div class="point-item"><div><b>${escapeHtml(item.reason)}</b><small>${formatDate(item.created_at)}</small></div><strong>${item.points > 0 ? '+' : ''}${item.points}</strong></div>`).join('') : '<div class="live-empty">暂无积分记录</div>'}</div></div>`
  }

  async function openCitizenOrder(id) {
    try {
      const order = await api(`/api/orders/${id}`, { role: 'citizen' })
      const drawer = document.getElementById('drawer-backdrop')
      const canRate = order.status === '已结案' && !order.rating
      drawer.querySelector('.drawer').innerHTML = `
        <div class="drawer-head"><div><div class="kicker">MY ORDER</div><h2>工单详情</h2></div><button class="close" id="drawer-close">×</button></div>
        <div class="detail-block"><h3>${escapeHtml(order.problem_type)}</h3><div class="detail-grid"><div>工单编号<b>${escapeHtml(order.order_no)}</b></div><div>当前状态<b>${escapeHtml(statusLabel(order.status))}</b></div><div>受理部门<b>${escapeHtml(order.department_name || '等待分派')}</b></div><div>提交时间<b>${formatDate(order.created_at)}</b></div></div></div>
        <div class="detail-block"><h3>问题与处理结果</h3><div class="reasoning">${escapeHtml(order.description || '—')}<br><br>处理反馈：${escapeHtml(order.result_description || '暂未反馈')}</div></div>
        ${canRate ? '<form id="rate-form"><div class="field"><label for="rate-value">服务评价</label><select id="rate-value"><option value="5">5 星 · 非常满意</option><option value="4">4 星 · 满意</option><option value="3">3 星 · 一般</option><option value="2">2 星 · 待改进</option><option value="1">1 星 · 不满意</option></select></div><div class="field"><label for="rate-comment">评价说明</label><textarea id="rate-comment" rows="3" maxlength="200"></textarea></div><button class="btn primary" style="margin-top:14px" type="submit">提交评价</button></form>' : `<div class="result-note">${order.rating ? `已评价：${order.rating} 星` : '工单结案后可评价'}</div>`}`
      drawer.classList.add('open')
      document.getElementById('drawer-close').addEventListener('click', () => drawer.classList.remove('open'))
      document.getElementById('rate-form')?.addEventListener('submit', async event => {
        event.preventDefault()
        try {
          await api(`/api/orders/${id}/rate`, { method: 'POST', body: { rating: Number(document.getElementById('rate-value').value), comment: document.getElementById('rate-comment').value.trim() || null }, role: 'citizen' })
          drawer.classList.remove('open')
          showToast('评价已提交')
          await loadCitizen()
        } catch (err) { showToast(err.message) }
      })
    } catch (err) { showToast(err.message) }
  }

  function prepareReportForm() {
    const zone = document.querySelector('#report-form .upload-zone')
    zone.innerHTML = '<b>＋ 添加一份现场照片 / 视频 / 语音</b><span>支持 jpg、png、webp、mp3、wav、mp4、avi、mov</span><input id="report-media" type="file" accept="image/jpeg,image/png,image/webp,audio/mpeg,audio/wav,video/mp4,video/quicktime,video/x-msvideo">'
    document.getElementById('analyze-btn').textContent = '提交并由 AI 识别 →'
    document.querySelector('#citizen-report .page-head p').textContent = '提交后由 AI 整理事实、判断紧急程度并匹配受理部门。'
    const draft = JSON.parse(localStorage.getItem('cxt_report_draft') || 'null')
    if (draft) {
      document.getElementById('description').value = draft.description || ''
      document.getElementById('location').value = draft.location || ''
      localStorage.removeItem('cxt_report_draft')
    }
  }

  async function submitCitizenReport() {
    if (!getToken('citizen')) return showAuth('citizen')
    const description = document.getElementById('description').value.trim()
    const locationValue = document.getElementById('location').value.trim()
    const file = document.getElementById('report-media').files[0]
    if (!locationValue) return showToast('请填写发生地点')
    if (!description && !file) return showToast('请填写问题描述或添加现场资料')
    const button = document.getElementById('analyze-btn')
    const form = new FormData()
    form.append('location', locationValue)
    if (description) form.append('text', description)
    if (file) {
      const field = file.type.startsWith('image/') ? 'image' : file.type.startsWith('audio/') ? 'audio' : 'video'
      form.append(field, file)
    }
    button.disabled = true
    button.textContent = 'AI 正在识别并生成工单…'
    try {
      const result = await api('/api/orders/report', { method: 'POST', body: form, role: 'citizen' })
      document.getElementById('scan-empty').classList.add('hidden')
      const panel = document.getElementById('scan-result')
      panel.classList.remove('hidden')
      panel.innerHTML = `<div class="result-row"><span>工单编号</span><b>${escapeHtml(result.order_no)}</b></div><div class="result-row"><span>识别问题</span><b>${escapeHtml(result.problem_type)}</b></div><div class="result-row"><span>建议受理</span><b>${escapeHtml(result.department || '待人工分派')}</b></div><div class="result-row"><span>紧急程度</span><b>${escapeHtml(result.urgency)}</b></div><div class="result-note">工单已写入后端数据库，获得基础积分 +${result.points_gained}，当前积分 ${result.current_points}。</div><button class="btn primary" type="button" id="view-live-orders">查看真实办理进度</button>`
      document.getElementById('view-live-orders').addEventListener('click', () => document.getElementById('citizen-orders').scrollIntoView({ behavior: 'smooth' }))
      showToast(`工单 ${result.order_no} 已生成`)
      document.getElementById('report-form').reset()
      await loadCitizen()
    } catch (err) {
      showToast(err.message)
      if (!getToken('citizen')) showAuth('citizen', '登录已过期，请重新登录')
    } finally {
      button.disabled = false
      button.textContent = '提交并由 AI 识别 →'
    }
  }

  function bindEvents() {
    document.querySelectorAll('[data-role-switch]').forEach(button => button.addEventListener('click', () => switchRole(button.dataset.roleSwitch)))
    document.querySelectorAll('[data-scroll]').forEach(button => button.addEventListener('click', () => {
      const element = document.getElementById(button.dataset.scroll)
      if (element) element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }))
    document.querySelectorAll('[data-action="show-toast"]').forEach(button => button.addEventListener('click', () => showToast(button.dataset.message)))
    document.querySelectorAll('[data-action="redeem"]').forEach(button => button.addEventListener('click', () => showToast('积分兑换功能暂未开放')))
    document.querySelector('[data-action="save-draft"]').addEventListener('click', () => {
      localStorage.setItem('cxt_report_draft', JSON.stringify({ description: document.getElementById('description').value, location: document.getElementById('location').value }))
      showToast('草稿已保存到当前浏览器')
    })
    document.getElementById('analyze-btn').addEventListener('click', submitCitizenReport)
    document.getElementById('admin-cases').addEventListener('click', event => {
      const target = event.target.closest('[data-live-order-id]')
      if (target) openAdminOrder(target.dataset.liveOrderId)
    })
    document.getElementById('citizen-orders').addEventListener('click', event => {
      const target = event.target.closest('[data-citizen-order-id]')
      if (target) openCitizenOrder(target.dataset.citizenOrderId)
    })
    document.getElementById('drawer-backdrop').addEventListener('click', event => {
      if (event.target === event.currentTarget) event.currentTarget.classList.remove('open')
    })
  }

  function updateClock() {
    const date = new Date()
    const pad = number => String(number).padStart(2, '0')
    document.getElementById('clock').textContent = `${date.getFullYear()}.${pad(date.getMonth() + 1)}.${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  }

  installStyles()
  installAuthModal()
  installSessionActions()
  prepareReportForm()
  bindEvents()
  updateClock()
  setInterval(updateClock, 1000)
  const requestedRole = new URLSearchParams(location.search).get('role') === 'citizen' ? 'citizen' : 'admin'
  switchRole(requestedRole, false)
})()
