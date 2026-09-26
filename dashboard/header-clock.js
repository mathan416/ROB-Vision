(() => {
  'use strict';
  const clock = document.getElementById('clock');
  if (!clock) return;
  const tick = () => { clock.textContent = new Date().toLocaleTimeString('en-GB', { hour12: false }); };
  tick();
  setInterval(tick, 1000);
})();
