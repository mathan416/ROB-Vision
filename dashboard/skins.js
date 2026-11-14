/* Artwork stays separate from the movement model. Every optional slot has a built-in fallback. */
(() => {
  'use strict';
  const ns = 'http://www.w3.org/2000/svg';
  const params = new URLSearchParams(location.search);
  const preview = params.get('skinPreview');
  if (preview) document.body.classList.add('skin-preview');
  let selected = 'built-in';
  let assets = {};
  let revision = -1;
  const $ = id => document.getElementById(id);
  const url = slot => assets[slot] && selected !== 'built-in'
    ? `/api/skins/${selected}/asset/${slot}` : null;
  const has = slot => Boolean(url(slot));
  const image = (id, slot) => {
    const element = $(id);
    if (!element) return;
    if (!element.dataset.skinErrorBound) {
      element.dataset.skinErrorBound = 'yes';
      element.addEventListener('error', () => {
        if (assets[slot]) { delete assets[slot]; apply(); }
      });
    }
    const source = url(slot);
    if (source) element.setAttribute('href', source + `?v=${Date.now()}`);
    else element.removeAttribute('href');
    if (source) element.removeAttribute('hidden');
    else element.setAttribute('hidden', '');
    element.style.display = source ? '' : 'none';
  };
  const replaceGroup = (id, slot, box) => {
    const group = $(id);
    if (!group) return;
    let art = group.querySelector(':scope > .skin-art');
    if (!art) {
      art = document.createElementNS(ns, 'image');
      art.id = `skin-${id}`;
      art.classList.add('skin-art');
      for (const [key, value] of Object.entries(box)) art.setAttribute(key, value);
      group.append(art);
    }
    group.classList.toggle('skin-replaced', has(slot));
    image(art.id, slot);
  };
  const armSlots = ['left_upper_arm', 'left_forearm', 'right_upper_arm', 'right_forearm'];
  for (const slot of armSlots) {
    const art = document.createElementNS(ns, 'image');
    art.id = `skin-${slot.replaceAll('_', '-')}`;
    art.classList.add('skin-art', 'skin-arm');
    art.setAttribute('x', '0'); art.setAttribute('y', '0');
    art.setAttribute('width', '64'); art.setAttribute('height', '128');
    art.style.display = 'none';
    $('arm-carriage').append(art);
  }
  function apply() {
    for (const slot of ['background', 'floor', 'body', 'head', 'platform', 'gyro_linkage', 'left_hand', 'right_hand']) {
      image(`skin-${slot.replaceAll('_', '-')}`, slot);
    }
    $('stage-ground').style.display = has('floor') ? 'none' : '';
    $('column-visual').style.display = has('body') ? 'none' : '';
    $('platform-art').style.display = has('platform') ? 'none' : '';
    $('gyro-linkage').style.display = has('gyro_linkage') ? 'none' : '';
    $('default-head').style.display = has('head') ? 'none' : '';
    for (const side of ['left', 'right']) {
      $(`${side}-hand`).querySelector('.default-hand').style.display = has(`${side}_hand`) ? 'none' : '';
    }
    for (const slot of armSlots) image(`skin-${slot.replaceAll('_', '-')}`, slot);
    for (const [id, slot, box] of [
      ['scene-second-dock', 'holder_far', {x: 102, y: 477, width: 86, height: 66}],
      ['scene-source-gyro', 'holder_near', {x: 180, y: 505, width: 90, height: 66}],
      ['scene-spinner', 'spinner', {x: 407, y: 485, width: 78, height: 62}],
      ['scene-target-gyro', 'red_pad', {x: 253, y: 522, width: 64, height: 37}],
      ['scene-blue-tray', 'blue_pad', {x: 338, y: 522, width: 64, height: 37}],
      ['stack-linkage', 'stack_linkage', {x: 107, y: 483, width: 430, height: 83}],
    ]) replaceGroup(id, slot, box);
    for (let i = 1; i <= 5; i += 1)
      replaceGroup(`stack-tray-${i}`, 'stack_tray', {x: -38, y: -14, width: 76, height: 78});
    window.RobDashboard?.refreshSkin?.();
  }
  function updateArms(points) {
    for (const [slot, start, end] of [
      ['left_upper_arm', points.leftShoulder, points.leftElbow],
      ['left_forearm', points.leftElbow, points.leftHand],
      ['right_upper_arm', points.rightShoulder, points.rightElbow],
      ['right_forearm', points.rightElbow, points.rightHand],
    ]) {
      if (!has(slot)) continue;
      const dx = end[0] - start[0], dy = end[1] - start[1];
      const length = Math.hypot(dx, dy);
      const angle = Math.atan2(-dx, dy) * 180 / Math.PI;
      $(`skin-${slot.replaceAll('_', '-')}`).setAttribute('transform',
        `translate(${start[0]} ${start[1]}) rotate(${angle}) scale(1 ${length / 112}) translate(-32 -8)`);
    }
  }
  async function load(force = false) {
    try {
      const response = await fetch('/api/skins', {cache: 'no-store'});
      if (!response.ok) return false;
      const list = await response.json();
      const target = preview || list.active;
      const record = list.skins.find(item => item.id === target) || list.skins[0];
      if (!record) return false;
      if (force || record.id !== selected || record.revision !== revision ||
          JSON.stringify(record.assets) !== JSON.stringify(assets)) {
        selected = record.id; assets = {...(record.assets || {})};
        revision = record.revision ?? 0;
        apply();
      }
      return true;
    } catch (_) {
      // The local static preview uses original Buddy.
      return false;
    }
  }
  window.RobSkins = {has, url, updateArms, load};
  load();
  const refreshButton = $('skin-refresh');
  if (refreshButton) refreshButton.addEventListener('click', async () => {
    refreshButton.disabled = true;
    refreshButton.textContent = 'CHECKING BUDDY…';
    const okay = await load(true);
    refreshButton.textContent = okay ? 'BUDDY UPDATED ↻' : 'REFRESH FAILED ↻';
    refreshButton.disabled = false;
  });
})();
