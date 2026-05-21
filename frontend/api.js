/**
 * SGOS – API Client
 * Centraliza todas as chamadas ao backend Django REST API.
 * Todas as páginas importam este arquivo.
 */

const API_BASE_STORAGE_KEY = 'sgos_api_base';

var API_BASE = window.API_BASE || localStorage.getItem(API_BASE_STORAGE_KEY) || 'http://127.0.0.1:8010/api';
window.SGOS_API_BASE = API_BASE;

let _apiBaseReadyPromise = null;

function _getApiBaseCandidates() {
  if (window.API_BASE) return [window.API_BASE];

  const host = window.location.hostname || '127.0.0.1';
  const bases = [
    `http://${host}:8010/api`,
  ];

  if (host === 'localhost') {
    bases.push('http://127.0.0.1:8010/api');
  }
  if (host === '127.0.0.1') {
    bases.push('http://localhost:8010/api');
  }

  const seen = new Set();
  return bases.filter(b => (seen.has(b) ? false : (seen.add(b), true)));
}

async function _probeApiBase(base) {
  try {
    const res = await fetch(`${base}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{}',
    });
    return res.status !== 404;
  } catch {
    return false;
  }
}

async function ensureApiBase() {
  if (_apiBaseReadyPromise) return _apiBaseReadyPromise;
  _apiBaseReadyPromise = (async () => {
    if (window.API_BASE) return;
    const stored = localStorage.getItem(API_BASE_STORAGE_KEY);
    if (stored) API_BASE = stored;
    window.SGOS_API_BASE = API_BASE;

    const okCurrent = await _probeApiBase(API_BASE);
    if (okCurrent) return;
    localStorage.removeItem(API_BASE_STORAGE_KEY);

    const candidates = _getApiBaseCandidates();
    for (const base of candidates) {
      const ok = await _probeApiBase(base);
      if (ok) {
        API_BASE = base;
        localStorage.setItem(API_BASE_STORAGE_KEY, base);
        window.SGOS_API_BASE = API_BASE;
        return;
      }
    }
  })();
  return _apiBaseReadyPromise;
}

// ── Token management ──────────────────────────────────────────────────────────
const Auth = {
  getAccess()  { return localStorage.getItem('sgos_access'); },
  getRefresh() { return localStorage.getItem('sgos_refresh'); },
  getUser()    { const u = localStorage.getItem('sgos_user'); return u ? JSON.parse(u) : null; },

  save(access, refresh, user) {
    localStorage.setItem('sgos_access',  access);
    localStorage.setItem('sgos_refresh', refresh);
    localStorage.setItem('sgos_user',    JSON.stringify(user));
  },

  clear() {
    ['sgos_access', 'sgos_refresh', 'sgos_user'].forEach(k => localStorage.removeItem(k));
  },

  isLoggedIn() { return !!this.getAccess(); },

  /** Redireciona para login se não autenticado */
  requireAuth() {
    if (!this.isLoggedIn()) { window.location.href = 'login.html'; }
  },

  /** Redireciona para dashboard se já autenticado */
  redirectIfLoggedIn() {
    if (this.isLoggedIn()) { window.location.href = 'dashboard.html'; }
  },
};

// ── HTTP helper ───────────────────────────────────────────────────────────────
async function request(method, path, body = null, isForm = false) {
  await ensureApiBase();

  const access = Auth.getAccess();
  const headers = {};
  if (access) headers['Authorization'] = `Bearer ${access}`;
  if (!isForm) headers['Content-Type'] = 'application/json';

  const opts = { method, headers };
  if (body) opts.body = isForm ? body : JSON.stringify(body);

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, opts);
  } catch (e) {
    throw { status: 0, data: null, message: e?.message || 'Falha ao conectar no servidor.' };
  }

  // Token expirado → tenta refresh
  if (res.status === 401) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
      res = await fetch(`${API_BASE}${path}`, { ...opts, headers });
    } else {
      Auth.clear();
      window.location.href = 'login.html';
      return;
    }
  }

  // Sem conteúdo (DELETE 204)
  if (res.status === 204) return null;

  let data = null;
  try {
    const ct = res.headers.get('content-type') || '';
    if (ct.includes('application/json')) data = await res.json();
    else data = await res.text();
  } catch {
    data = null;
  }
  if (!res.ok) throw { status: res.status, data };
  return data;
}

async function tryRefresh() {
  const refresh = Auth.getRefresh();
  if (!refresh) return false;
  try {
    const res = await fetch(`${API_BASE}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('sgos_access',  data.access);
    localStorage.setItem('sgos_refresh', data.refresh || refresh);
    return true;
  } catch { return false; }
}

// ── Shorthand methods ─────────────────────────────────────────────────────────
const api = {
  get:    (path)         => request('GET',    path),
  post:   (path, body)   => request('POST',   path, body),
  put:    (path, body)   => request('PUT',    path, body),
  patch:  (path, body)   => request('PATCH',  path, body),
  delete: (path)         => request('DELETE', path),
  upload: (path, form)   => request('POST',   path, form, true),

  // ── Auth ──────────────────────────────────────────────
  async login(username, password) {
    await ensureApiBase();
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    let data = null;
    try {
      const ct = res.headers.get('content-type') || '';
      if (ct.includes('application/json')) data = await res.json();
      else data = await res.text();
    } catch {
      data = null;
    }
    if (!res.ok) throw { status: res.status, data };
    return data;
  },

  async register(payload) {
    await ensureApiBase();
    const res = await fetch(`${API_BASE}/auth/register/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    let data = null;
    try {
      const ct = res.headers.get('content-type') || '';
      if (ct.includes('application/json')) data = await res.json();
      else data = await res.text();
    } catch {
      data = null;
    }
    if (!res.ok) throw { status: res.status, data };
    return data;
  },

  async logout() {
    try { await api.post('/auth/logout/', { refresh: Auth.getRefresh() }); } catch {}
    Auth.clear();
    window.location.href = 'login.html';
  },

  // ── Clientes ──────────────────────────────────────────
  clientes: {
    list:   (q = '')    => api.get(`/clientes/${q ? '?search=' + encodeURIComponent(q) : ''}`),
    get:    (id)        => api.get(`/clientes/${id}/`),
    create: (body)      => api.post('/clientes/', body),
    update: (id, body)  => api.put(`/clientes/${id}/`, body),
    delete: (id)        => api.delete(`/clientes/${id}/`),
  },

  // ── Ordens de Serviço ─────────────────────────────────
  os: {
    list:    (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return api.get(`/workorders/${qs ? '?' + qs : ''}`);
    },
    get:     (id)          => api.get(`/workorders/${id}/`),
    create:  (body)        => api.post('/workorders/', body),
    avancar: (id, obs='')  => api.patch(`/workorders/${id}/etapa/`, { observacao: obs }),
    delete:  (id)          => api.delete(`/workorders/${id}/`),
    meta:    ()            => api.get('/workorders/meta/'),
    iteracoes: {
      list:   (osId)       => api.get(`/workorders/${osId}/iteracoes/`),
      create: (osId, text) => api.post(`/workorders/${osId}/iteracoes/`, { texto: text }),
    },
    anexos: {
      upload: (osId, file) => {
        const fd = new FormData(); fd.append('arquivo', file);
        return api.upload(`/workorders/${osId}/anexos/`, fd);
      },
    },
  },

  // ── Dashboard ─────────────────────────────────────────
  dashboard: () => api.get('/dashboard/'),
};

// ── Toast utility (shared across pages) ──────────────────────────────────────
function showToast(type, msg) {
  let t = document.getElementById('_toast');
  if (!t) {
    t = document.createElement('div');
    t.id = '_toast';
    t.className = 'toast';
    document.body.appendChild(t);
  }
  const icons = {
    success: '<polyline points="20 6 9 17 4 12"/>',
    error:   '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    info:    '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
  };
  const colors = { success: ['#1e2433','#10b981'], error: ['#7f1d1d','#fca5a5'], info: ['#1e3a5f','#60a5fa'] };
  const [bg, iconColor] = colors[type] || colors.info;
  t.style.background = bg;
  t.style.color = '#fff';
  t.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="${iconColor}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">${icons[type]||icons.info}</svg><span>${msg}</span>`;
  t.classList.remove('is-visible');
  requestAnimationFrame(() => { t.classList.add('is-visible'); });
  setTimeout(() => { t.classList.remove('is-visible'); }, 3400);
}

/** Extrai mensagem legível de um erro da API */
function apiErrorMsg(err) {
  if (!err?.data) return err?.message || 'Erro de conexão com o servidor.';
  const d = err.data;
  if (typeof d === 'string') return d;
  // Pega o primeiro valor de campo com erro
  const firstKey = Object.keys(d)[0];
  const val = d[firstKey];
  if (Array.isArray(val)) return val[0];
  if (typeof val === 'string') return val;
  return JSON.stringify(d);
}

// Preenche sidebar com nome do usuário logado
function fillSidebarUser() {
  const user = Auth.getUser();
  if (!user) return;
  const nameEl = document.querySelector('.user-name');
  const roleEl = document.querySelector('.user-role');
  const avEl   = document.querySelector('.avatar');
  if (nameEl) nameEl.textContent = user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username;
  if (roleEl) roleEl.textContent = user.departamento || 'Funcionário';
  if (avEl)   avEl.textContent   = (user.first_name?.[0] || user.username[0]).toUpperCase() + (user.last_name?.[0] || '').toUpperCase();
}
