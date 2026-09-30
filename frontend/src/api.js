import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

export function saveToken(token) {
  localStorage.setItem("fairresolve_token", token);
}

export function getToken() {
  return localStorage.getItem("fairresolve_token");
}

export function clearToken() {
  localStorage.removeItem("fairresolve_token");
}

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
