(() => {
  'use strict'

  const API_BASE = location.protocol.startsWith('http') ? location.origin : 'http://127.0.0.1:9000'
  const tokenKey = 'cxt_citizen_token'
  const form = document.getElementById('report-form')
  const note = document.querySelector('.drawer-note')
  const reportBackdrop = document.getElementById('report-backdrop')
  const mediaButtons = [...form.querySelectorAll('.media-options button')]
  let selectedFile = null
  let continueToReport = false

  function installAuthDialog() {
    const style = document.createElement('style')
    style.textContent = `
      .home-auth-backdrop{position:fixed;inset:0;z-index:120;display:grid;place-items:center;padding:20px;background:rgba(3,31,41,.72);backdrop-filter:blur(9px);opacity:0;visibility:hidden;transition:.25s}
      .home-auth-backdrop.open{opacity:1;visibility:visible}.home-auth-card{width:min(430px,100%);padding:30px;background:#f7faf8;color:#073746;box-shadow:0 30px 90px rgba(0,0,0,.3)}
      .home-auth-top{display:flex;justify-content:space-between;align-items:start}.home-auth-top h2{margin:7px 0 4px;font:700 31px/1.2 Georgia,'Songti SC',serif}.home-auth-close{width:38px;height:38px;border:0;background:#073746;color:#fff;font-size:22px}
      .home-auth-copy{margin:0 0 20px;color:#6f8382;font-size:12px;line-height:1.7}.home-auth-tabs{display:flex;gap:7px;margin-bottom:16px}.home-auth-tabs button{flex:1;border:1px solid #c9d8d4;background:#fff;padding:10px;color:#637a78;font-weight:700}.home-auth-tabs button.active{border-color:#05869a;background:#05869a;color:#fff}
      .home-auth-form{display:grid;gap:13px}.home-auth-form label{display:block;margin-bottom:7px;font-size:10px;font-weight:800}.home-auth-form input{width:100%;border:1px solid #cad8d5;background:#fff;padding:13px;outline:none}.home-auth-form input:focus{border-color:#05869a;box-shadow:0 0 0 3px rgba(5,134,154,.1)}
      .home-auth-submit{border:0;background:#05869a;color:#fff;padding:14px;font-weight:800}.home-auth-error{min-height:17px;color:#b8463c;font-size:11px}.home-auth-hint{margin-top:13px;color:#718482;font-size:10px;line-height:1.6}.home-auth-hidden{display:none!important}
    `
    document.head.appendChild(style)

    const dialog = document.createElement('div')
    dialog.id = 'home-auth-dialog'
    dialog.className = 'home-auth-backdrop'
    dialog.innerHTML = `
      <section class="home-auth-card" role="dialog" aria-modal="true" aria-labelledby="home-auth-title">
        <div class="home-auth-top"><div><span class="eyebrow" style="color:#05869a">CITIZEN ACCOUNT</span><h2 id="home-auth-title">市民注册</h2></div><button class="home-auth-close" type="button" aria-label="关闭">×</button></div>
        <p class="home-auth-copy">注册或登录后即可提交问题、查询办理进度和文明积分。</p>
        <div class="home-auth-tabs"><button type="button" data-home-auth-mode="login">登录</button><button type="button" data-home-auth-mode="register" class="active">注册</button></div>
        <form class="home-auth-form" id="home-auth-form">
          <div id="home-auth-name-wrap"><label for="home-auth-name">姓名</label><input id="home-auth-name" autocomplete="name" placeholder="请输入姓名"></div>
          <div><label for="home-auth-phone">手机号</label><input id="home-auth-phone" inputmode="tel" autocomplete="username" required placeholder="请输入手机号"></div>
          <div><label for="home-auth-password">密码</label><input id="home-auth-password" type="password" minlength="6" autocomplete="new-password" required placeholder="至少 6 位"></div>
          <div class="home-auth-error" id="home-auth-error"></div>
          <button class="home-auth-submit" id="home-auth-submit" type="submit">注册并登录</button>
        </form>
        <div class="home-auth-hint">账号信息仅用于本项目的用户认证和工单归属。</div>
      </section>`
    document.body.appendChild(dialog)

    dialog.querySelector('.home-auth-close').addEventListener('click', closeAuth)
    dialog.addEventListener('click', event => { if (event.target === dialog) closeAuth() })
    dialog.querySelectorAll('[data-home-auth-mode]').forEach(button => button.addEventListener('click', () => setAuthMode(button.dataset.homeAuthMode)))
    dialog.querySelector('#home-auth-form').addEventListener('submit', submitAuth)
  }

  function setAuthMode(mode) {
    const register = mode === 'register'
    document.getElementById('home-auth-form').dataset.mode = mode
    document.getElementById('home-auth-title').textContent = register ? '市民注册' : '市民登录'
    document.getElementById('home-auth-name-wrap').classList.toggle('home-auth-hidden', !register)
    document.getElementById('home-auth-password').autocomplete = register ? 'new-password' : 'current-password'
    document.getElementById('home-auth-submit').textContent = register ? '注册并登录' : '登录'
    document.getElementById('home-auth-error').textContent = ''
    document.querySelectorAll('[data-home-auth-mode]').forEach(button => button.classList.toggle('active', button.dataset.homeAuthMode === mode))
  }

  function showAuth(mode = 'register', shouldContinue = false, message = '') {
    continueToReport = shouldContinue
    setAuthMode(mode)
    document.getElementById('home-auth-error').textContent = message
    document.getElementById('home-auth-dialog').classList.add('open')
    setTimeout(() => document.getElementById(mode === 'register' ? 'home-auth-name' : 'home-auth-phone').focus(), 50)
  }

  function closeAuth() { document.getElementById('home-auth-dialog').classList.remove('open') }

  async function request(path, body) {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    const payload = await response.json()
    if (!response.ok || !payload.success) {
      const error = new Error(payload.message || '请求失败')
      error.status = response.status
      throw error
    }
    return payload.data
  }

  async function submitAuth(event) {
    event.preventDefault()
    const mode = event.currentTarget.dataset.mode || 'register'
    const phone = document.getElementById('home-auth-phone').value.trim()
    const password = document.getElementById('home-auth-password').value
    const name = document.getElementById('home-auth-name').value.trim()
    const errorBox = document.getElementById('home-auth-error')
    const button = document.getElementById('home-auth-submit')
    errorBox.textContent = ''
    button.disabled = true
    button.textContent = '正在连接…'
    try {
      if (mode === 'register') {
        if (name.length < 2) throw new Error('姓名至少需要 2 个字符')
        await request('/api/users/register', { name, phone, password })
      }
      const data = await request('/api/users/login', { phone, password })
      localStorage.setItem(tokenKey, data.access_token)
      closeAuth()
      if (continueToReport) openReportDrawer()
      else location.href = 'index.html?role=citizen'
    } catch (error) {
      errorBox.textContent = error.message
    } finally {
      button.disabled = false
      button.textContent = mode === 'register' ? '注册并登录' : '登录'
    }
  }

  function openReportDrawer() {
    document.body.classList.remove('menu-open')
    document.body.classList.add('drawer-open')
    reportBackdrop.classList.add('open')
    setTimeout(() => document.getElementById('report-location').focus(), 350)
  }

  installAuthDialog()

  document.querySelectorAll('[data-auth-mode]').forEach(button => button.addEventListener('click', event => {
    event.preventDefault()
    document.body.classList.remove('menu-open')
    showAuth(button.dataset.authMode)
  }))

  document.addEventListener('click', event => {
    const trigger = event.target.closest('[data-open-report]')
    if (!trigger || localStorage.getItem(tokenKey)) return
    event.preventDefault()
    event.stopImmediatePropagation()
    showAuth('register', true)
  }, true)

  const input = document.createElement('input')
  input.type = 'file'
  input.hidden = true
  form.appendChild(input)

  const mediaTypes = [
    'image/jpeg,image/png,image/webp',
    'audio/mpeg,audio/wav',
    'video/mp4,video/quicktime,video/x-msvideo'
  ]
  mediaButtons.slice(0, 3).forEach((button, index) => button.addEventListener('click', () => {
    input.accept = mediaTypes[index]
    input.click()
  }))
  mediaButtons[3]?.addEventListener('click', () => document.getElementById('report-description').focus())
  input.addEventListener('change', () => {
    selectedFile = input.files[0] || null
    if (selectedFile) note.textContent = `已选择现场资料：${selectedFile.name}。提交后将由 AI 识别并生成真实工单。`
  })

  form.addEventListener('submit', async event => {
    event.preventDefault()
    const locationValue = document.getElementById('report-location').value.trim()
    const description = document.getElementById('report-description').value.trim()
    const token = localStorage.getItem(tokenKey)
    if (!token) {
      showAuth('register', true)
      return
    }

    const button = form.querySelector('.report-submit')
    const body = new FormData()
    body.append('location', locationValue)
    if (description) body.append('text', description)
    if (selectedFile) {
      const field = selectedFile.type.startsWith('image/') ? 'image' : selectedFile.type.startsWith('audio/') ? 'audio' : 'video'
      body.append(field, selectedFile)
    }
    button.disabled = true
    button.textContent = 'AI 正在识别并生成工单…'
    note.textContent = '正在连接城讯通后端，请稍候。'
    try {
      const response = await fetch(`${API_BASE}/api/orders/report`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body })
      const payload = await response.json()
      if (!response.ok || !payload.success) {
        const error = new Error(payload.message || '提交失败')
        error.status = response.status
        throw error
      }
      const result = payload.data
      note.textContent = `提交成功：${result.order_no}，AI 识别为“${result.problem_type}”，由${result.department || '工作人员'}受理，获得积分 +${result.points_gained}。`
      button.disabled = false
      button.type = 'button'
      button.textContent = '查看工单和积分 →'
      button.addEventListener('click', () => { location.href = 'index.html?role=citizen' }, { once: true })
      form.reset()
      selectedFile = null
    } catch (error) {
      if (error.status === 401) {
        localStorage.removeItem(tokenKey)
        note.textContent = '原登录状态已失效，请重新注册或登录后继续。'
        showAuth('register', true, error.message)
      } else {
        note.textContent = `提交失败：${error.message}`
      }
      button.disabled = false
      button.textContent = '重新提交 →'
    }
  })
})()
