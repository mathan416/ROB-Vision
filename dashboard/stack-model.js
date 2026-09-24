/* Stack-Up's virtual accessory state. A gripper closes around one level and
   carries that disc together with every disc resting above it. */
(() => {
  'use strict';
  const COLORS = Object.freeze(['green', 'yellow', 'blue', 'white', 'red']);
  const COMMANDS = Object.freeze(['LEFT', 'RIGHT', 'UP', 'DOWN', 'OPEN', 'CLOSE']);
  const create = () => ({
    trays: [[], [], [...COLORS], [], []],
    held: [],
    station: 3,
    height: 6,
    grip: 'open'
  });
  const snapshot = (state) => ({
    trays: state.trays.map((tray) => [...tray]), held: [...state.held],
    station: state.station, height: state.height, grip: state.grip
  });
  function valid(state) {
    if (!Number.isInteger(state.station) || state.station < 1 || state.station > 5 || !Number.isInteger(state.height) || state.height < 1 || state.height > 6) return false;
    if (!Array.isArray(state.trays) || state.trays.length !== 5 || !Array.isArray(state.held) || !['open', 'closed'].includes(state.grip)) return false;
    if (state.held.length && state.grip !== 'closed') return false;
    const pieces = [...state.held, ...state.trays.flat()];
    return state.trays.every((tray) => Array.isArray(tray) && tray.length <= 5) &&
      pieces.length === 5 && new Set(pieces).size === 5 && COLORS.every((color) => pieces.includes(color));
  }
  function apply(state, command) {
    if (!valid(state)) return { ok: false, reason: 'Invalid virtual stack state.' };
    if (!COMMANDS.includes(command)) return { ok: false, reason: 'Unknown Stack-Up command.' };
    const next = snapshot(state);
    const tray = next.trays[next.station - 1];
    if (command === 'UP') {
      if (next.height === 6) return { ok: false, reason: 'Arms are already at the highest level.' };
      next.height += 1;
    } else if (command === 'DOWN') {
      if (next.height === 1) return { ok: false, reason: 'Arms are already at the lowest level.' };
      if (next.held.length && next.height - 1 <= tray.length) return { ok: false, reason: 'The carried discs would collide with this tray stack.' };
      next.height -= 1;
    } else if (command === 'LEFT' || command === 'RIGHT') {
      const target = next.station + (command === 'LEFT' ? -1 : 1);
      if (target < 1 || target > 5) return { ok: false, reason: 'There is no tray in that direction.' };
      if (next.held.length && next.height <= next.trays[target - 1].length) return { ok: false, reason: 'Raise the carried discs to clear the next tray.' };
      next.station = target;
    } else if (command === 'CLOSE') {
      if (next.grip === 'closed') return { ok: false, reason: 'Hands are already closed.' };
      next.grip = 'closed';
      if (next.height <= tray.length) next.held = tray.splice(next.height - 1);
    } else if (command === 'OPEN') {
      if (next.grip === 'open') return { ok: false, reason: 'Hands are already open.' };
      if (next.held.length) {
        if (next.height !== tray.length + 1) return { ok: false, reason: 'Lower the carried discs to the next free level before releasing.' };
        if (tray.length + next.held.length > 5) return { ok: false, reason: 'That tray cannot hold more than five discs.' };
        tray.push(...next.held);
        next.held = [];
      }
      next.grip = 'open';
    }
    if (!valid(next)) return { ok: false, reason: 'Command would lose or duplicate a disc.' };
    Object.assign(state, next);
    return { ok: true, command, state: snapshot(state) };
  }
  const api = Object.freeze({ COLORS, COMMANDS, create, snapshot, valid, apply });
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') window.RobStackModel = api;
})();
