const host = window.CanvasTTYPlugin;
const DASHBOARD_URL = "http://127.0.0.1:9119/";
const HELPER_URL = "http://127.0.0.1:9210/";
const TOKEN_KEY = "helper_token";
const POLL_MS = 5_000;

const dot = document.querySelector("#dot");
const statusEl = document.querySelector("#status");
const detailEl = document.querySelector("#detail");
const openButton = document.querySelector("#open");
const startButton = document.querySelector("#start");
const widget = document.querySelector("#widget");

let locale = "en";
let helperToken = null;

host.onContext((context) => {
  locale = context.appearance.locale;
  document.documentElement.dataset.palette = context.appearance.palette;
  document.documentElement.lang = locale;
  render();
  void refresh();
});

// Читаем токен helper из изолированного хранилища плагина
async function loadToken() {
  try {
    helperToken = await host.storage.get(TOKEN_KEY);
  } catch {
    helperToken = null;
  }
  render();
}

openButton.addEventListener("click", () => {
  void host.request("external.open", { url: DASHBOARD_URL });
});

startButton.addEventListener("click", () => {
  void startDashboard();
});

async function startDashboard() {
  startButton.disabled = true;
  detailEl.textContent = locale === "ru" ? "Запуск дашборда…" : "Starting dashboard…";
  render();
  try {
    const headers = { "Content-Type": "application/json" };
    if (helperToken) headers["X-Hermes-Token"] = String(helperToken);
    const response = await fetch(HELPER_URL + "start", {
      method: "POST",
      cache: "no-store",
      headers,
      body: JSON.stringify({})
    });
    if (response.ok) {
      const data = await response.json();
      if (data.running) {
        dot.dataset.state = "online";
      } else {
        dot.dataset.state = "offline";
      }
    } else if (response.status === 403) {
      dot.dataset.state = "offline";
      detailEl.textContent = locale === "ru"
        ? "Нет токена helper (см. README)"
        : "Helper token missing (see README)";
    } else {
      dot.dataset.state = "offline";
    }
  } catch {
    dot.dataset.state = "offline";
  }
  render();
}

function render() {
  const state = dot.dataset.state;
  statusEl.textContent = state === "online"
    ? (locale === "ru" ? "Онлайн" : "Online")
    : state === "offline"
      ? (locale === "ru" ? "Офлайн" : "Offline")
      : "…";

  if (state === "online") {
    detailEl.textContent = locale === "ru" ? "Дашборд запущен" : "Dashboard is running";
    openButton.disabled = false;
    startButton.hidden = true;
  } else if (state === "offline") {
    detailEl.textContent = locale === "ru" ? "Дашборд не запущен" : "Dashboard is not running";
    openButton.disabled = true;
    startButton.hidden = false;
  } else {
    detailEl.textContent = locale === "ru" ? "Проверка…" : "Checking…";
    openButton.disabled = true;
    startButton.hidden = true;
  }

  openButton.textContent = locale === "ru" ? "Открыть дашборд" : "Open Dashboard";
  startButton.textContent = locale === "ru" ? "Запустить" : "Start";
}

async function refresh() {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 2_000);
    await fetch(DASHBOARD_URL, {
      method: "GET",
      cache: "no-store",
      signal: controller.signal
    });
    clearTimeout(timer);
    dot.dataset.state = "online";
  } catch {
    dot.dataset.state = "offline";
  }
  render();
}

setInterval(() => void refresh(), POLL_MS);
void loadToken();
