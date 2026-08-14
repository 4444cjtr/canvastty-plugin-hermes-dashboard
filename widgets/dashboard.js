const host = window.CanvasTTYPlugin;
const DASHBOARD_URL = "http://127.0.0.1:9119/";
const POLL_MS = 5_000;

const dot = document.querySelector("#dot");
const statusEl = document.querySelector("#status");
const detailEl = document.querySelector("#detail");
const openButton = document.querySelector("#open");
const widget = document.querySelector("#widget");

let locale = "en";

host.onContext((context) => {
  locale = context.appearance.locale;
  document.documentElement.dataset.palette = context.appearance.palette;
  document.documentElement.lang = locale;
  render();
  void refresh();
});

openButton.addEventListener("click", () => {
  void host.request("external.open", { url: DASHBOARD_URL });
});

function render() {
  const state = dot.dataset.state;
  statusEl.textContent = state === "online"
    ? (locale === "ru" ? "Онлайн" : "Online")
    : state === "offline"
      ? (locale === "ru" ? "Офлайн" : "Offline")
      : "…";
  detailEl.textContent = state === "online"
    ? (locale === "ru" ? "Дашборд запущен" : "Dashboard is running")
    : state === "offline"
      ? (locale === "ru" ? "Дашборд не запущен" : "Dashboard is not running")
      : (locale === "ru" ? "Проверка…" : "Checking…");
  openButton.disabled = state !== "online";
  openButton.textContent = locale === "ru" ? "Открыть дашборд" : "Open Dashboard";
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
