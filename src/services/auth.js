export function getToken() {
  return sessionStorage.getItem("token");
}

export function setToken(token) {
  sessionStorage.setItem("token", token);
}

export function logout() {
  sessionStorage.removeItem("token");
  window.location.href = "/login";
}

export function isLoggedIn() {
  return !!sessionStorage.getItem("token");
}