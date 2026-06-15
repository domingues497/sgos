/**
 * SGOS – API Client
 * Centraliza todas as chamadas ao backend Django REST API.
 * Todas as páginas importam este arquivo.
 */

const API_BASE_STORAGE_KEY = 'sgos_api_base';
const WORKSPACE_HIDDEN_STORAGE_KEY = 'sgos_workspace_hidden';

function _isLocalHost(host) {
  return host === 'localhost' || host === '127.0.0.1';
}

function _normalizeApiBase(input) {
  const u = new URL(String(input || '').trim());
  u.search = '';
  u.hash = '';

  let path = (u.pathname || '/').replace(/\/+$/g, '');
  if (!path.endsWith('/api')) path = `${path}/api`;
  u.pathname = path;

  return u.toString().replace(/\/+$/g, '');
}

const __host = window.location.hostname || '127.0.0.1';
const __defaultLocal = 'http://127.0.0.1:8010/api';
var API_BASE = window.API_BASE || localStorage.getItem(API_BASE_STORAGE_KEY) || (_isLocalHost(__host) ? __defaultLocal : `${window.location.origin}/api`);
window.SGOS_API_BASE = API_BASE;

let _apiBaseReadyPromise = null;
let _meOverviewPromise = null;

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
    if (stored) {
      try {
        API_BASE = _normalizeApiBase(stored);
      } catch {
        localStorage.removeItem(API_BASE_STORAGE_KEY);
      }
    }
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

