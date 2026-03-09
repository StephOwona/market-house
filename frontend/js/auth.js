function saveAuth(token, user) {
  localStorage.setItem("mh_token", token);
  localStorage.setItem("mh_user", JSON.stringify(user));
}

function getUser() {
  try { return JSON.parse(localStorage.getItem("mh_user")); } catch { return null; }
}

function getToken() {
  return localStorage.getItem("mh_token");
}

function logout() {
  localStorage.removeItem("mh_token");
  localStorage.removeItem("mh_user");
  window.location.href = "/";
}

function requireAuth(expectedRole) {
  const token = getToken();
  const user = getUser();
  if (!token || !user) {
    window.location.href = "/";
    return null;
  }
  if (expectedRole && user.role !== expectedRole && user.role !== "admin") {
    window.location.href = "/";
    return null;
  }
  return user;
}

function redirectByRole(user) {
  if (!user) { window.location.href = "/"; return; }
  if (user.role === "client") window.location.href = "/client/dashboard.html";
  else if (user.role === "courier") window.location.href = "/courier/dashboard.html";
  else if (user.role === "admin") window.location.href = "/admin/dashboard.html";
}

function initTheme() {
  const t = localStorage.getItem('mh_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', t);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('mh_theme', next);
}

initTheme();
