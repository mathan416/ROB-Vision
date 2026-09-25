/* Shared status wording for Mission and Setup. The top bar describes the
   browser-to-UNO-Q connection; RetroPie, camera, and Test status stay separate. */
(() => {
  'use strict';
  const gameName = game => game === 'gyromite' ? 'GYROMITE' : game === 'stack_up' ? 'STACK-UP' : 'CONTROLLER';
  const connection = snapshot => `${gameName(snapshot?.game)} / CONNECTED`;
  const receiver = snapshot => `RETROPIE ${snapshot?.link?.online ? 'ONLINE' : 'OFFLINE'}`;
  const camera = snapshot => {
    const capture = snapshot?.camera;
    if (!capture) return 'CAMERA UNKNOWN';
    if (capture.state === 'fault') return 'CAMERA FAULT';
    if (capture.state === 'capturing') return 'CAMERA CAPTURING';
    if (capture.platform === 'linux' && Array.isArray(capture.devices) && !capture.devices.length) return 'NO CAMERA DETECTED';
    return 'CAMERA OFFLINE';
  };
  const test = snapshot => snapshot?.test?.flash_active ? 'TEST SIGNAL SEEN' :
    snapshot?.test?.ready ? 'READY SIGNAL SEEN' : snapshot?.test?.armed ? 'WATCHING' : 'WAITING';
  const testSignal = snapshot => Boolean(snapshot?.test?.flash_active || snapshot?.test?.ready || snapshot?.test?.armed);
  const controllerDetail = snapshot => `${gameName(snapshot?.game)} · ${snapshot?.input?.frame_hook ? 'GAME FRAMES LINKED' : camera(snapshot)}${!snapshot?.input?.frame_hook && snapshot?.camera?.state === 'capturing' ? ` · ${snapshot.camera.fps || 0} FPS` : ''} · ${receiver(snapshot)}`;
  window.RobStatus = Object.freeze({ gameName, connection, receiver, camera, test, testSignal, controllerDetail,
    offline: 'CONTROLLER / OFFLINE', preview: 'PREVIEW / LOCAL', connecting: 'CONTROLLER / CONNECTING' });
})();
