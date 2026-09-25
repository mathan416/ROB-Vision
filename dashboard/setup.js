(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  let state = null;
  let previewUrl = null;
  let previewBusy = false;
  let polling = false;
  let pairExpanded = false;
  let lastReceiverOnline = null;
  let linkChecking = false;
  let cameraBusy = false;
  const headers = () => ({ 'Content-Type': 'application/json' });

  async function api(path, data) {
    const response = await fetch(path, { method: data === undefined ? 'GET' : 'POST', headers: headers(),
      ...(data === undefined ? {} : { body: JSON.stringify(data) }), cache: 'no-store' });
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
    message('setup-connection', `${snapshot.game ? snapshot.game.replace('_', '-').toUpperCase() : 'CONTROLLER'} / CONNECTED`);
    const receiverOnline = Boolean(snapshot.link?.online);
    message('pair-link', receiverOnline ? 'RECEIVER ONLINE' : 'RECEIVER OFFLINE');
    $('pair-connected').hidden = !receiverOnline || pairExpanded;
    $('pair-details').hidden = receiverOnline && !pairExpanded;
    $('pair-cancel').hidden = !receiverOnline;
    if (receiverOnline !== lastReceiverOnline) {
      message('pair-feedback', receiverOnline ? 'RetroPie receiver is online. Continue to the camera check.' :
        'No recent RetroPie receiver heartbeat. Check its power and network connection.');
      lastReceiverOnline = receiverOnline;
    }
    message('camera-state', snapshot.camera.state.toUpperCase());
    message('camera-device', snapshot.camera.devices?.[0]?.name || 'NO CAMERA DETECTED');
    message('camera-fps', `${snapshot.camera.fps || 0} FPS`);
    message('camera-brightness', `${Math.round((snapshot.camera.brightness || 0) * 100)}% SIGNAL`);
    message('camera-feedback', snapshot.camera.message);
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
    else if (game === 'stack_up') message('buttons-feedback', 'Send one movement at a time, then watch the virtual discs on Mission.');
    for (const color of ['red', 'blue']) {
      const button = document.querySelector(`[data-setup-gate="${color}"]`);
      const active = Boolean(snapshot.robot?.assist?.[color]);
      button.textContent = `${active ? 'RAISE' : 'LOWER'} ${color.toUpperCase()}`;
      button.setAttribute('aria-pressed', String(active));
      button.disabled = snapshot.camera.state === 'capturing';
    }
    message('test-state', snapshot.test?.ready ? 'READY SIGNAL SEEN' : snapshot.test?.armed ? 'WATCHING' : 'WAITING');
    message('test-feedback', snapshot.test?.ready ? 'The camera decoded a complete R.O.B. ready-light signal from this game.' :
      snapshot.test?.armed ? 'Waiting for a complete ready-light signal. Keep the flash area inside the green frame.' :
      'Select a game, start the camera, and arm the check while the game shows Test mode.');
    if (snapshot.camera.state === 'capturing') frame();
  }
  async function act(path, data, feedback, success) {
    try { render(await api(path, data)); if (feedback && success) message(feedback, success); }
    catch (error) { message(feedback || 'setup-connection', error.message); }
  }
  async function poll() {
    if (polling) return;
    polling = true;
    try { render(await api('/api/state')); }
    catch (error) {
      state = null;
      $('pair-connected').hidden = true;
      $('pair-details').hidden = true;
      message('setup-connection', error.message);
      message('pair-link', 'CONTROLLER OFFLINE');
      message('pair-feedback', 'The UNO Q controller is unavailable. Start R.O.B. Vision in App Lab.');
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
  $('pair-change').addEventListener('click', () => { pairExpanded = true; if (state) render(state); });
  $('pair-cancel').addEventListener('click', () => { pairExpanded = false; if (state) render(state); });
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
  document.querySelectorAll('[data-setup-gate]').forEach(button => button.addEventListener('click', () => {
    const color = button.dataset.setupGate;
    act('/api/gate-assist', { color, pressed: color === 'all' ? false : !state?.robot?.assist?.[color] }, 'buttons-feedback', 'Gate state updated. Check the game screen.');
  }));
  document.querySelectorAll('[data-setup-command]').forEach(button => button.addEventListener('click', () => {
    act('/api/command', { command: button.dataset.setupCommand }, 'buttons-feedback', 'Command sent to virtual R.O.B.');
  }));
  window.addEventListener('pagehide', clearFrame);
  poll();
  setInterval(poll, 1000);
})();
