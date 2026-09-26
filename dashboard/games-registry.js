(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const editor = $('registry-json');
  const chooser = $('registry-console');
  const notice = $('registry-feedback');
  let loaded = '';
  let revision = null;
  let hasBackup = false;
  let busy = false;
  let selection = '';
  let consoleSignature = '';

  function controls() {
    for (const button of document.querySelectorAll('.registry-card button')) {
      button.disabled = busy || !selection || (button.id !== 'registry-reload' && !revision) ||
        (button.id === 'registry-restore' && !hasBackup);
    }
  }
  async function request(action, extra = {}) {
    const response = await fetch('/api/games', {
      method: 'POST', cache: 'no-store', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ console_id: selection, action, revision, ...extra })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'Could not reach the paired console registry.');
    return result;
  }
  async function run(action) {
    if (busy || !selection) return;
    if (action === 'read' && revision && editor.value !== loaded &&
        !confirm('Discard unsaved registry edits and reload from the console?')) return;
    if (action === 'restore' && !confirm('Replace this console’s mappings with its previous save?')) return;
    busy = true; controls();
    try {
      if (action === 'format') {
        editor.value = JSON.stringify(JSON.parse(editor.value), null, 2) + '\n';
        notice.textContent = 'Formatted. Save to apply these mappings.';
      } else if (action === 'download') {
        const url = URL.createObjectURL(new Blob([loaded], { type: 'application/json' }));
        const anchor = document.createElement('a');
        anchor.href = url; anchor.download = 'rob-vision-games-backup.json'; anchor.click();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
        notice.textContent = 'Downloaded the last verified registry from this console.';
      } else {
        const result = await request(action, { document: editor.value });
        if (action === 'validate') {
          notice.textContent = 'Valid Gyromite and Stack-Up mappings. Save to apply them.';
        } else {
          editor.value = result.document;
          loaded = result.document;
          revision = result.revision;
          hasBackup = result.has_backup;
          notice.textContent = action === 'save' ? 'Saved on the console. New mappings apply at the next game launch.' :
            action === 'restore' ? 'Previous mappings restored on the console.' : 'Installed console mappings loaded.';
        }
      }
    } catch (error) {
      notice.textContent = `${error.message} Your draft is still here.`;
    } finally { busy = false; controls(); }
  }
  function setConsoles(consoles) {
    const rows = (consoles || []).filter(item => !item.legacy);
    const signature = JSON.stringify(rows.map(item => [item.id, item.host, item.online, item.active]));
    if (signature === consoleSignature) return;
    consoleSignature = signature;
    const previous = chooser.value;
    chooser.replaceChildren(new Option('Choose a paired console', ''));
    for (const item of rows) chooser.add(new Option(`${item.name} · ${item.host}${item.online ? ' · online' : ''}`, item.id));
    const chosen = rows.some(item => item.id === previous) ? previous :
      (rows.find(item => item.active) || rows.find(item => item.online) || rows[0])?.id || '';
    chooser.value = chosen;
    if (chosen !== selection) select(chosen);
  }
  function select(id) {
    selection = id;
    revision = null;
    loaded = '';
    editor.value = '';
    hasBackup = false;
    controls();
    if (id) { notice.textContent = 'Loading the installed console registry…'; run('read'); }
    else notice.textContent = 'Pair a console to edit its game mappings.';
  }
  function editConsole(id) {
    if (!Array.from(chooser.options).some(option => option.value === id)) return false;
    if (id !== selection && revision && editor.value !== loaded &&
        !confirm('Discard unsaved registry edits?')) return false;
    chooser.value = id;
    if (id !== selection || !revision) select(id);
    return true;
  }
  chooser.addEventListener('change', () => {
    if (revision && editor.value !== loaded && !confirm('Discard unsaved registry edits?')) {
      chooser.value = selection; return;
    }
    select(chooser.value);
  });
  for (const [id, action] of Object.entries({
    'registry-validate': 'validate', 'registry-format': 'format', 'registry-save': 'save',
    'registry-reload': 'read', 'registry-restore': 'restore', 'registry-download': 'download'
  })) $(id).addEventListener('click', () => run(action));
  window.addEventListener('beforeunload', event => {
    if (revision && editor.value !== loaded) { event.preventDefault(); event.returnValue = ''; }
  });
  window.RobGamesRegistry = { setConsoles, editConsole };
  controls();
})();
