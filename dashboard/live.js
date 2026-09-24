/* Same-origin bridge to the UNO Q controller service. The static preview still works. */
(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  let connected = false;
  let latest = null;
  let lastSequence = -1;
  let busy = false;
  let available = true;
  let suspended = false;
  let token = '';
  let previewUrl = null;
  let previewBusy = false;
  let lastPreview = 0;
  const headers = () => ({ 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) });
  async function request(path, data) {
    const response = await fetch(path, { method: data === undefined ? 'GET' : 'POST', headers: headers(), ...(data === undefined ? {} : { body: JSON.stringify(data) }), cache: 'no-store' });
    if (response.status === 401) {
      $('controller-token').hidden = false;
      throw new Error('Enter the controller token, then press Enter.');
    }
    if (response.status === 404 && path === '/api/state') { available = false; throw new Error('Local preview only.'); }
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Controller request failed.');
    return result;
  }
  function showError(error) { $('controller-status').textContent = error.message; }
  async function refreshPreview() {
    if (previewBusy || Date.now() - lastPreview < 1000) return;
    previewBusy = true;
    lastPreview = Date.now();
    try {
      const response = await fetch('/api/camera/frame', { headers: token ? { Authorization: `Bearer ${token}` } : {}, cache: 'no-store' });
      if (response.status !== 200) return;
      const next = URL.createObjectURL(await response.blob());
      const previous = previewUrl;
      previewUrl = next;
      $('camera-frame').src = next;
      $('camera-frame').hidden = false;
      document.querySelector('.observer-placeholder').classList.add('has-frame');
      if (previous) URL.revokeObjectURL(previous);
    } catch (_error) { /* Diagnostic preview must never interrupt optical control. */ }
    finally { previewBusy = false; }
  }
  function clearPreview() {
    $('camera-frame').hidden = true;
    document.querySelector('.observer-placeholder').classList.remove('has-frame');
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
  }
  function accept(snapshot) {
    latest = snapshot;
    connected = true;
    const assist = snapshot.game === 'gyromite' && snapshot.camera.state !== 'capturing';
    $('gate-assist').hidden = !assist;
    for (const color of ['red', 'blue']) {
      const button = document.querySelector(`[data-gate="${color}"]`);
      const active = Boolean(snapshot.robot?.assist?.[color]);
      button.setAttribute('aria-pressed', String(active));
      button.textContent = `${active ? 'RAISE' : 'LOWER'} ${color.toUpperCase()}`;
    }
    $('camera-button').hidden = false;
    $('camera-button').textContent = snapshot.camera.state === 'capturing' ? 'STOP CAMERA' : 'START CAMERA';
    if (snapshot.camera.state === 'capturing') refreshPreview(); else clearPreview();
    const noCamera = snapshot.camera.platform === 'linux' && !snapshot.camera.devices.length;
    $('controller-status').textContent = snapshot.camera.state === 'fault' ? snapshot.camera.message : noCamera ? 'CONTROLLER READY · NO CAMERA ATTACHED' : snapshot.game ? `${snapshot.game === 'stack_up' ? 'STACK-UP' : 'GYROMITE'} · ${snapshot.camera.state.toUpperCase()} · ${snapshot.camera.fps} FPS` : 'CONTROLLER READY · SELECT A GAME';
    if (snapshot.sequence !== lastSequence || snapshot.camera.state !== $('camera-button').dataset.state) {
      $('camera-button').dataset.state = snapshot.camera.state;
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
      if (connected) { connected = false; clearPreview(); window.RobDashboard.leaveLive(); $('camera-button').hidden = true; $('gate-assist').hidden = true; showError(error); }
      else if (!$('controller-token').hidden) showError(error);
    } finally { busy = false; }
  }
  async function act(path, data) {
    try { const snapshot = await request(path, data); if (!suspended) accept(snapshot); }
    catch (error) { showError(error); }
  }
  $('camera-button').addEventListener('click', () => act(latest?.camera.state === 'capturing' ? '/api/camera/stop' : '/api/camera/start', {}));
  document.querySelectorAll('[data-gate]').forEach((button) => button.addEventListener('click', () => {
    if (!latest || latest.game !== 'gyromite') return;
    const color = button.dataset.gate;
    act('/api/gate-assist', { color, pressed: color === 'all' ? false : !latest.robot?.assist?.[color] });
  }));
  document.addEventListener('keydown', (event) => {
    if (!connected || latest?.game !== 'gyromite' || latest?.camera.state === 'capturing' || event.repeat || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.target instanceof Element && event.target.closest('input, textarea, [contenteditable="true"]')) return;
    const color = { '1': 'red', '2': 'blue', '0': 'all' }[event.key];
    if (color) { event.preventDefault(); act('/api/gate-assist', { color, pressed: color === 'all' ? false : !latest.robot?.assist?.[color] }); }
  });
  $('controller-token').addEventListener('keydown', (event) => { if (event.key === 'Enter') { token = event.target.value; poll(); } });
  window.RobLive = {
    hasService() { return connected; },
    select(mode) { suspended = false; act('/api/game', { game: mode === 'stack' ? 'stack_up' : 'gyromite' }); },
    command(action) {
      if (!latest?.game) { $('controller-status').textContent = 'SELECT A GAME FIRST'; return; }
      const command = ({ left: 'LEFT', right: 'RIGHT', raise: 'UP', lower: 'DOWN' })[action] || (latest.robot.grip === 'open' ? 'CLOSE' : 'OPEN');
      act('/api/command', { command });
    },
    reset() { if (latest?.game) act('/api/game', { game: latest.game }); },
    stop() { act('/api/camera/stop', {}).then(() => act('/api/game', { game: null })); },
    disconnect() { suspended = true; clearPreview(); $('gate-assist').hidden = true; if (latest) act('/api/game', { game: null }); window.RobDashboard.leaveLive(); }
  };
  poll();
  setInterval(poll, 500);
})();
