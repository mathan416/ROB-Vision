/* Shared status wording for Mission, Setup, and Help. */
(() => {
  'use strict';
  const gameName = game => game === 'gyromite' ? 'GYROMITE' : game === 'stack_up' ? 'STACK-UP' : 'NO GAME';
  const connection = snapshot => `${gameName(snapshot?.game)} / CONNECTED`;
  const activeConsole = snapshot => snapshot?.game ? snapshot?.link?.consoles?.find(console => console.active) : null;
  const receiverOnline = snapshot => {
    const active = activeConsole(snapshot);
    if (active) return Boolean(active.online);
    const consoles = snapshot?.link?.consoles;
    return Array.isArray(consoles) ? consoles.some(console => console.online) : Boolean(snapshot?.link?.online);
  };
  const receiver = snapshot => {
    const consoles = snapshot?.link?.consoles;
    if (Array.isArray(consoles)) {
      if (!consoles.length) return 'NO CONSOLE PAIRED';
      const selected = activeConsole(snapshot) || (consoles.length === 1 ? consoles[0] : null);
      if (selected) return `${String(selected.name || 'CONSOLE').toUpperCase()} / ${selected.online ? 'LINKED' : 'WAITING'}`;
      return `${consoles.filter(console => console.online).length} OF ${consoles.length} RECEIVERS LINKED`;
    }
    return `${String(snapshot?.link?.receiver || 'CONSOLE').toUpperCase()} / ${snapshot?.link?.online ? 'LINKED' : 'WAITING'}`;
  };
  const frames = snapshot => !snapshot?.game ? 'GAME FRAMES IDLE' :
    snapshot?.input?.frame_hook ? 'GAME FRAMES LINKED' : 'GAME FRAMES WAITING';
  const test = snapshot => snapshot?.test?.flash_active ? 'TEST SIGNAL SEEN' :
    snapshot?.test?.ready ? 'READY SIGNAL SEEN' : 'WAITING';
  const testSignal = snapshot => Boolean(snapshot?.test?.flash_active || snapshot?.test?.ready);
  const controllerDetail = snapshot => `${frames(snapshot)} · ${receiver(snapshot)}`;
  window.RobStatus = Object.freeze({ gameName, connection, receiver, receiverOnline, activeConsole, frames, test, testSignal, controllerDetail,
    offline: 'CONTROLLER / OFFLINE', preview: 'PREVIEW / LOCAL', connecting: 'CONTROLLER / CONNECTING' });
})();
