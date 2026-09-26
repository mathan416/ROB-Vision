/* Shared status wording for Mission and Setup. */
(() => {
  'use strict';
  const gameName = game => game === 'gyromite' ? 'GYROMITE' : game === 'stack_up' ? 'STACK-UP' : 'CONTROLLER';
  const connection = snapshot => `${gameName(snapshot?.game)} / CONNECTED`;
  const receiver = snapshot => `${String(snapshot?.link?.receiver || 'CONSOLE').toUpperCase()} ${snapshot?.link?.online ? 'LINKED' : 'WAITING'}`;
  const frames = snapshot => snapshot?.input?.frame_hook ? 'GAME FRAMES LINKED' : 'GAME FRAMES WAITING';
  const test = snapshot => snapshot?.test?.flash_active ? 'TEST SIGNAL SEEN' :
    snapshot?.test?.ready ? 'READY SIGNAL SEEN' : 'WAITING';
  const testSignal = snapshot => Boolean(snapshot?.test?.flash_active || snapshot?.test?.ready);
  const controllerDetail = snapshot => `${gameName(snapshot?.game)} · ${frames(snapshot)} · ${receiver(snapshot)}`;
  window.RobStatus = Object.freeze({ gameName, connection, receiver, frames, test, testSignal, controllerDetail,
    offline: 'CONTROLLER / OFFLINE', preview: 'PREVIEW / LOCAL', connecting: 'CONTROLLER / CONNECTING' });
})();
