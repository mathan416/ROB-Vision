(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const StackModel = window.RobStackModel;
  let stackState = StackModel.create();
  const state = { mode: 'gyro', live: false, head: 0, arms: 0, turn: 0, depth: 1, grip: false, manualActive: false, manualCommand: null, stopped: false, running: false, timer: null, recoveryTimer: null, recoveryQueue: [], recoveryCount: { a: 0, b: 0 }, cleanupStarted: false, sequence: null, step: -1, prop: { x: 225, y: 496, scale: 1 }, propFrame: null, secondProp: { x: 145, y: 469, scale: .85 }, secondPropFrame: null, motion: { turn: 0, arms: 0, grip: 0, head: 0, depth: 1 }, motionFrame: null };
  // Preview timing is illustrative; the future virtual controller will own these states on UNO Q.
  const GYRO_SPIN_MS = 55000;
  const gyros = { a: { startedAt: null, phase: 'idle' }, b: { startedAt: null, phase: 'idle' } };
  let gyroTimer = null;
  const gyroLevel = (gyro, now = performance.now()) => gyro.startedAt === null ? 0 : Math.max(0, 1 - (now - gyro.startedAt) / GYRO_SPIN_MS);
  const gyroPhase = (gyro, now = performance.now()) => gyro.startedAt === null ? 'idle' : gyroLevel(gyro, now) === 0 ? 'stopped' : gyroLevel(gyro, now) <= .2 ? 'wobbling' : 'spinning';
  function resetGyros() {
    if (gyroTimer) clearInterval(gyroTimer);
    gyroTimer = null;
    for (const gyro of Object.values(gyros)) { gyro.startedAt = null; gyro.phase = 'idle'; }
  }
  function startGyro(which) {
    if (gyros[which].startedAt !== null && gyros[which].phase !== 'stopped') return;
    gyros[which].startedAt = performance.now();
    gyros[which].phase = 'spinning';
    if (!gyroTimer) gyroTimer = setInterval(updateGyros, 250);
  }
  const descriptions = {
    gyro: 'Watch R.O.B. spin two gyros, recover each once, then return both to their holders.',
    stack: 'Watch R.O.B. move one block, then carry two blocks together. Every move follows a Stack-Up command.',
    free: 'Try R.O.B.’s poses with the controls below, or run his short greeting. No game pieces.'
  };
  const missions = {
    // A docked gyro is positioned by its pointed tip (local y = 21), not its platter center.
    gyro: [
      { title: 'One gate / no spin', caption: 'A single gate can be pressed without spinning a gyro.', action: 'READY', location: 'holder', head: 0, arms: 0, turn: 0, grip: false, prop: [225, 496], event: 'Single-gate practice begins with Gyro A on its holder.' },
      { title: 'One gate / no spin', caption: 'R.O.B. grips Gyro A directly from its holder.', action: 'GRIPPING', location: 'held', head: -12, arms: 34, turn: -100, grip: true, prop: [225, 496], event: 'Gyro A gripped without using the spinner.' },
      { title: 'One gate / no spin', caption: 'Gyro A lifts from the holder.', action: 'LIFTING', location: 'held', head: -12, arms: -9, turn: -100, grip: true, prop: [225, 445], event: 'Unspun gyro raised.' },
      { title: 'One gate / no spin', caption: 'R.O.B. brings the unspun gyro to red.', action: 'CARRYING', location: 'held', head: -5, arms: -9, turn: -40, grip: true, prop: [285, 445, 1.12], event: 'Unspun gyro carried to red.' },
      { title: 'One gate / no spin', caption: 'R.O.B. holds Gyro A down; the red virtual button is pressed.', action: 'PRESSING', location: 'redTray', heldPress: true, head: -5, arms: 55, turn: -40, grip: true, prop: [285, 514.5, 1.12], event: 'Red button pressed by an unspun gyro held by R.O.B.' },
      { title: 'One gate / no spin', caption: 'R.O.B. lifts the gyro; the red button releases.', action: 'RELEASING', location: 'held', head: -5, arms: -9, turn: -40, grip: true, prop: [285, 445, 1.12], event: 'Red button released as Gyro A lifts.' },
      { title: 'One gate / no spin', caption: 'Returning the unspun gyro to its holder.', action: 'CARRYING', location: 'held', head: -12, arms: -9, turn: -100, grip: true, prop: [225, 445], event: 'Gyro A carried back to its holder.' },
      { title: 'One gate / no spin', caption: 'Gyro A returns to its holder.', action: 'STORED', location: 'holder', head: -12, arms: 34, turn: -100, grip: false, prop: [225, 496], event: 'Gyro A stored after one-gate practice.' },
      { title: 'Gyro relay', caption: 'The red gyro is waiting on its raised holder.', action: 'READY', location: 'holder', head: 0, arms: 0, turn: 0, grip: false, prop: [225, 496], event: 'Red gyro holder selected.' },
      { title: 'Gyro relay', caption: 'Both hands turn and descend around the gyro.', action: 'LOWERING', location: 'holder', head: -12, arms: 34, turn: -100, grip: false, prop: [225, 496], event: 'Arm carriage lowering to the holder.' },
      { title: 'Gyro relay', caption: 'Two hands close together around one gyro.', action: 'GRIPPING', location: 'held', head: -12, arms: 34, turn: -100, grip: true, prop: [225, 496], event: 'Opposing hands closed around red gyro.' },
      { title: 'Gyro relay', caption: 'Lifting the gyro clear of the holder.', action: 'LIFTING', location: 'held', head: -12, arms: -9, turn: -100, grip: true, prop: [225, 445], event: 'Red gyro raised.' },
      { title: 'Gyro relay', caption: 'Turning toward the spinner on your right.', action: 'CARRYING', location: 'held', head: 14, arms: -9, turn: 120, grip: true, prop: [445, 445, .85], event: 'Right-side spinner targeted.' },
      { title: 'Gyro relay', caption: 'Lowering the gyro into the right-side spinner.', action: 'LOWERING', location: 'held', head: 14, arms: 17, turn: 120, grip: true, prop: [445, 477, .85], event: 'Red gyro lowering into right-side spinner.' },
      { title: 'Gyro relay', caption: 'Hands release. The gyro begins to spin!', action: 'SPINNING', location: 'spinner', spin: true, head: 14, arms: 17, turn: 120, grip: false, prop: [445, 477, .85], event: 'Red gyro spinning on the right.' },
      { title: 'Gyro relay', caption: 'Hands rise clear of the spinning gyro.', action: 'SPINNING', location: 'spinner', spin: true, head: 14, arms: -9, turn: 120, grip: false, prop: [445, 477, .85], event: 'Spinner running; hands clear.' },
      { title: 'Gyro relay', caption: 'Returning to collect the spinning gyro.', action: 'REACHING', location: 'spinner', spin: true, head: 14, arms: 17, turn: 120, grip: false, prop: [445, 477, .85], event: 'Hands returning to right-side spinner.' },
      { title: 'Gyro relay', caption: 'Both hands secure the spinning gyro.', action: 'GRIPPING', location: 'held', spin: true, head: 14, arms: 17, turn: 120, grip: true, prop: [445, 477, .85], event: 'Spinning gyro secured.' },
      { title: 'Gyro relay', caption: 'Lifting the gyro out of the spinner.', action: 'LIFTING', location: 'held', spin: true, head: 14, arms: -9, turn: 120, grip: true, prop: [445, 445, .85], event: 'Spinning gyro raised.' },
      { title: 'Gyro relay', caption: 'Carrying the gyro toward the front red button.', action: 'CARRYING', location: 'held', spin: true, head: -5, arms: -9, turn: -40, grip: true, prop: [285, 445, 1.12], event: 'Front red button targeted.' },
      { title: 'Gyro relay', caption: 'Lowering the gyro onto the front red button.', action: 'LOWERING', location: 'held', spin: true, head: -5, arms: 55, turn: -40, grip: true, prop: [285, 514.5, 1.12], event: 'Red gyro lowering onto front button.' },
      { title: 'Gyro relay', caption: 'Hands release the gyro on the red button.', action: 'PLACING', location: 'redTray', spin: true, head: -5, arms: 55, turn: -40, grip: false, prop: [285, 514.5, 1.12], event: 'Red gyro released on front button.' },
      { title: 'First gyro placed', caption: 'The red pad holds Gyro A while R.O.B. turns to the far holder.', action: 'STAGED', location: 'redTray', spin: true, head: 0, arms: 0, turn: 0, grip: false, prop: [285, 514.5, 1.12], event: 'Gyro A spinning on front red pad.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Gyro B waits on the far holder. It matches Gyro A.', action: 'READY', location: 'holder', head: 0, arms: 0, turn: 0, grip: false, prop: [145, 469, .85], event: 'Far gyro holder selected.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Both hands reach the far gyro.', action: 'LOWERING', location: 'holder', head: -20, arms: 11, turn: -180, grip: false, prop: [145, 469, .85], event: 'Hands lower around Gyro B.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'The paired hands close around Gyro B.', action: 'GRIPPING', location: 'held', head: -20, arms: 11, turn: -180, grip: true, prop: [145, 469, .85], event: 'Gyro B gripped at far holder.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Gyro B lifts clear of its holder.', action: 'LIFTING', location: 'held', head: -20, arms: -9, turn: -180, grip: true, prop: [145, 445, .85], event: 'Gyro B raised.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Carrying Gyro B across to the right spinner.', action: 'CARRYING', location: 'held', head: 14, arms: -9, turn: 120, grip: true, prop: [445, 445, .85], event: 'Spinner targeted for Gyro B.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Gyro B lowers into the spinner.', action: 'LOWERING', location: 'held', head: 14, arms: 17, turn: 120, grip: true, prop: [445, 477, .85], event: 'Gyro B lowering into spinner.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Gyro B begins to spin while A keeps turning on red.', action: 'SPINNING', location: 'spinner', spin: true, head: 14, arms: 17, turn: 120, grip: false, prop: [445, 477, .85], event: 'Gyro B spinning at the right station.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Hands rise above spinning Gyro B.', action: 'SPINNING', location: 'spinner', spin: true, head: 14, arms: -9, turn: 120, grip: false, prop: [445, 477, .85], event: 'Gyro B spinning; hands clear.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Hands return to the spinner.', action: 'REACHING', location: 'spinner', spin: true, head: 14, arms: 17, turn: 120, grip: false, prop: [445, 477, .85], event: 'Hands return for Gyro B.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Both hands secure Gyro B.', action: 'GRIPPING', location: 'held', spin: true, head: 14, arms: 17, turn: 120, grip: true, prop: [445, 477, .85], event: 'Spinning Gyro B secured.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Gyro B lifts out of the spinner.', action: 'LIFTING', location: 'held', spin: true, head: 14, arms: -9, turn: 120, grip: true, prop: [445, 445, .85], event: 'Gyro B raised from spinner.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Bringing Gyro B forward to the blue pad.', action: 'CARRYING', location: 'held', spin: true, head: 5, arms: -9, turn: 45, grip: true, prop: [370, 445, 1.12], event: 'Front blue pad targeted.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Lowering Gyro B onto the blue pad.', action: 'LOWERING', location: 'held', spin: true, head: 5, arms: 55, turn: 45, grip: true, prop: [370, 514.5, 1.12], event: 'Gyro B lowering onto blue pad.' },
      { title: 'Second gyro relay', piece: 'b', caption: 'Gyro B settles on blue; Gyro A remains on red.', action: 'PLACING', location: 'blueTray', spin: true, head: 5, arms: 55, turn: 45, grip: false, prop: [370, 514.5, 1.12], event: 'Gyro B released on blue pad.' },
      { title: 'Dual gyro relay complete!', piece: 'b', caption: 'Two matching gyros spin on the red and blue pads.', action: 'COMPLETE', location: 'blueTray', spin: true, head: 0, arms: 0, turn: 0, grip: false, prop: [370, 514.5, 1.12], event: 'Both colored pads hold spinning gyros.' }
    ],
    stack: [],
    free: [
      { title: 'Pose Lab greeting', caption: 'Hello, operator!', head: -25, arms: -18, turn: 0, grip: false, event: 'R.O.B. says hello.' },
      { title: 'Pose Lab greeting', caption: 'Looking around the room.', head: 27, arms: 0, turn: 0, grip: false, event: 'Head sweep complete.' },
      { title: 'Pose Lab greeting', caption: 'Testing both hands together.', head: 0, arms: 28, turn: 0, grip: true, event: 'Opposing hands close together.' },
      { title: 'Pose Lab complete!', caption: 'Ready for another adventure.', head: 0, arms: 0, turn: 0, grip: false, event: 'Returned to home pose.' }
    ]
  };
  function buildStackDemo() {
    const preview = StackModel.create();
    const steps = [{ title: 'Stack-Up / five blocks', action: 'READY', caption: 'All five blocks begin on Tray 3. R.O.B. starts centered, high, and open.', event: 'Stack-Up virtual setup ready.' }];
    const add = (command, title) => {
      const before = StackModel.snapshot(preview);
      const result = StackModel.apply(preview, command);
      if (!result.ok) throw new Error(`Invalid Stack-Up demo: ${command}: ${result.reason}`);
      const colors = preview.held.join(' + ');
      let caption;
      if (command === 'CLOSE') caption = `CLOSE: R.O.B. grips ${colors} ${preview.held.length === 1 ? 'block' : 'blocks'} together on Tray ${preview.station}.`;
      else if (command === 'OPEN') caption = `OPEN: ${before.held.join(' + ')} ${before.held.length === 1 ? 'block lands' : 'blocks land'} on Tray ${preview.station}.`;
      else if (command === 'LEFT' || command === 'RIGHT') caption = `${command}: R.O.B. turns one station to Tray ${preview.station}${colors ? `, carrying ${colors}` : ''}.`;
      else caption = `${command}: arms move one level to ${preview.height}${colors ? ` with ${colors}` : ''}.`;
      steps.push({ title, action: command, command, caption, event: caption });
    };
    const repeat = (command, count, title) => { for (let i = 0; i < count; i += 1) add(command, title); };
    add('DOWN', 'Top red block'); add('CLOSE', 'Top red block'); add('UP', 'Top red block'); add('RIGHT', 'Top red block'); repeat('DOWN', 5, 'Top red block'); add('OPEN', 'Top red block');
    repeat('UP', 5, 'Two-block carry'); add('LEFT', 'Two-block carry'); repeat('DOWN', 3, 'Two-block carry'); add('CLOSE', 'Two-block carry'); repeat('UP', 3, 'Two-block carry'); add('LEFT', 'Two-block carry'); repeat('DOWN', 5, 'Two-block carry'); add('OPEN', 'Two-block carry');
    steps.push({ title: 'Stack-Up complete!', action: 'COMPLETE', caption: 'Red rests on Tray 4; blue and white stay stacked together on Tray 2. Green and yellow remain on Tray 3.', event: 'All five blocks accounted for; grouped carry demo complete.' });
    return steps;
  }
  missions.stack = buildStackDemo();
  const currentSequence = () => state.sequence || missions[state.mode];
  const currentItem = () => state.step >= 0 ? currentSequence()[state.step] : null;
  function recoverySequence(which) {
    const color = which === 'a' ? 'red' : 'blue';
    const pad = `${color}Tray`;
    const x = which === 'a' ? 285 : 370;
    const turn = which === 'a' ? -40 : 45;
    const head = which === 'a' ? -5 : 5;
    const title = `Gyro ${which.toUpperCase()} recovery`;
    const step = (action, location, caption, arms, heading, rotation, grip, prop) => {
      const locations = { a: 'redTray', b: 'blueTray' };
      locations[which] = location;
      return { title, piece: which, action, location, locations, caption, head: heading, arms, turn: rotation, grip, prop, event: caption };
    };
    return [
      step('RECOVERING', pad, `Gyro ${which.toUpperCase()} has tipped on the ${color} pad. R.O.B. reaches for it.`, 0, head, turn, false, [x, 514.5, 1.12]),
      step('LOWERING', pad, `Hands lower around stopped Gyro ${which.toUpperCase()}.`, 55, head, turn, false, [x, 514.5, 1.12]),
      step('GRIPPING', 'held', `Both hands secure Gyro ${which.toUpperCase()}.`, 55, head, turn, true, [x, 514.5, 1.12]),
      step('LIFTING', 'held', `Gyro ${which.toUpperCase()} lifts off the ${color} pad.`, -9, head, turn, true, [x, 445, 1.12]),
      step('CARRYING', 'held', `Carrying Gyro ${which.toUpperCase()} back to the spinner.`, -9, 14, 120, true, [445, 445, .85]),
      step('LOWERING', 'held', `Lowering Gyro ${which.toUpperCase()} into the spinner.`, 17, 14, 120, true, [445, 477, .85]),
      step('SPINNING', 'spinner', `The spinner recharges Gyro ${which.toUpperCase()}.`, 17, 14, 120, false, [445, 477, .85]),
      step('REACHING', 'spinner', `Hands return for spinning Gyro ${which.toUpperCase()}.`, 17, 14, 120, false, [445, 477, .85]),
      step('GRIPPING', 'held', `R.O.B. collects spinning Gyro ${which.toUpperCase()}.`, 17, 14, 120, true, [445, 477, .85]),
      step('LIFTING', 'held', `Lifting Gyro ${which.toUpperCase()} clear of the spinner.`, -9, 14, 120, true, [445, 445, .85]),
      step('CARRYING', 'held', `Returning Gyro ${which.toUpperCase()} to the ${color} pad.`, -9, head, turn, true, [x, 445, 1.12]),
      step('LOWERING', 'held', `Lowering Gyro ${which.toUpperCase()} onto the ${color} pad.`, 55, head, turn, true, [x, 514.5, 1.12]),
      step('PLACING', pad, `Gyro ${which.toUpperCase()} presses the ${color} pad again.`, 55, head, turn, false, [x, 514.5, 1.12]),
      step('RESTORED', pad, `Gyro ${which.toUpperCase()} is spinning on the ${color} pad again.`, 0, 0, 0, false, [x, 514.5, 1.12])
    ];
  }
  function cleanupSequence() {
    const locations = { a: 'redTray', b: 'blueTray' };
    const steps = [];
    const add = (which, action, location, caption, arms, head, turn, grip, prop) => {
      locations[which] = location;
      steps.push({ title: 'Gyro holders / tidy up', piece: which, action, location, locations: { ...locations }, caption, head, arms, turn, grip, prop, event: caption });
    };
    add('a', 'REACHING', 'redTray', 'R.O.B. reaches for stopped Gyro A on red.', 55, -5, -40, false, [285, 514.5, 1.12]);
    add('a', 'GRIPPING', 'held', 'Gyro A lifts off the red button.', 55, -5, -40, true, [285, 514.5, 1.12]);
    add('a', 'LIFTING', 'held', 'Carrying stopped Gyro A clear of red.', -9, -5, -40, true, [285, 445, 1.12]);
    add('a', 'CARRYING', 'held', 'Returning Gyro A to its front holder.', -9, -12, -100, true, [225, 445]);
    add('a', 'LOWERING', 'held', 'Lowering Gyro A onto the front holder.', 34, -12, -100, true, [225, 496]);
    add('a', 'STORED', 'holder', 'Gyro A rests on its holder.', 34, -12, -100, false, [225, 496]);
    add('b', 'REACHING', 'blueTray', 'R.O.B. reaches for stopped Gyro B on blue.', 55, 5, 45, false, [370, 514.5, 1.12]);
    add('b', 'GRIPPING', 'held', 'Gyro B lifts off the blue button.', 55, 5, 45, true, [370, 514.5, 1.12]);
    add('b', 'LIFTING', 'held', 'Carrying stopped Gyro B clear of blue.', -9, 5, 45, true, [370, 445, 1.12]);
    add('b', 'CARRYING', 'held', 'Returning Gyro B to its far holder.', -9, -20, -180, true, [145, 445, .85]);
    add('b', 'LOWERING', 'held', 'Lowering Gyro B onto the far holder.', 11, -20, -180, true, [145, 469, .85]);
    add('b', 'STORED', 'holder', 'Gyro B rests on its holder.', 11, -20, -180, false, [145, 469, .85]);
    add('b', 'COMPLETE', 'holder', 'Demo complete. Both gyros are back on their holders.', 0, 0, 0, false, [145, 469, .85]);
    return steps;
  }
  let eventTotal = 1;
  function animateProp(slot, frameSlot, elementId, x, y, scale, immediate) {
    if (state[frameSlot]) cancelAnimationFrame(state[frameSlot]);
    const start = { ...state[slot] };
    if (immediate || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      state[slot] = { x, y, scale }; $(elementId).setAttribute('transform', `translate(${x} ${y}) scale(${scale})`); state[frameSlot] = null; return;
    }
    const started = performance.now();
    function frame(now) {
      const t = Math.min(1, (now - started) / 1000);
      const eased = t * t * (3 - 2 * t);
      state[slot] = { x: start.x + (x - start.x) * eased, y: start.y + (y - start.y) * eased, scale: start.scale + (scale - start.scale) * eased };
      $(elementId).setAttribute('transform', `translate(${state[slot].x} ${state[slot].y}) scale(${state[slot].scale})`);
      state[frameSlot] = t < 1 ? requestAnimationFrame(frame) : null;
    }
    state[frameSlot] = requestAnimationFrame(frame);
  }
  function moveProp(x, y, scale = 1, immediate = false) { animateProp('prop', 'propFrame', 'move-prop', x, y, scale, immediate); }
  function moveSecondProp(x, y, scale = 1, immediate = false) { animateProp('secondProp', 'secondPropFrame', 'second-gyro-prop', x, y, scale, immediate); }
  function moveMechanism(turn, arms, grip, head, depth) {
    if (state.motionFrame) cancelAnimationFrame(state.motionFrame);
    const start = { ...state.motion };
    const target = { turn, arms, grip: grip ? 1 : 0, head, depth };
    const started = performance.now();
    function frame(now) {
      const t = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 1 : Math.min(1, (now - started) / 950);
      const eased = t * t * (3 - 2 * t);
      for (const key of Object.keys(target)) state.motion[key] = start[key] + (target[key] - start[key]) * eased;
      // The carriage moves vertically on the column. Its shoulder pivots stay attached;
      // the projected hands sweep across the front as the upper body turns.
      $('arm-carriage').setAttribute('transform', `translate(0 ${state.motion.arms})`);
      const closedGap = state.mode === 'stack' ? 27 : 23;
      const gap = (closedGap + (1 - state.motion.grip) * 23) * state.motion.depth;
      const center = 325 + state.motion.turn;
      const leftX = center - gap;
      const rightX = center + gap;
      const leftElbow = 245 + state.motion.turn * .25;
      const rightElbow = 405 + state.motion.turn * .25;
      const leftPath = `M285 318 L${leftElbow} 381 L${leftX} 449`;
      const rightPath = `M365 318 L${rightElbow} 381 L${rightX} 449`;
      $('left-arm-body').setAttribute('d', leftPath);
      $('left-arm-glint').setAttribute('d', leftPath);
      $('right-arm-body').setAttribute('d', rightPath);
      $('right-arm-glint').setAttribute('d', rightPath);
      $('left-elbow').setAttribute('cx', leftElbow);
      $('right-elbow').setAttribute('cx', rightElbow);
      $('left-hand').setAttribute('transform', `translate(${leftX} 453) scale(${state.motion.depth})`);
      $('right-hand').setAttribute('transform', `translate(${rightX} 453) scale(${-state.motion.depth} ${state.motion.depth})`);
      $('head').setAttribute('transform', `rotate(${state.motion.head} 325 265)`);
      state.motionFrame = t < 1 ? requestAnimationFrame(frame) : null;
    }
    state.motionFrame = requestAnimationFrame(frame);
  }
  const time = () => new Date().toLocaleTimeString('en-GB', { hour12: false });
  function log(message) {
    const item = document.createElement('li');
    const stamp = document.createElement('time');
    const text = document.createElement('span');
    stamp.textContent = time(); text.textContent = message;
    item.append(stamp, text);
    $('event-list').prepend(item);
    while ($('event-list').children.length > 5) $('event-list').lastElementChild.remove();
    eventTotal += 1;
    $('event-count').textContent = String(eventTotal).padStart(3, '0') + ' EVENTS';
  }
  function gyroLocations(item) {
    if (item?.locations) return item.locations;
    return {
      a: item?.piece === 'b' ? 'redTray' : item?.location || 'holder',
      b: item?.piece === 'b' ? item.location : 'holder'
    };
  }
  function startNextRecovery() {
    if (state.mode !== 'gyro' || state.running || state.stopped || state.recoveryTimer || state.cleanupStarted) return;
    const readyToClean = () => !state.recoveryQueue.length && state.recoveryCount.a > 0 && state.recoveryCount.b > 0 && gyros.a.phase === 'stopped' && gyros.b.phase === 'stopped';
    if (!state.recoveryQueue.length && !readyToClean()) return;
    state.recoveryTimer = setTimeout(() => {
      state.recoveryTimer = null;
      if (state.mode !== 'gyro' || state.running || state.stopped) return;
      if (readyToClean()) {
        state.cleanupStarted = true;
        state.sequence = cleanupSequence();
        state.step = 0;
        state.running = true;
        log('Virtual R.O.B. is returning both stopped gyros to their holders.');
        runStep();
        return;
      }
      const which = state.recoveryQueue.shift();
      if (!which) return;
      if (gyros[which].phase !== 'stopped') { startNextRecovery(); return; }
      state.recoveryCount[which] += 1;
      state.sequence = recoverySequence(which);
      state.step = 0;
      state.running = true;
      log(`Virtual recovery started for Gyro ${which.toUpperCase()}.`);
      runStep();
    }, 2500);
  }
  function updateGyros() {
    if (state.mode !== 'gyro' || state.stopped) return;
    const item = currentItem();
    const locations = gyroLocations(item);
    let changed = false;
    for (const [which, gyro] of Object.entries(gyros)) {
      const next = gyroPhase(gyro);
      if (next === gyro.phase) continue;
      gyro.phase = next;
      changed = true;
      if (next === 'wobbling') log(`Gyro ${which.toUpperCase()} is slowing and wobbling.`);
      if (next === 'stopped') {
        const color = which === 'a' ? 'red' : 'blue';
        const onPad = locations[which] === `${color}Tray`;
        log(`Gyro ${which.toUpperCase()} stopped.${onPad ? ` ${color.toUpperCase()} pad released in simulation.` : ''}`);
        if (onPad && state.recoveryCount[which] === 0 && !state.recoveryQueue.includes(which)) state.recoveryQueue.push(which);
        if (onPad && !state.running) {
          $('stage-caption').textContent = `Gyro ${which.toUpperCase()} stopped; ${color} pad released.`;
          $('mission-description').textContent = $('stage-caption').textContent;
        }
      }
    }
    if (changed || gyros.a.startedAt !== null || gyros.b.startedAt !== null) render(false);
    if (Object.values(gyros).every((gyro) => gyro.startedAt === null || gyro.phase === 'stopped')) {
      clearInterval(gyroTimer);
      gyroTimer = null;
    }
    startNextRecovery();
  }
  const stackXs = [145, 230, 325, 410, 500];
  const stackBases = [486, 509, 518, 505, 486];
  const stackPercents = [12, 31, 50, 69, 88];
  const stackTops = [30, 83, 174, 83, 30];
  const discPaint = {
    red: ['#a03c47', '#f08069', '#ffd8bb', '#583644'],
    white: ['#a1b5b5', '#e7efeb', '#fbfffa', '#849a9d'],
    blue: ['#317d9b', '#5dd1ef', '#b9f2fa', '#315d72'],
    yellow: ['#a98145', '#f1c76e', '#f9e3a2', '#806b42'],
    green: ['#4b9870', '#80d8a4', '#bcead4', '#42785b']
  };
  function stackPose(immediate = false) {
    const index = stackState.station - 1;
    state.turn = stackXs[index] - 325;
    state.head = Math.round(state.turn * .12);
    state.arms = 57 - (stackState.height - 1) * 14;
    state.grip = stackState.grip === 'closed';
    state.depth = 1;
    moveProp(stackXs[index], stackBases[index] - (stackState.height - 1) * 8, 1, immediate);
  }
  function svgDisc(color, x, y) {
    const ns = 'http://www.w3.org/2000/svg';
    const group = document.createElementNS(ns, 'g');
    group.setAttribute('transform', `translate(${x} ${y})`);
    const [side, top, rim, hub] = discPaint[color];
    for (const attributes of [
      { cy: 7, rx: 24, ry: 8, fill: side },
      { cy: 0, rx: 24, ry: 8, fill: top, stroke: rim, 'stroke-width': 3 },
      { cy: 0, rx: 8, ry: 3, fill: hub }
    ]) {
      const ellipse = document.createElementNS(ns, 'ellipse');
      for (const [key, value] of Object.entries(attributes)) ellipse.setAttribute(key, value);
      group.append(ellipse);
    }
    return group;
  }
  function renderStackPieces() {
    const placed = $('stack-colors');
    const carried = $('disc-prop');
    placed.replaceChildren(); carried.replaceChildren();
    stackState.trays.forEach((tray, index) => tray.forEach((color, level) => placed.append(svgDisc(color, stackXs[index], stackBases[index] - level * 8))));
    stackState.held.forEach((color, level) => carried.append(svgDisc(color, 0, -level * 8)));
    const stations = $('stack-fixture').querySelectorAll('.station-art.stack-tray');
    stations.forEach((station, index) => {
      station.replaceChildren();
      stackState.trays[index].forEach((color, level) => {
        const disc = document.createElement('span');
        disc.className = `disc ${color}`;
        disc.style.top = `${43 - level * 7}px`;
        disc.style.zIndex = String(2 + level);
        station.append(disc);
      });
    });
    const tableHeld = $('table-held-stack');
    tableHeld.replaceChildren();
    tableHeld.style.left = `${stackPercents[stackState.station - 1]}%`;
    tableHeld.style.top = `${Math.max(2, stackTops[stackState.station - 1] - 35 - (stackState.height - 1) * 3)}px`;
    stackState.held.forEach((color, level) => {
      const disc = document.createElement('span');
      disc.className = `disc ${color}`;
      disc.style.top = `${32 - level * 7}px`;
      disc.style.zIndex = String(2 + level);
      tableHeld.append(disc);
    });
    const mini = $('mini-stacks');
    mini.replaceChildren();
    const addMini = (color, station, top, level) => {
      const disc = document.createElement('i');
      disc.className = `mini-disc ${color}`;
      disc.style.left = `${[17, 33, 50, 67, 83][station]}%`;
      disc.style.top = `${top - 8 - level * 5}px`;
      disc.style.zIndex = String(2 + level);
      mini.append(disc);
    };
    const miniTops = [15, 43, 72, 43, 15];
    stackState.trays.forEach((tray, index) => tray.forEach((color, level) => addMini(color, index, miniTops[index], level)));
    stackState.held.forEach((color, level) => addMini(color, stackState.station - 1, Math.max(12, miniTops[stackState.station - 1] - 26), level));
  }
  function renderFixture() {
    $('gyro-fixture').hidden = state.mode !== 'gyro';
    $('stack-fixture').hidden = state.mode !== 'stack';
    $('free-fixture').hidden = state.mode !== 'free';
    const item = currentItem();
    const locations = gyroLocations(item);
    const firstLocation = state.mode === 'gyro' ? locations.a : null;
    const secondLocation = state.mode === 'gyro' ? locations.b : null;
    const atSpinner = firstLocation === 'spinner' || secondLocation === 'spinner';
    $('red-dock-piece').hidden = firstLocation !== 'holder';
    $('second-dock-piece').hidden = secondLocation !== 'holder';
    $('red-spinner-piece').hidden = !atSpinner;
    $('red-tray-piece').hidden = firstLocation !== 'redTray';
    $('blue-tray-piece').hidden = secondLocation !== 'blueTray';
    $('red-spinner-piece').classList.toggle('spinning', atSpinner && gyroLevel(gyros[item?.piece === 'b' ? 'b' : 'a']) > 0 && !state.stopped);
    const redActive = firstLocation === 'redTray' && (gyroLevel(gyros.a) > 0 || (item?.heldPress && item.piece !== 'b')) && !state.stopped;
    const blueActive = secondLocation === 'blueTray' && (gyroLevel(gyros.b) > 0 || (item?.heldPress && item.piece === 'b')) && !state.stopped;
    $('red-tray-piece').classList.toggle('wobbling', redActive && gyros.a.phase === 'wobbling');
    $('blue-tray-piece').classList.toggle('wobbling', blueActive && gyros.b.phase === 'wobbling');
    $('red-tray-piece').classList.toggle('toppled', firstLocation === 'redTray' && gyros.a.phase === 'stopped');
    $('blue-tray-piece').classList.toggle('toppled', secondLocation === 'blueTray' && gyros.b.phase === 'stopped');
    $('red-tray-piece').parentElement.classList.toggle('pad-active', redActive);
    $('blue-tray-piece').parentElement.classList.toggle('pad-active', blueActive);
    if (state.mode === 'stack') renderStackPieces();
    $('fixture-mode-label').textContent = state.mode === 'gyro' ? 'GYROMITE SETUP' : state.mode === 'stack' ? 'STACK-UP / FIVE TRAYS' : 'POSE LAB / NO GAME PIECES';
    $('world-title').textContent = state.mode === 'free' ? 'ROBOT MOTION / NO GAME' : 'GAME TABLE / SIMULATED PIECES';
    $('fixture-note').textContent = state.mode === 'gyro'
      ? state.cleanupStarted ? firstLocation === 'holder' && secondLocation === 'holder' ? 'Demo complete: both gyros stored; red and blue buttons released.' : `Returning stopped gyros to their holders. Red ${redActive ? 'PRESSED' : 'RELEASED'} · blue ${blueActive ? 'PRESSED' : 'RELEASED'}.` : secondLocation === 'blueTray' ? `Virtual buttons: red ${redActive ? 'PRESSED' : 'RELEASED'} · blue ${blueActive ? 'PRESSED' : 'RELEASED'}. Game link offline.` : item?.piece === 'b' ? `Gyro A on red: ${redActive ? 'pad pressed' : 'pad released'}. Gyro B moving toward blue.` : firstLocation === 'redTray' ? `Gyro A on red: ${redActive ? 'pad pressed' : 'pad released'}. Game link offline.` : firstLocation === 'spinner' ? 'Illustration: Gyro A spins at the right spinner.' : firstLocation === 'held' ? 'Illustration: Gyro A is held between both hands.' : 'Two matching gyros, one spinner, and two button pads. Positions are illustrative.'
      : state.mode === 'stack'
        ? `Virtual stack: ${stackState.held.length ? `${stackState.held.join(' + ')} in R.O.B.'s hands` : 'hands empty'} · ${stackState.trays.map((tray, index) => `T${index + 1} ${tray.length}`).join(' · ')}. Game link offline.`
        : 'Pose Lab is for trying R.O.B.’s movement without game accessories.';
  }
  function render(animateMotion = true) {
    const item = currentItem();
    if (!state.stopped && animateMotion) moveMechanism(state.turn, state.arms, state.grip, state.head, state.depth);
    $('scene-gyro').style.display = state.mode === 'gyro' ? '' : 'none';
    $('scene-stack').style.display = state.mode === 'stack' ? '' : 'none';
    $('move-prop').style.display = state.mode === 'free' ? 'none' : '';
    $('second-gyro-prop').style.display = state.mode === 'gyro' ? '' : 'none';
    $('gyro-prop').style.display = state.mode === 'gyro' ? '' : 'none';
    $('disc-prop').style.display = state.mode === 'stack' && stackState.held.length ? '' : 'none';
    $('scene-spinner').classList.toggle('station-active', state.mode === 'gyro' && (item?.location === 'spinner' || (item?.location === 'held' && item.prop?.[0] === 445)));
    $('scene-target-gyro').classList.toggle('station-active', state.mode === 'gyro' && gyroLocations(item).a === 'redTray');
    $('scene-blue-tray').classList.toggle('station-active', state.mode === 'gyro' && gyroLocations(item).b === 'blueTray');
    for (let station = 1; station <= 5; station += 1) $('stack-tray-' + station).classList.toggle('station-active', state.mode === 'stack' && stackState.station === station);
    const gyroPositions = gyroLocations(item);
    for (const [which, id] of [['a', 'gyro-prop'], ['b', 'second-gyro-prop']]) {
      const level = gyroLevel(gyros[which]);
      $(id).classList.toggle('is-spinning', state.mode === 'gyro' && level > 0 && !state.stopped);
      $(id).classList.toggle('is-wobbling', state.mode === 'gyro' && gyros[which].phase === 'wobbling' && !state.stopped);
      $(id).classList.toggle('is-toppled', state.mode === 'gyro' && gyros[which].phase === 'stopped' && gyroPositions[which]?.endsWith('Tray') && !state.stopped);
      $(id).style.setProperty('--gyro-spin-duration', `${(.38 + (1 - level) * 1.5).toFixed(2)}s`);
    }
    const focusedGyro = item?.piece === 'b' ? 'b' : 'a';
    $('focus-art').className = `focus-art ${state.mode}${state.mode === 'gyro' && gyroLevel(gyros[focusedGyro]) > 0 && !state.stopped ? ' spinning' : ''}`;
    $('focus-type').textContent = state.mode === 'free' ? 'MOTION STUDY' : 'GAME PIECE';
    $('floor-action').textContent = state.mode === 'free' ? 'TURN → LIFT → GRIP' : 'PICK → PLACE';
    const stackTop = stackState.trays[stackState.station - 1].at(-1);
    $('focus-name').textContent = state.mode === 'gyro' ? item?.piece === 'b' ? 'GYRO B' : 'GYRO A' : state.mode === 'stack' ? stackState.held.length ? stackState.held.length === 1 ? `${stackState.held[0].toUpperCase()} BLOCK` : `${stackState.held.length} BLOCKS TOGETHER` : stackTop ? `${stackTop.toUpperCase()} BLOCK` : 'EMPTY TRAY' : 'R.O.B. POSE';
    $('focus-art').style.background = state.mode === 'stack' ? discPaint[stackState.held.at(-1) || stackTop]?.[1] || '#536f7b' : '';
    $('focus-action').textContent = state.stopped ? 'STOPPED' : item?.action || (state.manualActive ? state.manualCommand || 'POSE' : 'READY');
    $('focus-location').textContent = state.mode === 'gyro' ? ({ holder: state.cleanupStarted ? item?.piece === 'b' ? 'FAR HOLDER / STORED' : 'FRONT HOLDER / STORED' : item?.piece === 'b' ? 'FAR HOLDER → BLUE PAD' : 'FRONT HOLDER → RED PAD', held: 'BETWEEN BOTH HANDS', spinner: 'RIGHT SPINNER / ROTATING', redTray: 'RED BUTTON PAD', blueTray: 'BLUE BUTTON PAD' })[item?.location || 'holder'] : state.mode === 'stack' ? `TRAY ${stackState.station} / LEVEL ${stackState.height}${stackState.held.length ? ' / IN HAND' : ''}` : 'NO GAME PIECES';
    $('stage-action-label').textContent = item ? `${item.action || 'PLAY'} / ${String(state.step + 1).padStart(2, '0')}` : state.manualActive ? `${state.manualCommand || 'POSE'} / MANUAL` : 'HOME / 00';
    $('head-value').textContent = `${state.head}°`;
    $('head-bar').style.width = `${50 + state.head * .6}%`;
    $('arm-value').textContent = state.arms === 0 ? 'HOME' : state.arms > 0 ? 'LOWERED' : 'RAISED';
    $('arm-bar').style.width = `${50 + state.arms * .9}%`;
    $('grip-value').textContent = state.grip ? 'CLOSED' : 'OPEN';
    $('grip-bar').style.width = state.grip ? '91%' : '14%';
    $('tracking-label').textContent = 'NOT CONNECTED';
    $('optical-value').textContent = state.running ? 'SCRIPTED DEMO' : 'NOT CONNECTED';
    $('optical-bar').style.width = state.running ? '75%' : '12%';
    $('gyro-vitals').hidden = state.mode !== 'gyro';
    $('controls-title').textContent = state.mode === 'stack' ? 'STACK-UP COMMANDS' : 'POSE PREVIEW';
    $('controls-context').textContent = state.mode === 'stack' ? 'LOCAL VIRTUAL CONTROL / NO OPTICAL INPUT' : 'MANUAL SIMULATION / NO GAME COMMANDS';
    $('grip-label').textContent = state.mode === 'stack' ? stackState.grip === 'open' ? 'CLOSE HANDS' : 'OPEN HANDS' : 'TOGGLE GRIP';
    $('demo-button').querySelector('.demo-label').textContent = state.mode === 'free' ? 'PLAY R.O.B. GREETING' : 'RUN DEMO SEQUENCE';
    const locations = gyroLocations(item);
    for (const [which, color] of [['a', 'red'], ['b', 'blue']]) {
      const level = gyroLevel(gyros[which]);
      const phase = gyroPhase(gyros[which]);
      const heldPress = item?.heldPress && (item.piece === 'b' ? 'b' : 'a') === which;
      const pressed = locations[which] === `${color}Tray` && (level > 0 || heldPress) && !state.stopped;
      $(`gyro-${which}-value`).textContent = `${heldPress && pressed ? 'HELD' : phase.toUpperCase()} / ${pressed ? 'PRESSED' : 'RELEASED'}`;
      $(`gyro-${which}-bar`).style.width = `${Math.round(level * 100)}%`;
    }
    $('stage').classList.toggle('stopped', state.stopped);
    $('stop-button').classList.toggle('latched', state.stopped);
    $('stop-button').innerHTML = state.stopped ? '↻ <span>RESET STOP</span>' : '■ <span>EMERGENCY STOP</span>';
    document.querySelectorAll('[data-action], #home-button, #demo-button').forEach((button) => { button.disabled = state.stopped; });
    renderFixture();
  }
  function cancelDemo() { if (state.timer) clearTimeout(state.timer); if (state.recoveryTimer) clearTimeout(state.recoveryTimer); state.timer = null; state.recoveryTimer = null; state.recoveryQueue = []; state.running = false; if (state.propFrame) cancelAnimationFrame(state.propFrame); state.propFrame = null; if (state.secondPropFrame) cancelAnimationFrame(state.secondPropFrame); state.secondPropFrame = null; if (state.motionFrame) cancelAnimationFrame(state.motionFrame); state.motionFrame = null; }
  function home() {
    cancelDemo(); resetGyros(); stackState = StackModel.create(); state.sequence = null; state.recoveryCount = { a: 0, b: 0 }; state.cleanupStarted = false; state.head = 0; state.arms = 0; state.turn = 0; state.depth = 1; state.grip = false; state.manualActive = false; state.manualCommand = null; state.step = -1; moveProp(state.mode === 'gyro' ? 225 : 325, state.mode === 'gyro' ? 496 : 486, 1, true); moveSecondProp(145, 469, .85, true); if (state.mode === 'stack') stackPose(true);
    $('mission-title').textContent = state.mode === 'free' ? 'Try a pose.' : 'Ready when you are.';
    $('mission-description').textContent = state.mode === 'free' ? 'Use Pose Preview below to turn, lift, and grip, or play R.O.B.’s greeting.' : 'Choose an accessory and give R.O.B. a mission. Every movement will play out here in real time.';
    $('stage-caption').textContent = 'Waiting for a mission.';
    $('mission-step').textContent = 'STANDBY'; $('progress-text').textContent = '0 / 0'; $('progress-fill').style.width = '0%';
    log('Returned to home pose.'); render();
  }
  function runStep() {
    if (!state.running || state.stopped) return;
    const sequence = currentSequence();
    const item = sequence[state.step];
    if (state.mode === 'gyro' && item.action === 'SPINNING' && item.location === 'spinner') startGyro(item.piece === 'b' ? 'b' : 'a');
    if (state.mode === 'stack') {
      if (item.command) {
        const result = StackModel.apply(stackState, item.command);
        if (!result.ok) { state.running = false; $('mission-step').textContent = 'FAULT'; $('stage-caption').textContent = result.reason; log(`Stack-Up command rejected: ${result.reason}`); render(); return; }
      }
      stackPose();
    } else {
      state.head = item.head; state.arms = item.arms; state.turn = item.turn; state.grip = item.grip; state.depth = item.prop?.[2] ?? 1;
      if (item.prop) (item.piece === 'b' ? moveSecondProp : moveProp)(...item.prop);
    }
    $('mission-title').textContent = item.title;
    $('mission-description').textContent = item.caption;
    $('stage-caption').textContent = item.caption;
    $('mission-step').textContent = state.step === sequence.length - 1 ? 'COMPLETE' : item.action === 'SPINNING' ? 'SPINNING' : 'IN PROGRESS';
    $('progress-text').textContent = `${state.step + 1} / ${sequence.length}`;
    $('progress-fill').style.width = `${(state.step + 1) / sequence.length * 100}%`;
    log(item.event); render();
    if (state.step < sequence.length - 1) state.timer = setTimeout(() => { state.step += 1; runStep(); }, state.mode === 'stack' ? 950 : state.mode === 'gyro' && item.action === 'SPINNING' ? 1750 : 1300);
    else { state.running = false; state.timer = null; render(); startNextRecovery(); }
  }
  $('demo-button').addEventListener('click', () => { if (state.live) return; cancelDemo(); resetGyros(); stackState = StackModel.create(); state.sequence = null; state.recoveryCount = { a: 0, b: 0 }; state.cleanupStarted = false; moveProp(state.mode === 'gyro' ? 225 : 325, state.mode === 'gyro' ? 496 : 505, 1, true); moveSecondProp(145, 469, .85, true); if (state.mode === 'stack') stackPose(true); state.manualActive = false; state.manualCommand = null; state.step = 0; state.running = true; log(state.mode === 'free' ? 'Pose Lab greeting started; no game commands or pieces.' : `${state.mode.toUpperCase()} scripted demonstration started; no optical command decoded.`); runStep(); });
  $('home-button').addEventListener('click', () => { if (state.live) window.RobLive.reset(); else home(); });
  $('stop-button').addEventListener('click', () => {
    if (state.live) { window.RobLive.stop(); return; }
    if (state.stopped) { state.stopped = false; log('Simulation stop reset. Home before a new mission.'); home(); }
    else { cancelDemo(); resetGyros(); state.stopped = true; $('mission-title').textContent = 'Motion stopped.'; $('mission-description').textContent = 'Simulation stop latched. Reset to return to the home pose.'; $('stage-caption').textContent = 'Movement halted by operator.'; $('mission-step').textContent = 'STOPPED'; log('Emergency stop latched in simulation.'); render(); }
  });
  document.querySelectorAll('[data-mode]').forEach((button) => button.addEventListener('click', () => {
    if (window.RobLive?.gameActive()) return;
    if (state.stopped) return;
    cancelDemo(); state.mode = button.dataset.mode;
    document.querySelectorAll('[data-mode]').forEach((tab) => tab.classList.toggle('active', tab === button));
    $('mode-description').textContent = descriptions[state.mode];
    $('accessory-art').className = `accessory-art mode-${state.mode}`;
    home(); log(`${button.textContent} scene selected.`);
  }));
  document.querySelectorAll('[data-action]').forEach((button) => button.addEventListener('click', () => {
    if (state.live) { window.RobLive.command(button.dataset.action); return; }
    if (state.stopped) return;
    cancelDemo();
    state.manualActive = true; state.depth = 1;
    const action = button.dataset.action;
    if (state.mode === 'stack') {
      state.step = -1;
      const command = ({ left: 'LEFT', right: 'RIGHT', raise: 'UP', lower: 'DOWN' })[action] || (stackState.grip === 'open' ? 'CLOSE' : 'OPEN');
      state.manualCommand = command;
      const before = StackModel.snapshot(stackState);
      const result = StackModel.apply(stackState, command);
      if (result.ok) {
        stackPose();
        const moved = command === 'CLOSE' && stackState.held.length ? ` Gripped ${stackState.held.join(' + ')}.` : command === 'OPEN' && before.held.length ? ` Placed ${before.held.join(' + ')} on Tray ${stackState.station}.` : '';
        $('stage-caption').textContent = `${command}: Tray ${stackState.station}, level ${stackState.height}.${moved}`;
        $('mission-title').textContent = 'Virtual Stack-Up controls';
        $('mission-description').textContent = $('stage-caption').textContent;
        $('mission-step').textContent = 'MANUAL';
        log(`Manual Stack-Up ${command}.${moved}`);
      } else {
        $('stage-caption').textContent = `${command} rejected: ${result.reason}`;
        $('mission-title').textContent = 'Move blocked';
        $('mission-description').textContent = $('stage-caption').textContent;
        $('mission-step').textContent = 'BLOCKED';
        log($('stage-caption').textContent);
      }
      render();
      return;
    }
    if (action === 'left') state.turn = Math.max(-100, state.turn - 18);
    if (action === 'right') state.turn = Math.min(120, state.turn + 18);
    if (action === 'left' || action === 'right') state.head = Math.round(state.turn * .12);
    if (action === 'raise') state.arms = Math.max(-35, state.arms - 10);
    if (action === 'lower') state.arms = Math.min(63, state.arms + 10);
    if (action === 'grip') state.grip = !state.grip;
    $('stage-caption').textContent = `Direct control: ${button.textContent.trim().toLowerCase()}.`;
    $('mission-title').textContent = 'Pose preview'; $('mission-description').textContent = 'Manual input is updating the illustration. Game commands are not connected.';
    $('mission-step').textContent = 'MANUAL';
    log(`Manual pose preview: ${button.textContent.trim().toLowerCase()}.`); render();
  }));
  window.RobDashboard = {
    applyLive(snapshot) {
      cancelDemo();
      state.live = true;
      state.stopped = false;
      state.mode = snapshot.game === 'stack_up' ? 'stack' : 'gyro';
      document.querySelectorAll('[data-mode]').forEach((tab) => tab.classList.toggle('active', tab.dataset.mode === state.mode));
      $('accessory-art').className = `accessory-art mode-${state.mode}`;
      $('mode-description').textContent = descriptions[state.mode];
      const robot = snapshot.robot;
      if (!robot) {
        state.sequence = null; state.step = -1;
        stackState = StackModel.create(); resetGyros();
        state.head = 0; state.arms = 0; state.turn = 0; state.grip = false;
        moveProp(225, 496, 1, true); moveSecondProp(145, 469, .85, true);
      }
      if (robot && state.mode === 'stack') {
        stackState = robot;
        state.sequence = null; state.step = -1;
        stackPose();
      } else if (robot) {
        const names = { holder_a: 'holder', holder_b: 'holder', red_pad: 'redTray', blue_pad: 'blueTray', spinner: 'spinner', held: 'held' };
        const locations = { a: names[robot.pieces.a], b: names[robot.pieces.b] };
        const piece = robot.held || (robot.station === 1 || robot.station === 4 ? 'b' : 'a');
        const place = robot.pieces[piece];
        const coords = { holder_a: [225, 496, 1], holder_b: [145, 469, .85], red_pad: [285, 514.5, 1.12], blue_pad: [370, 514.5, 1.12], spinner: [445, 477, .85] };
        const target = place === 'held' ? [145, 225, 285, 370, 445][robot.station - 1] : null;
        const position = place === 'held' ? [target, robot.height <= 2 ? 500 : 445, 1] : coords[place];
        state.sequence = [{ title: 'Live Gyromite', action: snapshot.events.at(-1)?.command || 'READY', location: names[place], locations, piece, prop: position }];
        state.step = 0;
        state.turn = [-180, -100, -40, 45, 120][robot.station - 1];
        state.head = Math.round(state.turn * .12);
        state.arms = 55 - (robot.height - 1) * 14;
        state.grip = robot.grip === 'closed';
        (piece === 'b' ? moveSecondProp : moveProp)(...position);
        for (const which of ['a', 'b']) {
          gyros[which].startedAt = robot.spinning[which] ? performance.now() - 1000 : null;
          gyros[which].phase = robot.spinning[which] ? 'spinning' : 'idle';
        }
      }
      state.manualActive = true;
      state.manualCommand = snapshot.events.at(-1)?.command?.replace(/_(GYRO|STACK)$/, '') || 'READY';
      $('mission-title').textContent = robot ? `Live ${state.mode === 'stack' ? 'Stack-Up' : 'Gyromite'}` : 'Select a game';
      $('mission-description').textContent = robot ? snapshot.events.at(-1)?.message || 'Watching for game commands.' : 'Choose Gyromite or Stack-Up in the Accessory Bay.';
      $('stage-caption').textContent = $('mission-description').textContent;
      $('mission-step').textContent = snapshot.camera.state === 'capturing' ? 'WATCHING' : 'CAMERA OFFLINE';
      $('progress-text').textContent = `#${snapshot.sequence}`;
      render();
      const flashing = Boolean(snapshot.test?.flash_active);
      const ready = Boolean(snapshot.test?.ready) && !flashing;
      $('stage').classList.toggle('test-flashing', flashing);
      $('stage').classList.toggle('test-ready', ready);
      if (flashing) $('mission-step').textContent = 'TEST FLASHES';
      else if (ready) $('mission-step').textContent = 'READY LIGHT';
      $('demo-button').disabled = true;
      document.querySelectorAll('[data-mode]').forEach((tab) => { tab.disabled = true; });
      $('tracking-label').textContent = flashing ? 'TEST FLASHES DETECTED' : ready ? 'READY LIGHT SEEN' : snapshot.camera.state === 'capturing' ? 'CAMERA ACTIVE' : 'CAMERA OFFLINE';
      $('optical-value').textContent = snapshot.camera.state === 'capturing' ? `${snapshot.camera.fps} FPS` : 'CAMERA OFFLINE';
      $('connection').textContent = snapshot.link?.online ? 'CONTROLLER CONNECTED / RETROPIE ONLINE' : 'CONTROLLER CONNECTED / GAME LINK PENDING';
      document.querySelector('.gyro-vitals-note').textContent = snapshot.link?.online ? 'Virtual pad states sent to RetroPie Controller 2' : 'Virtual spin and button states; game link offline';
      $('controls-context').textContent = 'LIVE CONTROLLER / CAMERA OR MANUAL';
      document.querySelector('.vitals-card .live-text').textContent = '● CONTROLLER';
      document.querySelector('.stage-panel .chip').textContent = 'LIVE VIRTUAL MOTION';
      $('fixture-note').textContent = $('fixture-note').textContent.replaceAll('Game link offline.', 'Game-host buttons pending.');
      $('gyro-a-value').textContent = robot?.pads?.red ? 'SPINNING / PRESSED' : $('gyro-a-value').textContent;
      $('gyro-b-value').textContent = robot?.pads?.blue ? 'SPINNING / PRESSED' : $('gyro-b-value').textContent;
    },
    leaveLive() { state.live = false; $('stage').classList.remove('test-flashing', 'test-ready'); home(); document.querySelectorAll('[data-mode]').forEach((tab) => { tab.disabled = false; }); $('connection').textContent = 'OPTICAL + LAN / SIMULATED'; document.querySelector('.vitals-card .live-text').textContent = '● SIMULATION'; document.querySelector('.stage-panel .chip').textContent = 'SIMULATED MOTION'; document.querySelector('.gyro-vitals-note').textContent = 'Virtual spin and button states; no game link'; }
  };
  $('event-list').querySelector('time').textContent = time();
  function tick() { $('clock').textContent = time(); } tick(); setInterval(tick, 1000); render();
})();
