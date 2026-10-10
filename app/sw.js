const CACHE_NAME = "apuppet-web-admin-v1";
const BASEUI_CDN = "https://cdn.jsdelivr.net/npm/@thebase/ui@1.1.2/dist/";

const PRECACHE_URLS = [
  "./",
  "manifest.webmanifest",
  "app.css",
  "app.js",
  "app.xml",
  "js/lib/adapter-6.4.0.min.js",
  "js/lib/janus.js",
  "js/store.js",
  "js/janus-config.js",
  "js/utils.js",
  "js/commands.js",
  "js/video-stats.js",
  "js/remote-video.js",
  "js/remote-chat.js",
  "js/gesture-builder.js",
  "js/session-monitoring.js",
  "js/cheat-codes.js",
  "js/debug-utils.js",
  "js/remote-session.js",
  "static/images/favicon.ico",
  "static/images/icon-back.png",
  "static/images/icon-home.png",
  "static/images/icon-recents.png",
  "icons/icon-192.png",
  "icons/icon-512.png",
  "https://cdn.jsdelivr.net/npm/@thebase/ui@1.1.2/dist/baseui.min.css",
  "https://cdn.jsdelivr.net/npm/@thebase/ui@1.1.2/dist/baseui.esm.js",
  "https://cdn.jsdelivr.net/npm/@thebase/ui@1.1.2/dist/baseui.templates.xml"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

async function fromCdnCache(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) return cached;
  const response = await fetch(request);
  if (response.ok) cache.put(request, response.clone());
  return response;
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;
  if (request.url.startsWith(BASEUI_CDN)) {
    event.respondWith(fromCdnCache(request));
    return;
  }
  if (new URL(request.url).origin !== self.location.origin) return;

  event.respondWith(
    caches.open(CACHE_NAME).then(async (cache) => {
      try {
        const response = await fetch(request);
        if (response.ok) cache.put(request, response.clone());
        return response;
      } catch {
        const cached = await cache.match(request);
        if (cached) return cached;
        throw new Error(`No cached response for ${request.url} and network unavailable`);
      }
    })
  );
});
