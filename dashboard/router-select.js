// A direct, visible visit to R.O.B. Vision selects it without stopping VirtualGlove.
async function refreshAppsLink() {
  const link = document.getElementById('apps-link');
  if (!link) return;
  try {
    const response = await fetch('http://' + window.location.hostname + '/api/state', {cache: 'no-store'});
    if (!response.ok) throw new Error('Controller Router unavailable');
    const state = await response.json();
    link.hidden = Object.values(state.apps || {}).filter(app => app.installed).length < 2;
  } catch (_error) {
    link.hidden = true;
  }
}
refreshAppsLink();
setInterval(refreshAppsLink, 15000);
if (window.top === window.self && document.visibilityState === 'visible' &&
    window.location.protocol === 'http:' && window.location.port === '8101') {
  fetch('http://' + window.location.hostname + '/api/select', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({app: 'rob_vision'}), cache: 'no-store'
  }).catch(() => {});
}
