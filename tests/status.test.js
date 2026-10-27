const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const context = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../dashboard/status.js'), 'utf8'), context);
const status = context.window.RobStatus;

test('game and frame labels distinguish selection from a frame link', () => {
  const idle = { game: null, input: { frame_hook: true }, link: { consoles: [] } };
  assert.equal(status.connection(idle), 'NO GAME / CONNECTED');
  assert.equal(status.frames(idle), 'GAME FRAMES IDLE');
  assert.equal(status.receiver(idle), 'NO CONSOLE PAIRED');
  assert.equal(status.receiverOnline(idle), false);

  for (const [game, label] of [['gyromite', 'GYROMITE'], ['stack_up', 'STACK-UP']]) {
    const snapshot = { game, input: { frame_hook: false }, link: { consoles: [] } };
    assert.equal(status.connection(snapshot), `${label} / CONNECTED`);
    assert.equal(status.frames(snapshot), 'GAME FRAMES WAITING');
    snapshot.input.frame_hook = true;
    assert.equal(status.frames(snapshot), 'GAME FRAMES LINKED');
  }
});

test('receiver status follows the active console, not another recent check-in', () => {
  const consoles = [
    { name: 'RetroPie', online: false, active: true },
    { name: 'Batocera', online: true, active: false },
    { name: 'Recalbox', online: true, active: false },
  ];
  const snapshot = { game: 'gyromite', link: { online: true, receiver: 'Batocera', consoles } };
  assert.equal(status.receiver(snapshot), 'RETROPIE / WAITING');
  assert.equal(status.receiverOnline(snapshot), false);
  assert.equal(status.controllerDetail(snapshot), 'GAME FRAMES WAITING · RETROPIE / WAITING');
  consoles[0].online = true;
  assert.equal(status.receiver(snapshot), 'RETROPIE / LINKED');
  assert.equal(status.receiverOnline(snapshot), true);
  snapshot.game = null;
  assert.equal(status.receiver(snapshot), '3 OF 3 RECEIVERS LINKED');
});

test('one saved console and an older snapshot retain readable labels', () => {
  for (const name of ['RetroPie', 'Batocera', 'Recalbox']) {
    const snapshot = { link: { consoles: [{ name, online: true }] } };
    assert.equal(status.receiver(snapshot), `${name.toUpperCase()} / LINKED`);
    snapshot.link.consoles[0].online = false;
    assert.equal(status.receiver(snapshot), `${name.toUpperCase()} / WAITING`);
  }
  assert.equal(status.receiver({ link: { receiver: 'RetroPie', online: true } }), 'RETROPIE / LINKED');
});
