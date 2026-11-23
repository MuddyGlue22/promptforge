// Cookie-free visit counter (Umami Cloud). See privacy.html.
// Sends only the page path plus any utm_* tags. Shared-character links carry the
// whole character in the query string, and that must never leave the browser,
// so automatic tracking is off and every hit is sent with the cleaned path.
(() => {
  const WEBSITE_ID = "f4037189-7473-464b-97e6-74320dd95198";
  if (!/^[0-9a-f-]{36}$/.test(WEBSITE_ID)) return;

  const tags = new URLSearchParams();
  for (const [k, v] of new URLSearchParams(location.search)) {
    if (k.startsWith("utm_")) tags.set(k, v);
  }
  const url = location.pathname + (tags.size ? `?${tags}` : "");

  const s = document.createElement("script");
  s.src = "https://cloud.umami.is/script.js";
  s.defer = true;
  s.dataset.websiteId = WEBSITE_ID;
  s.dataset.autoTrack = "false";
  s.dataset.doNotTrack = "true";
  s.dataset.domains = "tavernportraits.com";
  s.onload = () => window.umami?.track(p => ({ ...p, url }));
  document.head.appendChild(s);

  // Named events (e.g. "copy-prompt"), with no details about the character.
  window.countEvent = name => window.umami?.track(p => ({ ...p, url, name }));
})();
