const test = require('node:test');
const assert = require('node:assert/strict');
const stack = require('../dashboard/stack-model.js');

function commands(state, ...items) {
  for (const command of items.flat()) {
    const result = stack.apply(state, command);
    assert.equal(result.ok, true, `${command}: ${result.reason}`);
  }
}

test('gripping below the top carries an ordered disc segment', () => {
  const state = stack.create();
  commands(state, 'DOWN', 'DOWN', 'DOWN', 'CLOSE');
  assert.deepEqual(state.held, ['blue', 'white', 'red']);
  assert.deepEqual(state.trays[2], ['green', 'yellow']);
  commands(state, 'UP', 'UP', 'UP', 'RIGHT', ...Array(5).fill('DOWN'), 'OPEN');
  assert.deepEqual(state.trays[3], ['blue', 'white', 'red']);
  assert.deepEqual(state.held, []);
  assert.equal(stack.valid(state), true);
});

test('invalid placement preserves all discs and the closed grip', () => {
  const state = stack.create();
  commands(state, 'DOWN', 'CLOSE', 'UP', 'RIGHT');
  const before = stack.snapshot(state);
  const result = stack.apply(state, 'OPEN');
  assert.equal(result.ok, false);
  assert.deepEqual(stack.snapshot(state), before);
  assert.equal(state.grip, 'closed');
});

test('carried discs cannot descend into an occupied tray', () => {
  const state = stack.create();
  commands(state, 'DOWN', 'CLOSE', 'UP', 'RIGHT', ...Array(5).fill('DOWN'), 'OPEN', ...Array(5).fill('UP'), 'LEFT', 'DOWN', 'DOWN', 'DOWN', 'CLOSE', 'UP', 'UP', 'UP', 'RIGHT', 'DOWN', 'DOWN', 'DOWN', 'DOWN');
  assert.equal(state.height, 2);
  assert.deepEqual(state.held, ['blue', 'white']);
  const before = stack.snapshot(state);
  const result = stack.apply(state, 'DOWN');
  assert.equal(result.ok, false);
  assert.deepEqual(stack.snapshot(state), before);
});

test('station and height boundaries reject moves without changing state', () => {
  const state = stack.create();
  commands(state, 'LEFT', 'LEFT');
  const before = stack.snapshot(state);
  assert.equal(stack.apply(state, 'LEFT').ok, false);
  assert.equal(stack.apply(state, 'UP').ok, false);
  assert.deepEqual(stack.snapshot(state), before);
});

test('five discs remain accounted for throughout the scripted transfer', () => {
  const state = stack.create();
  const sequence = ['DOWN', 'CLOSE', 'UP', 'RIGHT', ...Array(5).fill('DOWN'), 'OPEN', ...Array(5).fill('UP'), 'LEFT', ...Array(3).fill('DOWN'), 'CLOSE', ...Array(3).fill('UP'), 'LEFT', ...Array(5).fill('DOWN'), 'OPEN'];
  for (const command of sequence) {
    commands(state, command);
    assert.equal(stack.valid(state), true);
  }
  assert.deepEqual(state.trays, [[], ['blue', 'white'], ['green', 'yellow'], ['red'], []]);
});
