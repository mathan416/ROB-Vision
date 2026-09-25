(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const status = window.RobStatus;
  let state = null;
  let polling = false;
  let pairExpanded = false;
  let lastReceiverOnline = null;
  let linkChecking = false;
  let previewActive = false;
  let previewTimer = null;
  let removingId = null;
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
  function renderConsoles(consoles) {
    const list = $('console-list');
    const rows = Array.isArray(consoles) ? consoles : [];
    const signature = JSON.stringify(rows.map(item => [item.id, item.online, item.active, item.host, item.legacy, removingId]));
    if (list.dataset.signature === signature) return;
    list.dataset.signature = signature;
    list.replaceChildren();
    message('console-count', `${rows.length} SAVED`);
    if (!rows.length) {
      const empty = document.createElement('p');
      empty.textContent = 'No consoles paired yet.';
      list.append(empty);
      return;
    }
    for (const item of rows) {
      const row = document.createElement('div');
      row.className = `console-item${item.active ? ' active' : ''}`;
      const identity = document.createElement('div');
      identity.className = 'console-identity';
      const name = document.createElement('span');
      name.className = 'console-name';
      name.textContent = item.name;
      const host = document.createElement('span');
      host.className = 'console-host';
      host.textContent = item.host || (item.legacy ? 'Older shared pairing' : 'Console address unknown');
      identity.append(name, host);
      const meta = document.createElement('div');
      meta.className = 'console-meta';
      const badge = document.createElement('span');
      badge.className = `console-state${item.online ? ' online' : ''}`;
      badge.textContent = item.active ? 'PLAYING' : item.online ? 'ONLINE' : 'OFFLINE';
      meta.append(badge);
      if (removingId === item.id) {
        const confirm = document.createElement('button');
        confirm.type = 'button';
        confirm.className = 'console-confirm';
        confirm.textContent = 'CONFIRM REMOVE';
        confirm.addEventListener('click', async () => {
          confirm.disabled = true;
          try {
            render(await api('/api/consoles/remove', { id: item.id }));
            message('pair-feedback', `${item.name} pairing removed. Its saved key no longer works.`);
            removingId = null;
            if (state) render(state);
          } catch (error) { message('pair-feedback', error.message); confirm.disabled = false; }
        });
        const cancel = document.createElement('button');
        cancel.type = 'button';
        cancel.className = 'console-remove';
        cancel.textContent = 'CANCEL';
        cancel.addEventListener('click', () => { removingId = null; if (state) render(state); });
        meta.append(confirm, cancel);
      } else {
        const remove = document.createElement('button');
        remove.type = 'button';
        remove.className = 'console-remove';
        remove.textContent = 'REMOVE';
        remove.setAttribute('aria-label', `Remove ${item.name} pairing ${item.host || ''}`);
        remove.addEventListener('click', () => { removingId = item.id; if (state) render(state); });
        meta.append(remove);
      }
      row.append(identity, meta);
      list.append(row);
    }
  }
  function render(snapshot) {
    state = snapshot;
    message('setup-connection', status.connection(snapshot));
    $('setup-connection').closest('.top-status').dataset.connection = 'connected';
    const consoles = snapshot.link?.consoles || [];
    renderConsoles(consoles);
    const onlineCount = consoles.filter(item => item.online).length;
    const receiverOnline = onlineCount > 0 || Boolean(snapshot.link?.online);
    message('pair-link', consoles.length > 1 ? `${onlineCount} OF ${consoles.length} ONLINE` : status.receiver(snapshot));
    $('pair-link').dataset.state = receiverOnline ? 'online' : 'offline';
    $('pair-connected').hidden = !receiverOnline || pairExpanded;
    $('pair-details').hidden = receiverOnline && !pairExpanded;
    $('pair-cancel').hidden = !receiverOnline;
    if (receiverOnline !== lastReceiverOnline) {
      message('pair-feedback', receiverOnline ? 'Console receiver is online. Continue to the game-frame check.' :
        'No recent console receiver heartbeat. Check its power and network connection.');
      lastReceiverOnline = receiverOnline;
    }
    message('frame-state', status.frames(snapshot));
    message('frame-feedback', snapshot.input?.frame_hook ?
      'The selected game is sending rendered frames to R.O.B. Vision. Automatic movement is ready.' :
      'Launch Gyromite or Stack-Up with its R.O.B. Vision emulator choice to link game frames.');
    const game = snapshot.game;
    message('buttons-mode', game ? game.replace('_', '-').toUpperCase() : 'SELECT A GAME');
    $('setup-gates').hidden = game !== 'gyromite';
    $('setup-stack').hidden = game !== 'stack_up';
    if (game === 'gyromite') message('buttons-feedback', 'Use the red and blue buttons to test the matching gates.');
    else if (game === 'stack_up') message('buttons-feedback', 'Send one movement at a time, then watch the virtual blocks on Mission.');
    for (const color of ['red', 'blue']) {
      const button = document.querySelector(`[data-setup-gate="${color}"]`);
      const active = Boolean(snapshot.robot?.assist?.[color]);
      button.textContent = `${active ? 'RAISE' : 'LOWER'} ${color.toUpperCase()}`;
      button.setAttribute('aria-pressed', String(active));
    }
    const flashing = Boolean(snapshot.test?.flash_active);
    const ready = Boolean(snapshot.test?.ready) && !flashing;
    $('test-light').classList.toggle('flashing', flashing || previewActive && !ready);
    $('test-light').classList.toggle('ready', ready);
    message('test-led-label', flashing ? 'R.O.B. LIGHT FLASHING' : ready ? 'R.O.B. LIGHT ON' : previewActive ? 'PREVIEW ONLY · FLASHING' : 'R.O.B. LIGHT OFF');
    message('test-state', status.test(snapshot));
    message('test-feedback', flashing ? 'Test-mode optical signal detected. R.O.B.’s red light blinks; his arms do not move.' :
      ready ? 'A separate ready-light command was decoded. R.O.B.’s red light stays on; his arms do not move.' :
      previewActive ? 'This is a visual preview only. No game signal was detected.' :
      snapshot.test?.armed ? 'Waiting for the Test-mode signal from linked game frames.' :
      'Select a game, link its frames, and arm the check while the game shows Test mode.');
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
      message('pair-link', 'CONSOLE UNKNOWN');
      renderConsoles([]);
      $('pair-link').dataset.state = 'unknown';
      message('frame-state', 'GAME FRAMES UNKNOWN');
      message('test-state', 'SIGNAL UNKNOWN');
      message('buttons-mode', 'SELECT A GAME');
      $('setup-gates').hidden = true; $('setup-stack').hidden = true;
      message('pair-feedback', preview ? 'Local preview only. Open Setup on the UNO Q for live checks.' : 'The UNO Q controller is unavailable. Start R.O.B. Vision in App Lab.');
      message('frame-feedback', 'Game-frame status is unavailable until the controller reconnects.');
      message('test-feedback', 'Game signal status is unavailable until the controller reconnects.');
    } finally { polling = false; }
  }
  async function checkLink() {
    if (linkChecking) return;
    linkChecking = true;
    $('pair-refresh').disabled = true;
    $('pair-refresh-offline').disabled = true;
    message('pair-feedback', 'Checking the latest console receiver heartbeat…');
    try {
      const snapshot = await api('/api/state');
      render(snapshot);
      const checkedAt = new Date().toLocaleTimeString([], { hour: 'numeric', minute: '2-digit', second: '2-digit' });
      const consoles = snapshot.link?.consoles || [];
      const online = consoles.filter(item => item.online).length;
      message('pair-feedback', online ?
        `Checked ${checkedAt}: ${online} of ${consoles.length} paired consoles online.` :
        `Checked ${checkedAt}: no paired console is online. Check power and network.`);
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
      message('pair-feedback', result.paired ? 'Pairing complete. Waiting for the console receiver to reconnect.' : 'Pairing was not confirmed.');
      if (result.paired) pairExpanded = false;
      $('pair-code').value = '';
      $('pair-fingerprint').value = '';
      poll();
    } catch (error) { message('pair-feedback', error.message); }
    finally { button.disabled = false; }
  });
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
  window.addEventListener('pagehide', () => { if (previewTimer) clearTimeout(previewTimer); });
  poll();
  setInterval(poll, 1000);
})();
