(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const status = window.RobStatus;
  let state = null;
  let previewUrl = null;
  let previewBusy = false;
  let polling = false;
  let pairExpanded = false;
  let lastReceiverOnline = null;
  let linkChecking = false;
  let cameraBusy = false;
  let previewActive = false;
  let previewTimer = null;
  const headers = () => ({ 'Content-Type': 'application/json' });

  async function api(path, data) {
    const response = await fetch(path, { method: data === undefined ? 'GET' : 'POST', headers: headers(),
      ...(data === undefined ? {} : { body: JSON.stringify(data) }), cache: 'no-store' });
    if (response.status === 404 && path === '/api/state') throw new Error('Controller not available.');
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Controller request failed.');
    return result;
  }
  function message(id, value) { $(id).textContent = value; }
  function clearFrame() {
    $('setup-frame').hidden = true;
    $('camera-placeholder').hidden = false;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    previewUrl = null;
  }
  async function frame() {
    if (previewBusy || state?.camera.state !== 'capturing') return;
    previewBusy = true;
    try {
      const response = await fetch('/api/camera/frame', { cache: 'no-store' });
      if (response.status !== 200) return;
      const next = URL.createObjectURL(await response.blob());
      const previous = previewUrl;
      previewUrl = next;
      $('setup-frame').src = next;
      $('setup-frame').hidden = false;
      $('camera-placeholder').hidden = true;
      if (previous) URL.revokeObjectURL(previous);
    } catch (_error) { /* A preview failure must not interrupt capture. */ }
    finally { previewBusy = false; }
  }
  function render(snapshot) {
    state = snapshot;
    message('setup-connection', status.connection(snapshot));
    $('setup-connection').closest('.top-status').dataset.connection = 'connected';
    const receiverOnline = Boolean(snapshot.link?.online);
    message('pair-link', status.receiver(snapshot));
    $('pair-link').dataset.state = receiverOnline ? 'online' : 'offline';
    $('pair-connected').hidden = !receiverOnline || pairExpanded;
    $('pair-details').hidden = receiverOnline && !pairExpanded;
    $('pair-cancel').hidden = !receiverOnline;
    if (receiverOnline !== lastReceiverOnline) {
      message('pair-feedback', receiverOnline ? 'RetroPie receiver is online. Continue to the camera check.' :
        'No recent RetroPie receiver heartbeat. Check its power and network connection.');
      lastReceiverOnline = receiverOnline;
    }
    message('camera-state', status.camera(snapshot));
    $('camera-state').dataset.state = status.camera(snapshot) === 'NO CAMERA DETECTED' ? 'missing' : snapshot.camera.state;
    message('camera-device', snapshot.camera.devices?.[0]?.name || 'NO CAPTURE DEVICE');
    message('camera-fps', `${snapshot.camera.fps || 0} FPS`);
    message('camera-brightness', `${Math.round((snapshot.camera.brightness || 0) * 100)}% SIGNAL`);
    message('camera-feedback', snapshot.input?.frame_hook ?
      'Game frames are linked directly from RetroPie. Camera check is still available for alignment.' : snapshot.camera.message);
    $('camera-toggle').textContent = snapshot.camera.state === 'capturing' ? 'STOP CAMERA CHECK' :
      snapshot.camera.state === 'fault' ? 'CLEAR CAMERA FAULT' : 'START CAMERA CHECK';
    $('camera-toggle').disabled = cameraBusy;
    $('camera-reconnect').disabled = cameraBusy;
    if (snapshot.camera.state !== 'capturing') clearFrame();
    const game = snapshot.game;
    message('buttons-mode', game ? game.replace('_', '-').toUpperCase() : 'SELECT A GAME');
    $('setup-gates').hidden = game !== 'gyromite';
    $('setup-stack').hidden = game !== 'stack_up';
    if (game === 'gyromite') message('buttons-feedback', 'Use the red and blue buttons to test the matching gates. Stop the camera first.');
    else if (game === 'stack_up') message('buttons-feedback', 'Send one movement at a time, then watch the virtual blocks on Mission.');
    for (const color of ['red', 'blue']) {
      const button = document.querySelector(`[data-setup-gate="${color}"]`);
      const active = Boolean(snapshot.robot?.assist?.[color]);
      button.textContent = `${active ? 'RAISE' : 'LOWER'} ${color.toUpperCase()}`;
      button.setAttribute('aria-pressed', String(active));
      button.disabled = snapshot.camera.state === 'capturing';
    }
    const flashing = Boolean(snapshot.test?.flash_active);
    const ready = Boolean(snapshot.test?.ready) && !flashing;
    $('test-light').classList.toggle('flashing', flashing || previewActive && !ready);
    $('test-light').classList.toggle('ready', ready);
    message('test-led-label', flashing ? 'R.O.B. LIGHT FLASHING' : ready ? 'R.O.B. LIGHT ON' : previewActive ? 'PREVIEW ONLY · FLASHING' : 'R.O.B. LIGHT OFF');
    message('test-state', status.test(snapshot));
    message('test-feedback', flashing ? 'Test-mode optical signal detected. R.O.B.’s red light blinks; his arms do not move.' :
      ready ? 'A separate ready-light command was decoded. R.O.B.’s red light stays on; his arms do not move.' :
      previewActive ? 'This is a visual preview only. No camera signal was detected.' :
      snapshot.test?.armed ? 'Waiting for the Test-mode signal. Keep the green game area inside the camera frame.' :
      'Select a game, start the camera, and arm the check while the game shows Test mode.');
    if (snapshot.camera.state === 'capturing') frame();
  }
  async function act(path, data, feedback, success) {
    try { render(await api(path, data)); if (feedback && success) message(feedback, success); }
    catch (error) { message(feedback || 'pair-feedback', error.message); }
  }
  async function poll() {
    if (polling) return;
    polling = true;
    try { render(await api('/api/state')); }
    catch (error) {
      state = null;
      lastReceiverOnline = null;
      $('pair-connected').hidden = true;
      $('pair-details').hidden = true;
      const preview = location.protocol === 'file:';
      message('setup-connection', preview ? status.preview : status.offline);
      $('setup-connection').closest('.top-status').dataset.connection = preview ? 'preview' : 'offline';
      message('pair-link', 'RETROPIE UNKNOWN');
      $('pair-link').dataset.state = 'unknown';
      message('camera-state', 'CAMERA UNKNOWN');
      $('camera-state').dataset.state = 'unknown';
      message('camera-device', 'NO CAPTURE DEVICE');
      message('camera-fps', '0 FPS');
      message('camera-brightness', '0% SIGNAL');
      message('test-state', 'SIGNAL UNKNOWN');
      message('buttons-mode', 'SELECT A GAME');
      $('setup-gates').hidden = true; $('setup-stack').hidden = true;
      message('pair-feedback', preview ? 'Local preview only. Open Setup on the UNO Q for live checks.' : 'The UNO Q controller is unavailable. Start R.O.B. Vision in App Lab.');
      message('camera-feedback', 'Camera status is unavailable until the controller reconnects.');
      message('test-feedback', 'Game signal status is unavailable until the controller reconnects.');
      clearFrame();
    } finally { polling = false; }
  }
  async function checkLink() {
    if (linkChecking) return;
    linkChecking = true;
    $('pair-refresh').disabled = true;
    $('pair-refresh-offline').disabled = true;
    message('pair-feedback', 'Checking the latest RetroPie receiver heartbeat…');
    try {
      const snapshot = await api('/api/state');
      render(snapshot);
      const checkedAt = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit' });
      message('pair-feedback', snapshot.link?.online ?
        `Checked ${checkedAt}: RetroPie receiver heartbeat is current. Link ready.` :
        `Checked ${checkedAt}: no recent RetroPie receiver heartbeat. Check RetroPie's power and network.`);
    } catch (error) { message('pair-feedback', `Link check failed: ${error.message}`); }
    finally { linkChecking = false; $('pair-refresh').disabled = false; $('pair-refresh-offline').disabled = false; }
  }
  $('pair-refresh').addEventListener('click', checkLink);
  $('pair-refresh-offline').addEventListener('click', checkLink);
  $('pair-change').addEventListener('click', () => { pairExpanded = true; if (state) render(state); act('/api/matrix/pairing', { active: true }); });
  $('pair-cancel').addEventListener('click', () => { pairExpanded = false; if (state) render(state); act('/api/matrix/pairing', { active: false }); });
  $('pair-button').addEventListener('click', async () => {
    const button = $('pair-button');
    button.disabled = true;
    message('pair-feedback', 'Checking the console fingerprint and pairing…');
    try {
      const result = await api('/api/pair', { host: $('pair-host').value.trim(), code: $('pair-code').value.trim(), fingerprint: $('pair-fingerprint').value.trim() });
      message('pair-feedback', result.paired ? 'Pairing complete. Waiting for the RetroPie receiver to reconnect.' : 'Pairing was not confirmed.');
      if (result.paired) pairExpanded = false;
      $('pair-code').value = '';
      $('pair-fingerprint').value = '';
      poll();
    } catch (error) { message('pair-feedback', error.message); }
    finally { button.disabled = false; }
  });
  async function cameraAction(path) {
    if (cameraBusy) return;
    cameraBusy = true;
    $('camera-toggle').disabled = true;
    $('camera-reconnect').disabled = true;
    message('camera-feedback', path === '/api/camera/reconnect' ? 'Resetting camera and scanning for a connection…' : 'Updating camera…');
    try { render(await api(path, {})); }
    catch (error) { message('camera-feedback', error.message); poll(); }
    finally { cameraBusy = false; $('camera-toggle').disabled = false; $('camera-reconnect').disabled = false; }
  }
  $('camera-toggle').addEventListener('click', () => cameraAction(state?.camera.state === 'offline' ? '/api/camera/start' : '/api/camera/stop'));
  $('camera-reconnect').addEventListener('click', () => cameraAction('/api/camera/reconnect'));
  $('select-gyro').addEventListener('click', () => act('/api/game', { game: 'gyromite' }, 'test-feedback'));
  $('select-stack').addEventListener('click', () => act('/api/game', { game: 'stack_up' }, 'test-feedback'));
  $('arm-test').addEventListener('click', () => act('/api/test/arm', {}, 'test-feedback'));
  $('test-preview').addEventListener('click', () => {
    previewActive = true;
    if (previewTimer) clearTimeout(previewTimer);
    if (state) render(state);
    previewTimer = setTimeout(() => { previewActive = false; if (state) render(state); }, 4500);
  });
  document.querySelectorAll('[data-setup-gate]').forEach(button => button.addEventListener('click', () => {
    const color = button.dataset.setupGate;
    act('/api/gate-assist', { color, pressed: color === 'all' ? false : !state?.robot?.assist?.[color] }, 'buttons-feedback', 'Gate state updated. Check the game screen.');
  }));
  document.querySelectorAll('[data-setup-command]').forEach(button => button.addEventListener('click', () => {
    act('/api/command', { command: button.dataset.setupCommand }, 'buttons-feedback', 'Command sent to virtual R.O.B.');
  }));
  window.addEventListener('pagehide', () => { clearFrame(); if (previewTimer) clearTimeout(previewTimer); });
  poll();
  setInterval(poll, 1000);
})();
