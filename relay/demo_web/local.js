(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const stage = $('local-stage');
  let state = null;
  let busy = false;
  let needsRead = false;
  let morningChoice = 'keep';
  const phaseNames = { idle: 'Ready', started: 'Baseline', authorized: 'Permitted', observed: 'Refused', applied: 'Applied', verified: 'Measured', morning: 'Morning', finished: 'Finished', uncertain: 'Uncertain' };
  const steps = { idle: 0, started: 1, authorized: 2, observed: 3, applied: 3, verified: 4, morning: 5, finished: 6, uncertain: 3 };
  const busyCopy = { start: 'Sending real baseline checkouts and saving the starting flags.', authorize: 'Saving your permission for this local shop.', observe: 'Planting the fault, sending actual checkout requests and checking the exact permission.', verify: 'Sending fresh checkout traffic through the whole shop.', morning: 'Applying your morning choice and measuring fresh traffic.', finish: 'Removing the planted fault, restoring starting flags and checking the shop.', reload: 'Reading the saved record and checking the current flags. No action is repeated.' };

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = String(text);
    return element;
  }
  function time(value, date = false) {
    const parsed = new Date(value);
    if (!value || Number.isNaN(parsed.getTime())) return 'Not recorded';
    return parsed.toLocaleString(undefined, { ...(date ? { month: 'short', day: 'numeric' } : {}), hour: '2-digit', minute: '2-digit', second: '2-digit', timeZoneName: 'short' });
  }
  function button(label, operation, secondary = false) {
    const element = node('button', 'local-button' + (secondary ? ' local-secondary' : ''), label);
    element.type = 'button';
    element.dataset.operation = operation;
    element.addEventListener('click', () => act(operation));
    return element;
  }
  function paragraph(text) { return node('p', '', text); }
  function result(title, text, healthy) {
    const box = node('div', 'local-result');
    if (typeof healthy === 'boolean') box.dataset.healthy = String(healthy);
    box.append(node('strong', '', title), paragraph(text));
    return box;
  }
  function scope() {
    const box = node('div', 'local-scope');
    box.append(paragraph('One shop. One exact change.'), node('strong', '', 'new_checkout to off'));
    box.append(paragraph('Only when the new checkout has more than 5% errors for five complete logical minutes, with at least 10 checkouts per minute.'));
    let detail = 'Only this disposable local shop. Once. Permission expires after 10 real minutes and before the logical night ends.';
    if (state.authorization) detail = 'Local browser consent. ' + (state.authorization.used ? 'Used once.' : 'Unused.') + ' Expires ' + time(state.authorization.expires_at) + '. No other flag or environment is allowed.';
    box.append(paragraph(detail));
    return box;
  }
  function appendChoice(parent, value, title, copy) {
    const label = node('label', 'local-choice');
    const radio = node('input');
    radio.type = 'radio';
    radio.name = 'morning-choice';
    radio.value = value;
    radio.checked = morningChoice === value;
    radio.addEventListener('change', () => { morningChoice = value; });
    const text = node('span');
    text.append(node('strong', '', title), node('small', '', copy));
    label.append(radio, text);
    parent.append(label);
  }
  function renderStage(focus) {
    const phase = state.phase;
    stage.dataset.phase = phase;
    stage.replaceChildren();
    const line = node('div', 'local-step-line');
    line.append(node('p', 'local-kicker', phase === 'finished' ? 'Run complete' : phase === 'uncertain' ? 'Pause and recover' : 'Step ' + (steps[phase] + 1) + ' of 6'));
    const dots = node('div', 'local-step-dots');
    dots.setAttribute('aria-hidden', 'true');
    for (let i = 0; i < 6; i += 1) dots.append(node('span', i < steps[phase] ? 'is-done' : i === steps[phase] ? 'is-current' : ''));
    line.append(dots);
    stage.append(line);
    const heading = node('h2');
    heading.id = 'local-stage-title';
    heading.tabIndex = -1;
    stage.append(heading);
    const actions = node('div', 'local-actions');
    if (phase === 'idle') {
      heading.textContent = 'A small shop. A safe place to try.';
      stage.append(paragraph('Start with real checkout requests and a saved copy of the shop flags. Nothing here touches a production service.'), result('You control each step', 'The fault is planted only when you run watch. Finish clears it and restores the starting state.'));
      actions.append(button('Start a local night', 'start'));
    } else if (phase === 'started') {
      heading.textContent = 'What may happen while you sleep?';
      stage.append(paragraph('The starting flags are saved. Give the code one narrow permission, or run without permission to see the refusal.'), scope());
      actions.append(button('Allow this one change', 'authorize'), button('Run without permission', 'observe', true));
    } else if (phase === 'authorized') {
      heading.textContent = 'Your boundary is in place.';
      stage.append(paragraph('Now plant a rounding fault in the new checkout path. Watch will measure five logical minutes of real requests and check your permission before acting.'), scope());
      actions.append(button('Plant the fault and run watch', 'observe'));
    } else if (phase === 'applied' || phase === 'observed') {
      const applied = Boolean(state.decision && state.decision.applied);
      heading.textContent = applied ? 'The permitted change ran.' : 'The order was refused.';
      stage.append(paragraph(applied ? 'The real local flag was turned off and independently read back. Recovery still needs fresh checkout traffic.' : 'The checkout fault was measured. Code left the flag unchanged because the permission checks did not allow an action.'));
      const reasons = state.decision && Array.isArray(state.decision.reasons) ? state.decision.reasons.join(' ') : 'No decision reason was recorded.';
      stage.append(result(applied ? 'Confirmed readback: new_checkout ' + (state.decision.readback?.new_checkout || 'unknown') : 'No nightly flag change', reasons));
      actions.append(button(applied ? 'Verify whole-shop recovery' : 'Measure current health', 'verify'));
    } else if (phase === 'verified') {
      const health = state.verification;
      const healthy = health?.healthy === true;
      const changed = Boolean(state.decision?.applied);
      heading.textContent = healthy ? 'Fresh traffic confirms recovery.' : 'The shop still needs attention.';
      stage.append(result(healthy ? 'Recovery measured' : 'Recovery not confirmed', health?.reason || 'No verification result was recorded.', healthy), paragraph(changed ? 'Morning brings the choice back to you. Keep the overnight change for this session, or restore the saved flags.' : 'No overnight change was allowed, so there is nothing to undo. Either morning choice leaves the flags unchanged. Finish will remove the planted fault.'));
      const choices = node('fieldset', 'local-choices');
      choices.append(node('legend', '', 'Your morning decision'));
      appendChoice(choices, 'keep', 'Keep the current flag state', changed ? 'Leave new_checkout off until you finish this local run.' : 'Leave the flags as they are. The planted fault is still present.');
      appendChoice(choices, 'restore', 'Restore the starting flags', changed ? 'The planted fault is still present. Turning the path back on may bring errors back.' : 'No change was made overnight. This will not remove the planted fault.');
      stage.append(choices);
      actions.append(button('Apply morning decision', 'morning'));
    } else if (phase === 'morning') {
      const morning = state.morning;
      heading.textContent = morning?.choice === 'restore' ? 'The starting flags were requested.' : 'Your morning choice is recorded.';
      stage.append(result(morning?.healthy ? 'Fresh checkouts passed' : 'The shop is still unhealthy', morning?.reason || 'No morning measurement was recorded.', morning?.healthy === true), paragraph('Finish now to remove the planted fault, restore the starting flags and send a final set of real checkout requests.'));
      actions.append(button('Finish and restore the local shop', 'finish'));
    } else if (phase === 'finished') {
      heading.textContent = 'Local run finished.';
      stage.append(result(state.cleanup?.healthy ? 'Cleanup checked with fresh traffic' : 'Review the cleanup record', state.cleanup?.reason || 'See the saved record for cleanup details.', state.cleanup?.healthy === true), paragraph('The receipt includes your permission, actual HTTP responses, saved snapshots and measured outcomes. Start a new run by relaunching the local runner with a fresh state directory.'));
      const receipt = node('a', 'local-button', 'Download the run receipt');
      receipt.href = '/local/api/receipt';
      receipt.download = 'local-session.json';
      actions.append(receipt);
    } else {
      heading.textContent = 'The result needs a careful reset.';
      stage.append(result('An outcome is uncertain', state.error || 'The saved state cannot confirm whether the last operation completed.'), paragraph('Do not repeat the night action. Finish will clear the fault, restore the original flags and independently check the shop.'));
      actions.append(button('Finish and restore the local shop', 'finish'));
    }
    stage.append(actions);
    if (!['idle', 'morning', 'finished', 'uncertain'].includes(phase)) {
      const finish = button('Finish early and restore the shop', 'finish', true);
      finish.classList.add('local-quiet');
      stage.append(finish);
    }
    if (focus) heading.focus();
  }
  function metric(label, bucket) {
    const card = node('div', 'local-metric');
    const count = Number(bucket?.['checkouts.all']);
    const rate = Number(bucket?.['checkout_error_rate.all']);
    const measured = bucket && Number.isFinite(count) && count > 0 && Number.isFinite(rate);
    card.append(node('span', '', label));
    if (measured) {
      card.dataset.healthy = String(rate <= 0.05);
      card.append(node('strong', '', (rate * 100).toFixed(1) + '%'), node('small', '', 'whole-shop errors'), node('small', '', count + ' actual checkouts'));
    } else {
      card.classList.add('is-empty');
      card.append(node('strong', '', bucket ? 'No traffic measured' : 'Not measured'), node('small', '', 'No recovery claim'));
    }
    return card;
  }
  function fact(label, value) {
    const row = node('div', 'local-fact');
    row.append(node('dt', '', label), node('dd', '', value));
    return row;
  }
  function renderEvidence() {
    const before = Array.isArray(state.metrics?.before) ? state.metrics.before.at(-1) : null;
    const after = Array.isArray(state.metrics?.after) ? state.metrics.after.at(-1) : null;
    const afterLabel = state.phase === 'finished' ? 'After cleanup' : state.phase === 'morning' ? 'After your choice' : 'Fresh check';
    $('local-metrics').replaceChildren(metric(state.decision ? 'Before the decision' : 'Starting baseline', before), metric(afterLabel, after));
    const initial = state.starting_flags || state.original?.flags;
    $('local-flags').replaceChildren(
      fact('Starting new_checkout', initial?.new_checkout || 'Not captured yet'),
      fact('Current new_checkout', state.flags?.new_checkout || 'Not read yet'),
      fact('stock_from_cache', state.flags?.stock_from_cache || 'Not read yet'),
      fact('Permission', state.authorization ? (state.authorization.used ? 'Used once' : 'Granted, unused') : 'Not granted')
    );
    $('local-request-count').textContent = Number.isFinite(state.request_count) ? String(state.request_count) : '0';
    $('local-phase').textContent = phaseNames[state.phase] || 'Unknown';
    $('local-session-label').textContent = 'Session ' + String(state.session_id || 'unknown');
    const events = Array.isArray(state.events) ? state.events : [];
    $('local-events-summary').textContent = events.length ? events.length + ' recorded events' : 'No events yet';
    $('local-events').replaceChildren(...events.map((event) => {
      const item = node('li', 'local-event');
      const stamp = node('time', '', time(event.at));
      if (event.at) stamp.dateTime = event.at;
      item.append(stamp, paragraph(event.message || 'No event detail recorded.'));
      return item;
    }));
    const { csrf_token, ...receipt } = state;
    $('local-raw').textContent = JSON.stringify(receipt, null, 2);
  }
  function render(focus = false) { renderStage(focus); renderEvidence(); setBusy(false); }
  function setBusy(value, operation) {
    busy = value;
    stage.setAttribute('aria-busy', String(value));
    document.querySelectorAll('.local-page button, .local-page input').forEach((element) => {
      const recovery = element.dataset.operation === 'finish' || element.id === 'local-reload';
      element.disabled = value || !state || needsRead || (Boolean(state?.error) && !recovery);
    });
    const previous = stage.querySelector('.local-busy');
    if (previous) previous.remove();
    if (value && operation) {
      stage.append(node('p', 'local-busy', busyCopy[operation] || 'Reading the local session.'));
      $('local-announcement').textContent = busyCopy[operation] || 'Reading the local session.';
    }
    if (!value) $('local-retry').disabled = false;
  }
  async function request(path, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 45000);
    try {
      const response = await fetch('/local/api/' + path, { cache: 'no-store', credentials: 'same-origin', ...options, signal: controller.signal });
      const data = await response.json();
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'The local controller returned HTTP ' + response.status + '.');
      if (!data || typeof data.phase !== 'string' || typeof data.csrf_token !== 'string') throw new Error('The local controller returned an incomplete state.');
      return data;
    } finally { clearTimeout(timeout); }
  }
  function showError(error) {
    $('local-error-copy').textContent = error?.name === 'AbortError' ? 'The request timed out. Read the current state before deciding what to do next. The operation was not automatically repeated.' : error?.message || 'The local controller could not be reached.';
    $('local-error').hidden = false;
    $('local-announcement').textContent = 'The operation could not be confirmed. Read the error and current state.';
  }
  async function load() {
    if (busy) return;
    setBusy(true, 'reload');
    $('local-error').hidden = true;
    try {
      state = await request('state');
      needsRead = false;
      if (!state.decision?.applied) morningChoice = 'restore';
      render();
      if (state.error) showError(new Error(state.error));
    } catch (error) { showError(error); } finally { setBusy(false); }
  }
  async function act(operation) {
    if (busy || !state || needsRead) return;
    setBusy(true, operation);
    $('local-error').hidden = true;
    try {
      state = await request(operation, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Local-Key': state.csrf_token }, body: JSON.stringify(operation === 'morning' ? { choice: morningChoice } : {}) });
      needsRead = false;
      if (operation === 'observe') morningChoice = state.decision?.applied ? 'keep' : 'restore';
      render(true);
      $('local-announcement').textContent = $('local-stage-title').textContent;
    } catch (error) {
      try { state = await request('state'); needsRead = false; render(true); } catch { needsRead = true; }
      showError(error);
    } finally { setBusy(false); }
  }
  $('local-retry').addEventListener('click', load);
  $('local-reload').addEventListener('click', () => act('reload'));
  load();
})();
