const test = require('node:test');
const assert = require('node:assert/strict');
const stack = require('../dashboard/stack-model.js');

function commands(state, ...items) {
  for (const command of items.flat()) {
    const result = stack.apply(state, command);
    assert.equal(result.ok, true, `${command}: ${result.reason}`);
  }
}

test('gripping below the top carries an ordered block segment', () => {
  const state = stack.create();
  commands(state, 'DOWN', 'DOWN', 'DOWN', 'CLOSE');
  assert.deepEqual(state.held, ['blue', 'white', 'red']);
  assert.deepEqual(state.trays[2], ['green', 'yellow']);
  commands(state, 'UP', 'UP', 'UP', 'RIGHT', ...Array(5).fill('DOWN'), 'OPEN');
  assert.deepEqual(state.trays[3], ['blue', 'white', 'red']);
  assert.deepEqual(state.held, []);
  assert.equal(stack.valid(state), true);
});

test('invalid placement preserves all blocks and the closed grip', () => {
  const state = stack.create();
  commands(state, 'DOWN', 'CLOSE', 'UP', 'RIGHT');
  const before = stack.snapshot(state);
  const result = stack.apply(state, 'OPEN');
  assert.equal(result.ok, false);
  assert.deepEqual(stack.snapshot(state), before);
  assert.equal(state.grip, 'closed');
});

test('carried blocks cannot descend into an occupied tray', () => {
  const state = stack.create();
  commands(state, 'DOWN', 'CLOSE', 'UP', 'RIGHT', ...Array(5).fill('DOWN'), 'OPEN', ...Array(5).fill('UP'), 'LEFT', 'DOWN', 'DOWN', 'DOWN', 'CLOSE', 'UP', 'UP', 'UP', 'RIGHT', 'DOWN', 'DOWN', 'DOWN', 'DOWN');
  assert.equal(state.height, 2);
  assert.deepEqual(state.held, ['blue', 'white']);
  const before = stack.snapshot(state);
  const result = stack.apply(state, 'DOWN');
  assert.equal(result.ok, false);
  assert.deepEqual(stack.snapshot(state), before);
});

test('sideways moves clear destination stacks with open, closed, and carrying hands', () => {
  for (const [command, targetIndex, targetStation] of [['LEFT', 1, 2], ['RIGHT', 3, 4]]) {
    for (let stackHeight = 1; stackHeight <= 5; stackHeight += 1) {
      for (const grip of ['open', 'closed']) {
        const state = { trays: [[], [], stack.COLORS.slice(stackHeight), [], []], held: [],
          station: 3, height: stackHeight, grip };
        state.trays[targetIndex] = stack.COLORS.slice(0, stackHeight);
        const before = stack.snapshot(state);
        const result = stack.apply(state, command);
        assert.equal(result.reason, `Raise the hands to level ${stackHeight + 1} to clear Tray ${targetStation}.`);
        assert.deepEqual(stack.snapshot(state), before);
        commands(state, 'UP', command);
        assert.equal(state.station, targetStation);
      }
      if (stackHeight < 5) {
        const state = { trays: [[], [], stack.COLORS.slice(stackHeight, -1), [], []],
          held: [stack.COLORS.at(-1)], station: 3, height: stackHeight, grip: 'closed' };
        state.trays[targetIndex] = stack.COLORS.slice(0, stackHeight);
        const before = stack.snapshot(state);
        assert.equal(stack.apply(state, command).ok, false);
        assert.deepEqual(stack.snapshot(state), before);
        commands(state, 'UP', command);
      }
    }
  }
});

test('closed empty hands stop at a stack while open hands descend to pick a block', () => {
  for (let stackHeight = 1; stackHeight <= 5; stackHeight += 1) {
    const trays = [stack.COLORS.slice(stackHeight), [], stack.COLORS.slice(0, stackHeight), [], []];
    const closed = { trays, held: [], station: 3, height: stackHeight + 1, grip: 'closed' };
    const before = stack.snapshot(closed);
    assert.match(stack.apply(closed, 'DOWN').reason, /Open the hands/);
    assert.deepEqual(stack.snapshot(closed), before);
    const open = { ...stack.snapshot(closed), grip: 'open' };
    commands(open, 'DOWN', 'CLOSE');
    assert.deepEqual(open.held, [stack.COLORS[stackHeight - 1]]);
  }
});

test('station and height boundaries reject moves without changing state', () => {
  const state = stack.create();
  commands(state, 'LEFT', 'LEFT');
  const before = stack.snapshot(state);
  assert.equal(stack.apply(state, 'LEFT').ok, false);
  assert.equal(stack.apply(state, 'UP').ok, false);
  assert.deepEqual(stack.snapshot(state), before);
});

test('five blocks remain accounted for throughout the scripted transfer', () => {
  const state = stack.create();
  const sequence = ['DOWN', 'CLOSE', 'UP', 'RIGHT', ...Array(5).fill('DOWN'), 'OPEN', ...Array(5).fill('UP'), 'LEFT', ...Array(3).fill('DOWN'), 'CLOSE', ...Array(3).fill('UP'), 'LEFT', ...Array(5).fill('DOWN'), 'OPEN'];
  for (const command of sequence) {
    commands(state, command);
    assert.equal(stack.valid(state), true);
  }
  assert.deepEqual(state.trays, [[], ['blue', 'white'], ['green', 'yellow'], ['red'], []]);
});
