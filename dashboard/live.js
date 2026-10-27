/* Same-origin bridge to the UNO Q controller service. The static preview still works. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const status = window.RobStatus;
  let connected = false;
  let latest = null;
  let lastSequence = -1;
  let busy = false;
  let available = true;
  let suspended = false;
  let lastFrameLink = null;
  let lastLinkOnline = null;
  let lastTestLightMode = null;
  let liveGame = null;
  const headers = () => ({ 'Content-Type': 'application/json' });
  async function request(path, data) {
    const response = await fetch(path, { method: data === undefined ? 'GET' : 'POST', headers: headers(), ...(data === undefined ? {} : { body: JSON.stringify(data) }), cache: 'no-store' });
    if (response.status === 404 && path === '/api/state') { available = false; throw new Error('Local preview only.'); }
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Controller request failed.');
    return result;
  }
  function showError(error) { $('controller-status').textContent = error.message; }
  function accept(snapshot) {
    latest = snapshot;
    connected = true;
    $('connection').textContent = status.connection(snapshot);
    $('connection').closest('.top-status').dataset.connection = 'connected';
    if (!snapshot.game) {
      $('gate-assist').hidden = true;
      if (liveGame) window.RobDashboard.leaveLive();
      $('connection').textContent = status.connection(snapshot);
      $('connection').closest('.top-status').dataset.connection = 'connected';
      $('controller-status').textContent = status.controllerDetail(snapshot);
      liveGame = null;
      lastSequence = snapshot.sequence;
      lastFrameLink = Boolean(snapshot.input?.frame_hook);
      lastLinkOnline = Boolean(snapshot.link?.online);
      lastTestLightMode = null;
      return;
    }
    liveGame = snapshot.game;
    const assist = snapshot.game === 'gyromite';
    $('gate-assist').hidden = !assist;
    for (const color of ['red', 'blue']) {
      const button = document.querySelector(`[data-gate="${color}"]`);
      const active = Boolean(snapshot.robot?.assist?.[color]);
      button.setAttribute('aria-pressed', String(active));
      button.textContent = `${active ? 'RAISE' : 'LOWER'} ${color.toUpperCase()}`;
    }
    $('controller-status').textContent = status.controllerDetail(snapshot);
    const testLightMode = snapshot.test?.flash_active ? 'flashing' : snapshot.test?.ready ? 'ready' : 'off';
    if (snapshot.sequence !== lastSequence || Boolean(snapshot.input?.frame_hook) !== lastFrameLink || Boolean(snapshot.link?.online) !== lastLinkOnline || testLightMode !== lastTestLightMode) {
      lastFrameLink = Boolean(snapshot.input?.frame_hook);
      lastLinkOnline = Boolean(snapshot.link?.online);
      lastTestLightMode = testLightMode;
      lastSequence = snapshot.sequence;
      window.RobDashboard.applyLive(snapshot);
      const recent = snapshot.events.at(-1);
      if (recent && recent.kind !== 'session') {
        const item = document.createElement('li');
        const stamp = document.createElement('time');
        const message = document.createElement('span');
        stamp.textContent = new Date(recent.time * 1000).toLocaleTimeString('en-GB', { hour12: false });
        message.textContent = recent.message;
        item.append(stamp, message);
        $('event-list').prepend(item);
        while ($('event-list').children.length > 5) $('event-list').lastElementChild.remove();
        $('event-count').textContent = String(snapshot.sequence).padStart(3, '0') + ' EVENTS';
      }
    }
  }
  async function poll() {
    if (busy || !available || suspended) return;
    busy = true;
    try { accept(await request('/api/state')); }
    catch (error) {
      if (connected && liveGame) window.RobDashboard.leaveLive();
      connected = false; liveGame = null; latest = null; $('gate-assist').hidden = true;
      const preview = location.protocol === 'file:' || !available;
      $('connection').textContent = preview ? status.preview : status.offline;
      $('connection').closest('.top-status').dataset.connection = preview ? 'preview' : 'offline';
      $('controller-status').textContent = preview ? 'LOCAL PREVIEW · NO CONTROLLER' : 'CONTROLLER OFFLINE · GAME FRAMES UNKNOWN · CONSOLE UNKNOWN';
    } finally { busy = false; }
  }
  async function act(path, data) {
    try { const snapshot = await request(path, data); if (!suspended) accept(snapshot); }
    catch (error) { showError(error); }
  }
  document.querySelectorAll('[data-gate]').forEach((button) => button.addEventListener('click', () => {
    if (!latest || latest.game !== 'gyromite') return;
    const color = button.dataset.gate;
    act('/api/gate-assist', { color, pressed: color === 'all' ? false : !latest.robot?.assist?.[color] });
  }));
  document.addEventListener('keydown', (event) => {
    if (!connected || latest?.game !== 'gyromite' || event.repeat || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.target instanceof Element && event.target.closest('input, textarea, [contenteditable="true"]')) return;
    const color = { '1': 'red', '2': 'blue', '0': 'all' }[event.key];
    if (color) { event.preventDefault(); act('/api/gate-assist', { color, pressed: color === 'all' ? false : !latest.robot?.assist?.[color] }); }
  });
  window.RobLive = {
    hasService() { return connected; },
    gameActive() { return Boolean(liveGame); },
    select(mode) { suspended = false; act('/api/game', { game: mode === 'stack' ? 'stack_up' : 'gyromite' }); },
    command(action) {
      if (!latest?.game) { $('controller-status').textContent = 'SELECT A GAME FIRST'; return; }
      const command = ({ left: 'LEFT', right: 'RIGHT', raise: 'UP', lower: 'DOWN' })[action] || (latest.robot.grip === 'open' ? 'CLOSE' : 'OPEN');
      act('/api/command', { command });
    },
    reset() { if (latest?.game) act('/api/game', { game: latest.game }); },
    stop() { act('/api/game', { game: null }); },
    disconnect() { suspended = true; $('gate-assist').hidden = true; if (latest) act('/api/game', { game: null }); window.RobDashboard.leaveLive(); }
  };
  poll();
  setInterval(poll, 500);
})();
