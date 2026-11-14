(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const labels = {
    head: 'Head', body: 'Body', left_upper_arm: 'Left upper arm', left_forearm: 'Left forearm',
    right_upper_arm: 'Right upper arm', right_forearm: 'Right forearm', left_hand: 'Left hand',
    right_hand: 'Right hand', background: 'Stage background', floor: 'Floor', platform: 'Platform',
    gyro_linkage: 'Gyromite links', holder_far: 'Far gyro holder', holder_near: 'Near gyro holder',
    spinner: 'Spinner', red_pad: 'Red pad', blue_pad: 'Blue pad',
    stack_linkage: 'Stack-Up links', stack_tray: 'Stack-Up tray'
  };
  let library = {active: 'built-in', skins: [], slots: Object.keys(labels)};
  const feedback = value => { $('skin-feedback').textContent = value; };
  const chosen = () => $('skin-library').value;
  const record = () => library.skins.find(item => item.id === chosen());
  async function request(path, method = 'GET', body, contentType = 'application/json') {
    const options = {method, cache: 'no-store'};
    if (body !== undefined) { options.headers = {'Content-Type': contentType}; options.body = body; }
    const response = await fetch(path, options);
    if (!response.ok) {
      let reason = 'Skin request failed.';
      try { reason = (await response.json()).error || reason; } catch (_) { /* Keep default error. */ }
      throw new Error(reason);
    }
    return response;
  }
  function updateControls() {
    const id = chosen();
    if (!id) return;
    const original = id === 'built-in';
    for (const control of ['skin-upload', 'skin-delete', 'skin-remove-part', 'skin-export'])
      $(control).disabled = original;
    $('skin-activate').disabled = id === library.active;
    const slot = $('skin-slot').value;
    $('skin-remove-part').disabled = original || !record()?.assets?.[slot];
  }
  function preview() {
    const id = chosen();
    if (!id) return;
    const query = new URLSearchParams({skinPreview: id, skinMode: $('skin-mode').value,
      skinPose: $('skin-pose').value, refresh: String(Date.now())});
    $('skin-preview').src = `index.html?${query}`;
    updateControls();
  }
  function showList(preferred) {
    const menu = $('skin-library');
    const before = preferred || menu.value || library.active;
    menu.replaceChildren();
    for (const item of library.skins) {
      const option = new Option(`${item.name} — ${item.artist}${item.id === library.active ? ' (ACTIVE)' : ''}`, item.id);
      menu.add(option);
    }
    menu.value = library.skins.some(item => item.id === before) ? before : library.active;
    preview();
  }
  async function refresh(preferred) {
    const latest = await (await request('/api/skins')).json();
    const changed = JSON.stringify(latest) !== JSON.stringify(library);
    library = latest;
    if (!$('skin-slot').options.length) {
      for (const slot of library.slots) $('skin-slot').add(new Option(labels[slot] || slot, slot));
    }
    if (changed || preferred) showList(preferred);
  }
  async function perform(action) {
    try { await action(); }
    catch (error) { feedback(error.message); }
  }
  $('skin-library').addEventListener('change', preview);
  $('skin-slot').addEventListener('change', updateControls);
  $('skin-mode').addEventListener('change', preview);
  $('skin-pose').addEventListener('change', preview);
  $('skin-refresh-list').addEventListener('click', () => perform(async () => {
    await refresh(chosen());
    feedback('Skin list and preview refreshed.');
  }));
  $('skin-guide-toggle').addEventListener('change', () => {
    $('skin-placement-guide').hidden = !$('skin-guide-toggle').checked;
  });
  $('skin-create').addEventListener('click', () => perform(async () => {
    const body = JSON.stringify({name: $('skin-name').value, artist: $('skin-artist').value});
    const result = await (await request('/api/skins/create', 'POST', body)).json();
    await refresh(result.id);
    feedback('Skin created. Add any parts you want to change, then preview and activate it.');
  }));
  $('skin-upload').addEventListener('click', () => perform(async () => {
    const file = $('skin-file').files[0];
    if (!file) throw new Error('Choose a PNG or SVG file for this part.');
    const kind = file.name.toLowerCase().endsWith('.png') ? 'image/png' :
      file.name.toLowerCase().endsWith('.svg') ? 'image/svg+xml' : null;
    if (!kind) throw new Error('Artwork must be PNG or SVG.');
    const id = chosen(), slot = $('skin-slot').value;
    await request(`/api/skins/${id}/asset/${slot}`, 'POST', file, kind);
    await refresh(id);
    feedback(`${labels[slot]} saved. Preview its movement before activating the skin.`);
  }));
  $('skin-remove-part').addEventListener('click', () => perform(async () => {
    const id = chosen(), slot = $('skin-slot').value;
    await request(`/api/skins/${id}/remove-asset/${slot}`, 'POST', '{}');
    await refresh(id);
    feedback(`${labels[slot]} now uses original Buddy artwork.`);
  }));
  $('skin-activate').addEventListener('click', () => perform(async () => {
    const id = chosen();
    await request(`/api/skins/${id}/activate`, 'POST', '{}');
    await refresh(id);
    feedback('Skin activated. Other open Mission pages can use Refresh Buddy to see it.');
  }));
  $('skin-delete').addEventListener('click', () => perform(async () => {
    const id = chosen();
    if (!confirm('Remove this skin from the UNO Q? Export a ZIP first if you want to keep it.')) return;
    await request(`/api/skins/${id}/delete`, 'POST', '{}');
    await refresh('built-in');
    feedback('Skin removed.');
  }));
  $('skin-export').addEventListener('click', () => {
    if (chosen() !== 'built-in') location.href = `/api/skins/${chosen()}/export`;
  });
  $('skin-import').addEventListener('click', () => perform(async () => {
    const file = $('skin-pack').files[0];
    if (!file || !file.name.toLowerCase().endsWith('.zip')) throw new Error('Choose a ZIP skin pack.');
    const result = await (await request('/api/skins/import', 'POST', file, 'application/zip')).json();
    await refresh(result.id);
    feedback('Skin pack imported. Preview it, then choose Use this skin.');
  }));
  refresh().catch(() => feedback('Connect to the UNO Q to manage skins. The original Buddy still works locally.'));
})();