async function getMeOverviewCached() {
  if (_meOverviewPromise) return _meOverviewPromise;
  _meOverviewPromise = api.me.overview().catch(err => {
    _meOverviewPromise = null;
    throw err;
  });
  return _meOverviewPromise;
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
    if (!this.isLoggedIn()) {
      window.location.href = 'login.html';
      return false;
    }
    return true;
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
      throw { status: 401, data: null, message: 'Não autenticado.' };
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

  async resetPassword(payload) {
    await ensureApiBase();
    const res = await fetch(`${API_BASE}/auth/reset-password/`, {
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
    list:   (params = {}) => {
      const normalized = typeof params === 'string'
        ? (params ? { search: params } : {})
        : (params || {});
      const qs = new URLSearchParams(normalized).toString();
      return api.get(`/clientes/${qs ? '?' + qs : ''}`);
    },
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
    assign:  (id, body = {}) => api.patch(`/workorders/${id}/assign/`, body),
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

  users: {
    list:   (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return api.get(`/admin/users/${qs ? '?' + qs : ''}`);
    },
    create: (body)        => api.post('/admin/users/', body),
    update: (id, body)    => api.patch(`/admin/users/${id}/`, body),
    disable:(id)          => api.delete(`/admin/users/${id}/`),
  },

  lookups: {
    list:   (kind)          => api.get(`/admin/lookups/${encodeURIComponent(kind)}/`),
    create: (kind, body)    => api.post(`/admin/lookups/${encodeURIComponent(kind)}/`, body),
    update: (kind, id, body)=> api.patch(`/admin/lookups/${encodeURIComponent(kind)}/${id}/`, body),
    disable:(kind, id)      => api.delete(`/admin/lookups/${encodeURIComponent(kind)}/${id}/`),
  },

  // ── Dashboard ─────────────────────────────────────────
  dashboard: () => api.get('/dashboard/'),

  me: {
    overview: (params = {}) => {
      const qs = new URLSearchParams(params).toString();
      return api.get(`/me/overview/${qs ? '?' + qs : ''}`);
    },
  },
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

function isWorkspaceHidden() {
  const stored = localStorage.getItem(WORKSPACE_HIDDEN_STORAGE_KEY);
  if (stored === null) return true;
  return stored === '1';
}

function applyWorkspaceVisibility(hidden) {
  document.body.classList.toggle('workspace-hidden', hidden);
  document.querySelectorAll('.btn-sidebar-toggle').forEach(btn => {
    const label = hidden ? 'Mostrar workspace' : 'Ocultar workspace';
    btn.setAttribute('aria-label', label);
    btn.setAttribute('title', label);
    const text = btn.querySelector('.btn-sidebar-toggle-text');
    if (text) text.textContent = label;
  });
}

function toggleWorkspaceVisibility() {
  const hidden = !document.body.classList.contains('workspace-hidden');
  localStorage.setItem(WORKSPACE_HIDDEN_STORAGE_KEY, hidden ? '1' : '0');
  applyWorkspaceVisibility(hidden);
}

function initSidebarToggle() {
  if (!document.querySelector('.btn-sidebar-toggle') || !document.querySelector('.hero-card')) return;

  applyWorkspaceVisibility(isWorkspaceHidden());

  document.querySelectorAll('.btn-sidebar-toggle').forEach(btn => {
    if (btn.dataset.bound === '1') return;
    btn.dataset.bound = '1';
    btn.addEventListener('click', toggleWorkspaceVisibility);
  });
}

function getSidebarNavKey(link) {
  if (!link) return '';
  if (link.dataset && link.dataset.nav) return link.dataset.nav;
  const href = String(link.getAttribute('href') || '');
  if (href === 'dashboard.html') return 'dashboard';
  if (href === 'abrir-chamado.html') return 'abrir';
  if (href.includes('kanban.html?view=mine')) return 'mine';
  if (href === 'kanban.html') return 'kanban';
  if (href === 'clientes.html') return 'clientes';
  if (href.startsWith('cadastros.html')) return 'cadastros';
  return '';
}

function applySidebarPermissions(overview = null) {
  const isAdmin = !!(overview?.user?.is_admin);
  const tipo = overview?.user?.tipo || '';
  const allowed = new Set(
    tipo === 'somente_cliente'
      ? ['dashboard', 'abrir', 'mine']
      : isAdmin
      ? ['dashboard', 'abrir', 'mine', 'kanban', 'clientes', 'cadastros']
      : ['dashboard', 'abrir', 'mine', 'kanban']
  );

  document.querySelectorAll('.sidebar-nav .nav-item').forEach(link => {
    const key = getSidebarNavKey(link);
    if (!key) return;
    link.style.display = allowed.has(key) ? '' : 'none';
  });

  const currentKey = getCurrentPageNavKey();
  if (currentKey && !allowed.has(currentKey)) {
    if (tipo === 'somente_cliente') {
      window.location.replace(currentKey === 'kanban' ? 'kanban.html?view=mine' : 'dashboard.html');
    }
  }

  return { isAdmin, tipo, allowed };
}

function getCurrentPageNavKey() {
  const path = window.location.pathname.split('/').pop().toLowerCase();
  const qs = new URLSearchParams(window.location.search);
  if (path === 'dashboard.html' || path === '') return 'dashboard';
  if (path === 'abrir-chamado.html') return 'abrir';
  if (path === 'clientes.html') return 'clientes';
  if (path === 'cadastros.html') return 'cadastros';
  if (path === 'kanban.html') return (qs.get('view') || '').toLowerCase() === 'mine' ? 'mine' : 'kanban';
  return '';
}

// Preenche sidebar com nome do usuário logado
function fillSidebarUser() {
  const user = Auth.getUser();
  if (!user) return;
  const nameEl = document.querySelector('.user-name');
  const roleEl = document.querySelector('.user-role');
  const avEl   = document.querySelector('.avatar');
  if (nameEl) nameEl.textContent = user.first_name ? `${user.first_name} ${user.last_name || ''}`.trim() : user.username;
  if (avEl)   avEl.textContent   = (user.first_name?.[0] || user.username[0]).toUpperCase() + (user.last_name?.[0] || '').toUpperCase();

  const mineLink = Array.from(document.querySelectorAll('a.nav-item')).find(a => (a.getAttribute('href') || '').includes('kanban.html?view=mine'));
  getMeOverviewCached().then(o => {
    const { isAdmin } = applySidebarPermissions(o);
    if (roleEl) {
      const dept = o?.user?.departamento || user.departamento || '';
      const tipo = o?.user?.tipo || user.tipo || '';
      roleEl.textContent =
        isAdmin ? 'Administrador'
        : tipo === 'somente_cliente' ? 'Cliente'
        : (dept || 'Técnico');
    }

    if (!mineLink) return;
    const aguardando = o?.badges?.aguardando || 0;
    const altaCritica = o?.badges?.alta_critica || 0;
    const txt = [];
    if (altaCritica) txt.push(`${altaCritica}`);
    if (aguardando) txt.push(`${aguardando}`);
    let badge = mineLink.querySelector('.nav-badge');
    if (!badge) {
      badge = document.createElement('span');
      badge.className = 'nav-badge';
      mineLink.appendChild(badge);
    }
    badge.textContent = txt.length ? txt.join(' · ') : '';
    badge.style.display = txt.length ? 'inline-flex' : 'none';
  }).catch(() => {
    applySidebarPermissions(null);
    if (roleEl) roleEl.textContent = user.tipo === 'somente_cliente' ? 'Cliente' : (user.departamento || 'Técnico');
  });
}

async function requireAdminAccess(redirectTo = 'dashboard.html') {
  try {
    const overview = await getMeOverviewCached();
    if (overview?.user?.is_admin) return true;
  } catch {
  }
  window.location.href = redirectTo;
  return false;
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSidebarToggle);
} else {
  initSidebarToggle();
}
