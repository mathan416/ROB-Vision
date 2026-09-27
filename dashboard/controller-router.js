(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const chooser = $('router-console');
  const inventory = $('router-inventory');
  const feedback = $('router-feedback');
  let selection = '', revision = null, snapshot = null, busy = false;
  let signature = '';

  function controls() {
    for (const button of document.querySelectorAll('.router-card button')) {
      button.disabled = busy || !selection || !revision ||
        (button.id === 'router-rollback' && !snapshot?.has_backup);
    }
  }
  function setConsoles(consoles) {
    const rows = (consoles || []).filter(item => !item.legacy);
    const next = JSON.stringify(rows.map(item => [item.id, item.host, item.online]));
    if (next === signature) return;
    signature = next;
    const previous = chooser.value;
    chooser.replaceChildren(new Option('Choose a console', ''));
    for (const item of rows) chooser.add(new Option(`${item.name} · ${item.host}`, item.id));
    chooser.value = rows.some(item => item.id === previous) ? previous :
      (rows.find(item => item.online) || rows[0])?.id || '';
    if (chooser.value !== selection) select(chooser.value);
  }
  async function request(action, extra = {}) {
    const response = await fetch('/api/router', { method: 'POST', cache: 'no-store',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ console_id: selection, action, revision, ...extra }) });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Controller Router is unavailable.');
    return result;
  }
  function render(result) {
    snapshot = result; revision = result.revision;
    inventory.replaceChildren();
    const sources = result.inventory || [];
    if (!sources.length) {
      const empty = document.createElement('p');
      empty.textContent = 'No configured controllers are visible. Configure a gamepad in EmulationStation, then reload.';
      inventory.append(empty);
    }
    for (const source of sources) {
      const row = document.createElement('div'); row.className = 'router-source';
      const label = document.createElement('div');
      const name = document.createElement('strong'); name.textContent = source.name;
      const state = document.createElement('span');
      state.textContent = source.connected ?
        (source.mapping_status === 'refreshed' ? 'Connected · mapping updated' : 'Connected') : 'Unavailable';
      label.append(name, state);
      const assigned = document.createElement('select');
      assigned.dataset.sourceId = source.id;
      const buddy = source.name === 'R.O.B. Vision Controller 2';
      if (buddy) {
        assigned.add(new Option('Player 2 · Buddy', '2'));
        assigned.disabled = true;
      } else {
        for (const [value, title] of [['', 'Unassigned'], ['1', 'Player 1'],
          ['2', 'Player 2'], ['3', 'Player 3'], ['4', 'Player 4']]) assigned.add(new Option(title, value));
        assigned.value = source.assigned_player ? String(source.assigned_player) : '';
      }
      row.append(label, assigned); inventory.append(row);
    }
    controls();
  }
  function draft() {
    const players = new Map();
    for (const select of inventory.querySelectorAll('select[data-source-id]')) {
      if (!select.value) continue;
      const number = Number(select.value);
      if (!players.has(number)) players.set(number, { player: number, sources: [] });
      players.get(number).sources.push(select.dataset.sourceId);
    }
    return { players: Array.from(players.values()).sort((a, b) => a.player - b.player),
      virtualglove_player: snapshot.config.virtualglove_player };
  }
  async function run(action) {
    if (busy || !selection) return;
    if (action === 'rollback' && !confirm('Restore the previous controller assignments on this console?')) return;
    busy = true; controls();
    try {
      const result = await request(action, action === 'save' ? { config: draft() } :
        action === 'check' ? { watch_ms: 5000 } : {});
      render(result);
      if (action === 'check') {
        const activity = Object.values(result.activity || {}).flat();
        feedback.textContent = activity.length ? `Detected: ${[...new Set(activity)].join(', ')}.` :
          'No controller input was detected during the test.';
      } else feedback.textContent = action === 'save' ? 'Assignments saved. Launch a game to use them.' :
        action === 'rollback' ? 'Previous assignments restored.' : 'Console assignments loaded.';
    } catch (error) { feedback.textContent = error.message; }
    finally { busy = false; controls(); }
  }
  function select(id) {
    selection = id; revision = null; snapshot = null; inventory.replaceChildren(); controls();
    feedback.textContent = id ? 'Loading controller assignments…' : 'Pair a console to configure its controllers.';
    if (id) run('read');
  }
  chooser.addEventListener('change', () => select(chooser.value));
  for (const [id, action] of Object.entries({ 'router-save': 'save', 'router-check': 'check',
    'router-reload': 'read', 'router-rollback': 'rollback' })) {
    $(id).addEventListener('click', () => run(action));
  }
  window.RobControllerRouter = { setConsoles, editConsole(id) {
    if (!Array.from(chooser.options).some(option => option.value === id)) return false;
    chooser.value = id; select(id); return true;
  } };
  controls();
})();
