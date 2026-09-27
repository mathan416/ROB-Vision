// A direct, visible visit to R.O.B. Vision selects it without stopping VirtualGlove.
if (window.top === window.self && document.visibilityState === 'visible' &&
    window.location.protocol === 'http:' && window.location.port === '8101') {
  fetch('http://' + window.location.hostname + '/api/select', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({app: 'rob_vision'}), cache: 'no-store'
  }).catch(() => {});
}
