"use strict";

(() => {
  document.body.classList.remove("no-js");
  const root = document.getElementById("replay-root");
  const live = document.getElementById("replay-status");
  const navigation = document.querySelector(".journey-nav");
  const state = {
    replay: null,
    view: "dusk",
    nightScene: "inventory",
    signedChoice: null,
    approvedChoice: null,
    busy: false,
    error: null,
    request: 0,
    controller: null,
    retry: null,
  };

  const escape = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[character]));
  const percent = (value) => `${(Number(value) * 100).toFixed(1)}%`;
  const timeOf = (value) => typeof value === "string" && value.includes("T") ? value.slice(11, 16) : value;
  const events = (kind, incident) => (state.replay?.timeline || []).filter((event) => event.kind === kind && (incident === undefined || event.incident === incident));
  const firstEvent = (kind, incident) => events(kind, incident)[0];
  const disabled = () => state.busy ? " disabled" : "";

  function button(id, text, action, type = "primary") {
    return `<button id="${id}" class="button ${type}" type="button" data-action="${action}"${disabled()}>${escape(text)}</button>`;
  }

  function chapter(time, title, copy) {
    return `<div class="chapter-head"><p class="chapter-time">${escape(time)} <span>Priya's local time</span></p><h2 class="chapter-title" id="chapter-heading" tabindex="-1">${escape(title)}</h2><p class="chapter-copy">${escape(copy)}</p></div>`;
  }

  function actionName(action) {
    if (!action) return "No change";
    if (action.flag === "new_checkout") return action.to === "off" ? "Turn off the new checkout" : "Turn on the new checkout";
    if (action.flag === "stock_from_cache") return action.to === "on" ? "Serve stock from the cache" : "Return to live stock checks";
    if (action.action === "traffic_to_revision" || action.kind === "traffic_to_revision") return "Send traffic to the previous shop version";
    return "Change described in the recorded order";
  }

  function choiceBadge() {
    if (state.signedChoice === null) return "<span class=\"choice-badge\">Your demo choice is next</span>";
    return `<span class="choice-badge">${state.signedChoice ? "Demo orders signed" : "Demo orders left unsigned"}</span>`;
  }

  function orderCards() {
    return `<div class="order-list" aria-label="The two demo orders">${state.replay.orders.map((order) => {
      const checkout = order.when.signal === "checkout_error_rate";
      const condition = checkout ? `If new checkout errors stay above ${Number(order.when.above) * 100}% for ${order.when.for_minutes} minutes` : `If response time stays above ${Number(order.when.above) / 1000} seconds for ${order.when.for_minutes} minutes`;
      const reason = checkout ? "Today's price rounding change is running only in the new checkout." : "Today's larger image cache shipped in a new shop version.";
      return `<article class="order-card"><div class="order-number">Order ${escape(order.id)}</div><h3 class="order-title">${checkout ? "New checkout errors" : "A slower shop"}</h3><p class="order-condition">${escape(condition)},</p><p class="order-action">${escape(actionName(order.do))}.</p><p class="order-reason">${reason}</p></article>`;
    }).join("")}</div>`;
  }

  function dusk() {
    const chosen = state.signedChoice !== null;
    let actions;
    if (!chosen) {
      actions = `${button("sign-orders", "Sign demo orders", "sign")} ${button("leave-unsigned", "Leave unsigned", "unsigned", "secondary")}`;
    } else {
      actions = `${button("next-step", "See what wakes Priya", "night")} ${button(state.signedChoice ? "leave-unsigned" : "sign-orders", state.signedChoice ? "Try leaving them unsigned" : "Try signing the orders", state.signedChoice ? "unsigned" : "sign", "quiet")}`;
    }
    return `${chapter("22:06", "What may happen while she sleeps?", "Priya reviews two narrow orders. Signing gives permission for these actions until 07:00. Anything outside them needs her.")}
      <div class="action-row" id="primary-action">${actions}</div>
      ${chosen ? `<p class="inline-note">${state.signedChoice ? "Priya's signature is part of this demo night." : "No permission was given. Watch must wake Priya instead of acting alone."}</p>` : "<p class=\"small-copy\">Choose a path. You can replay the other one.</p>"}
      ${orderCards()}
      <div class="decision-note"><strong>A boundary she keeps.</strong> Today's carts table change is left out. A database change needs a person; it cannot be safely undone by these orders.</div>`;
  }

  function inventoryMessage() {
    return (state.replay.messages || []).find((message) => message.incident === 1) || state.replay.messages?.[0];
  }

  function inventory() {
    const message = inventoryMessage();
    const page = firstEvent("woke", 1);
    const actualTime = message?.time || page?.time || "01:52";
    const available = Boolean(message?.suggestion);
    const selected = state.approvedChoice !== null;
    const approved = firstEvent("approved", 1);
    let title = "This one needs Priya.";
    let copy = "Both the old and new checkout are failing. Turning off only the new one would not fix it. Priya is needed for a different action.";
    let actions;
    if (!available) {
      copy = "With no signed orders, Watch wakes Priya as soon as the alert fires. It does not request an agent reply or offer an action to approve.";
      actions = button("next-step", "Continue to the checkout alert", "checkout");
    } else if (!selected) {
      actions = `${button("approve-fallback", "Approve demo fallback", "approve")} ${button("decline-fallback", "Decline", "decline", "secondary")}`;
    } else {
      title = state.approvedChoice ? "Priya approves one different action." : "Priya keeps that permission to herself.";
      copy = state.approvedChoice ? `At ${approved?.time || "01:53"}, her demo approval allows cached stock checks. The fallback was outside the signed orders, so it needed her.` : "The fallback is not applied. The approval window ends, and the simulated inventory problem continues until its fault ends at 02:40.";
      actions = `${button("next-step", "See the next alert", "checkout")} ${button(state.approvedChoice ? "decline-fallback" : "approve-fallback", state.approvedChoice ? "Try declining instead" : "Try approving instead", state.approvedChoice ? "decline" : "approve", "quiet")}`;
    }
    const notification = message ? `<section class="wake-message" id="wake-message" aria-labelledby="wake-message-title"><div class="wake-message-head"><h3 id="wake-message-title">Priya's wake-up</h3><time datetime="${escape(message.at)}">${escape(message.time)}</time></div><ul class="wake-message-lines">${message.lines.slice(0, 3).map((line) => `<li>${escape(line)}</li>`).join("")}</ul></section>` : "";
    return `${chapter(actualTime, title, copy)}<div class="action-row" id="primary-action">${actions}</div>
      ${notification}
      <article class="decision-card"><p class="decision-kicker">${available ? "Priya decides on this suggestion" : "No signed permission"}</p><h3 class="decision-title">${available ? "Use cached stock while inventory is slow" : "Priya must investigate this alert"}</h3><p class="decision-copy">${available ? "This can restore checkout on both paths. The code only applies it after approval from the on-call person." : "Leaving the orders unsigned also leaves the recorded agent suggestion unavailable. This replay makes no fallback change."}</p><p class="decision-note">${available ? "The new checkout order was declined because the old checkout was failing too." : "The demo approval choice is unavailable on this path."}</p></article>
      ${selected ? `<p class="inline-note">${state.approvedChoice ? `Demo approval recorded. Cached stock turned on at ${escape(approved?.time || "01:53")}.` : "Demo fallback declined. Nothing was changed by this suggestion."}</p>` : ""}
      <p class="small-copy">Priya's wake-up is part of the recorded demo.</p>`;
  }

  function checkout() {
    const acted = firstEvent("acted", 2);
    const woke = firstEvent("woke", 2);
    const recovered = firstEvent("recovered", 2);
    const handled = Boolean(acted);
    const time = acted?.time || woke?.time || "03:13";
    return `${chapter(time, handled ? "This time, Priya stays asleep." : "Without a signature, Priya is needed again.", handled ? "Only the new checkout is failing. Its error rate has stayed above 5% for five complete minutes, and the evidence fits the signed order." : "The new checkout is now failing by itself. The same threshold is met, but unsigned orders give Watch no permission to act.")}
      <div class="action-row" id="primary-action">${button("next-step", "Read the morning brief", "dawn")}${button("review-wake", "Back to the wake-up", "inventory", "quiet")}</div>
      <article class="decision-card"><p class="decision-kicker">${handled ? "Signed order 1 · Applied by code" : "No signed order · Human decision needed"}</p><h3 class="decision-title">${handled ? "The new checkout is turned off" : "The new checkout stays on"}</h3><p class="decision-copy">${handled ? `The code checks the signature, expiry, measured threshold, exact action and first use. At ${recovered?.time || "03:23"}, its re-check confirms the signal is below the limit. No page.` : "Watch records the alert and wakes Priya. The replay makes no checkout change on her behalf."}</p></article>
      ${handled ? `<div class="event-list"><div class="event-card"><span class="event-time">${escape(acted.time)}</span><div class="event-body"><strong>Permission checked, new checkout off.</strong><p>Only the action in the signed file was used.</p></div></div><div class="event-card"><span class="event-time">${escape(recovered?.time || "03:23")}</span><div class="event-body"><strong>Re-check passed.</strong><p>Priya did not need another wake-up.</p></div></div></div>` : "<p class=\"inline-note\">This replay records a second wake-up. It does not invent a response from Priya.</p>"}`;
  }

  function dawn() {
    const replay = state.replay;
    const morning = replay.morning;
    const hasChanges = morning.kept.length || morning.undone.length || morning.by_hand.length;
    const kept = morning.kept.map((item) => `<li class="morning-item"><span class="status-tag">Kept</span><div><strong>${escape(actionName(item.action))}</strong><p>${escape(item.until)}</p></div></li>`).join("");
    const undone = morning.undone.map((item) => `<li class="morning-item"><span class="status-tag neutral">Undone</span><div><strong>${escape(actionName(item.action))}</strong><p>The overnight fallback is not kept in the morning decision.</p></div></li>`).join("");
    const byHand = morning.by_hand.map((item) => `<li class="morning-item"><span class="status-tag neutral">For Priya</span><div><p>${escape(item)}</p></div></li>`).join("");
    return `${chapter(morning.time || "07:42", "Coffee, and a clear account of the night.", hasChanges ? "Priya sees every wake-up and every change. In this demo, the recorded morning decision keeps what still helps and undoes the temporary fallback." : "Priya sees every wake-up. Watch made no changes on her behalf, so there is nothing to keep or undo in the morning.")}
      <div class="action-row" id="primary-action">${button("restart-demo", "Replay this night", "restart")}${button("review-night", "Review the night", "checkout", "quiet")}</div>
      <div class="stat-grid" aria-label="Actual replay counts"><div class="stat"><span class="stat-value">${escape(replay.counts.pages)}</span><span class="stat-label">${replay.counts.pages === 1 ? "wake-up" : "wake-ups"}</span></div><div class="stat"><span class="stat-value">${escape(replay.counts.automatic_incidents_handled)}</span><span class="stat-label">handled while she slept</span></div><div class="stat"><span class="stat-value">${escape(replay.counts.approved_actions)}</span><span class="stat-label">${replay.counts.approved_actions === 1 ? "human-approved action" : "human-approved actions"}</span></div></div>
      <div class="event-card expiry-card"><span class="event-time">07:00</span><div class="event-body"><strong>Tonight's permission expires.</strong><p>Expiry stops further automatic action. It does not automatically undo a change.</p></div></div>
      <h3 class="section-title">${hasChanges ? "The recorded morning countersign" : "No overnight changes to keep or undo"}</h3>
      ${hasChanges ? `<ul class="morning-list">${kept}${undone}${byHand}</ul>` : "<p class=\"small-copy\">Watch made no changes, so this path needs no morning countersign.</p>"}
      <p class="small-copy">A countersign is Priya's morning decision about what stays. This one is recorded demo data, not a live merge.</p>`;
  }

  function samplesForChart() {
    const start = state.nightScene === "inventory" && state.view === "night" ? "01:40" : "03:00";
    const end = state.nightScene === "inventory" && state.view === "night" ? (state.approvedChoice === null ? inventoryMessage()?.time || "01:52" : "02:05") : "03:30";
    return state.replay.metrics.filter((sample) => {
      const time = timeOf(sample.sampled_at);
      return time >= start && time <= end;
    });
  }

  function metricChart() {
    const samples = samplesForChart();
    if (!samples.length) return "<p class=\"small-copy\">No metric samples were returned for this part of the replay.</p>";
    const inventoryView = state.view === "night" && state.nightScene === "inventory";
    const max = Math.max(inventoryView ? 0.25 : 0.10, ...samples.flatMap((sample) => [sample.old_rate, sample.new_rate]));
    const width = 600, height = 220, left = 42, top = 14, plotWidth = 542, plotHeight = 160;
    const x = (index) => left + index * plotWidth / Math.max(samples.length - 1, 1);
    const y = (rate) => top + plotHeight * (1 - rate / max);
    const path = (key) => samples.map((sample, index) => `${index ? "L" : "M"}${x(index).toFixed(2)},${y(sample[key]).toFixed(2)}`).join(" ");
    const ticks = inventoryView ? [0, 0.10, 0.20] : [0, 0.05, 0.10];
    const grids = ticks.map((rate) => `<line x1="${left}" y1="${y(rate)}" x2="${left + plotWidth}" y2="${y(rate)}" class="chart-grid"/><text x="${left - 8}" y="${y(rate) + 4}" text-anchor="end" class="chart-label">${Math.round(rate * 100)}%</text>`).join("");
    const indices = [...new Set([0, Math.floor((samples.length - 1) / 2), samples.length - 1])];
    const labels = indices.map((index) => `<text x="${x(index)}" y="198" text-anchor="${index === 0 ? "start" : index === samples.length - 1 ? "end" : "middle"}" class="chart-label">${escape(timeOf(samples[index].sampled_at))}</text>`).join("");
    const description = inventoryView ? "Both old and new checkout error rates rise together when inventory is slow. The displayed points are the actual simulated shop samples returned by Watch's replay." : "The old checkout stays near 0.3 percent errors. The new checkout rises to 7.9 percent. When signed order 1 switches it off, its measured error rate becomes zero because that path receives no traffic. All points come from the backend replay.";
    const action = inventoryView ? firstEvent("approved", 1) : firstEvent("acted", 2);
    let marker = "";
    if (action && samples.length) {
      const index = samples.findIndex((sample) => timeOf(sample.sampled_at) >= action.time);
      if (index >= 0) marker = `<line x1="${x(index)}" y1="${top}" x2="${x(index)}" y2="${top + plotHeight}" class="chart-action"/><text x="${Math.min(x(index) + 5, 455)}" y="29" class="chart-label">${escape(action.time)} change</text>`;
    }
    const caption = inventoryView ? (state.approvedChoice === true ? "The approval at 01:53 turns cached stock on. Both paths recover in the following complete minute." : "Both paths are affected. The 5% line belongs to the signed new checkout order; it does not authorize an inventory fallback.") : (state.signedChoice ? "After the new checkout is switched off, its 0% means no traffic on that path. Old checkout keeps serving; the underlying rounding bug still needs a fix." : "With no signed permission, the new checkout stays on and its error rate remains above the limit.");
    return `<section class="metric-card" aria-labelledby="metric-title"><div class="metric-title"><p class="eyebrow">Simulated shop · Actual replay samples</p><h3 id="metric-title">${inventoryView ? "Both checkout paths fail" : "One checkout path fails"}</h3></div><div class="metric-legend" aria-label="Chart legend"><span class="legend-item old">Old checkout</span><span class="legend-item new">New checkout</span></div><div class="chart-wrap"><svg id="metrics-chart" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="chart-title chart-description"><title id="chart-title">Checkout error rates during the ${inventoryView ? "inventory" : "rounding"} fault</title><desc id="chart-description">${escape(description)}</desc>${grids}<line x1="${left}" y1="${y(0.05)}" x2="${left + plotWidth}" y2="${y(0.05)}" class="chart-threshold"/><path d="${path("old_rate")}" class="chart-line old"/><path d="${path("new_rate")}" class="chart-line new"/>${marker}${labels}</svg></div><p class="chart-threshold-note">Dashed line: 5% limit for signed new checkout order.</p><p class="metric-caption">${escape(caption)}</p><details class="chart-table"><summary>Read the chart samples</summary><div class="table-scroll"><table><caption>Complete one-minute samples, Priya's local time</caption><thead><tr><th scope="col">Minute</th><th scope="col">Old checkout</th><th scope="col">New checkout</th></tr></thead><tbody>${samples.map((sample) => `<tr><th scope="row">${escape(timeOf(sample.sampled_at))}</th><td>${percent(sample.old_rate)}</td><td>${percent(sample.new_rate)}</td></tr>`).join("")}</tbody></table></div></details></section>`;
  }

  function context() {
    const persona = `<div class="persona-strip"><div class="avatar" aria-hidden="true">P</div><div class="persona-note"><strong>Priya</strong><p>Demo persona · On call tonight</p></div></div>`;
    if (state.view === "dusk") return `<aside class="context-panel" aria-label="Priya's context">${persona}<blockquote class="persona-quote">"Wake me when you need me. Let the small, agreed fixes happen without me."</blockquote><div class="context-note"><p class="eyebrow">What changed today</p><h3>A new checkout. A larger cache.</h3><p>Both have a narrow way back. The carts table change needs human judgment and stays outside tonight's permission.</p></div><div class="expiry-note"><strong>Permission ends at 07:00.</strong><p>Two actions, exact conditions, one use each.</p></div></aside>`;
    return `<aside class="context-panel" aria-label="Replay evidence">${persona}${choiceBadge()}${metricChart()}</aside>`;
  }

  function evidence() {
    const replay = state.replay;
    const signature = replay.signature;
    const checks = events("acted").map((event) => `<li><strong>${escape(event.time)} · Order ${escape(event.order)}</strong><p>${escape(event.text)}</p></li>`).join("");
    const pageItems = replay.messages.map((message) => `<li><strong>${escape(message.time)} · Incident ${escape(message.incident)}</strong><ul>${message.lines.map((line) => `<li>${escape(line)}</li>`).join("")}</ul></li>`).join("");
    return `<details class="evidence" id="evidence-details"><summary><span>Read the decision evidence</span><span class="small-copy">Signature, checks and the code's record</span></summary><div class="evidence-grid"><section class="evidence-section"><h3>Demo signature and expiry</h3><dl class="evidence-list"><dt>Signature</dt><dd>${signature.signed ? `${escape(signature.user)} by ${escape(signature.method)} at ${escape(timeOf(signature.at))}` : "Unsigned. Watch has no permission to act alone."}</dd><dt>Ends</dt><dd>${escape(replay.expiry.time)} in ${escape(replay.timezone)}</dd><dt>When expiry happens</dt><dd>Permission ends. Existing changes are not automatically reverted.</dd>${signature.signed ? `<dt>Recorded commit</dt><dd class="mono">${escape(signature.commit)}</dd>` : ""}</dl><h3>What was checked</h3>${checks ? `<ul class="evidence-list">${checks}</ul>` : "<p>No signed order was carried out in this replay.</p>"}</section><section class="evidence-section"><h3>The actual wake-up messages</h3><ul class="evidence-list">${pageItems}</ul></section><section class="evidence-section evidence-wide"><h3>Ledger written by Watch</h3><ol class="evidence-list ledger-list">${replay.timeline.map((event) => `<li><span class="mono">${escape(event.time)} · ${escape(event.kind)}</span><p>${escape(event.text)}</p></li>`).join("")}</ol><details><summary>Read the recorded port log</summary><pre class="proof-log">${escape(replay.logs.join("\n"))}</pre></details><details><summary>Read the demo order structure</summary><pre class="proof-log">${escape(JSON.stringify(replay.orders, null, 2))}</pre></details><details><summary>Read the morning record</summary><pre class="proof-log">${escape(morningProof(replay.morning))}</pre></details></section></div><div class="evidence-sources"><strong>Inspect the code and labelled files</strong><a href="https://github.com/alejandro-publius/life-after-code/blob/main/relay/nightorders/watch.py">Watch decision code</a><a href="https://github.com/alejandro-publius/life-after-code/blob/main/relay/nightorders/demo_night.py">In-memory replay</a><a href="https://github.com/alejandro-publius/life-after-code/tree/main/demo/night-2026-10-20">Labelled demo inputs</a><p class="small-copy">The same existing Watch code makes these verdicts. Shop faults and agent replies are recorded demo data. This page does not run a live model, make GitLab writes, send phone push notifications or call production services.</p></div></details>`;
  }

  function morningProof(morning) {
    return morning.lines.length ? morning.lines.join("\n") : "No morning changes were needed in this replay.";
  }

  function render({focus = false} = {}) {
    root.setAttribute("aria-busy", String(state.busy));
    root.dataset.view = state.view;
    root.dataset.scene = state.view === "night" ? state.nightScene : state.view;
    for (const step of navigation.querySelectorAll("[data-step]")) {
      const active = step.dataset.step === state.view;
      step.classList.toggle("active", active);
      step.classList.toggle("complete", step.dataset.step === "dusk" && state.signedChoice !== null || step.dataset.step === "night" && state.view === "dawn");
      if (active) step.setAttribute("aria-current", "step"); else step.removeAttribute("aria-current");
      step.disabled = state.busy || !state.replay || (step.dataset.step !== "dusk" && state.signedChoice === null) || (step.dataset.step === "dawn" && state.nightScene === "inventory" && state.approvedChoice === null && Boolean(inventoryMessage()?.suggestion));
    }
    if (!state.replay) {
      root.innerHTML = state.error ? `<main class="journey-panel error-state" id="journey-content"><h2 class="chapter-title" id="chapter-heading" tabindex="-1">The demo could not load.</h2><p>${escape(state.error)}</p><div class="action-row">${button("retry-replay", "Retry the replay", "retry")}</div><p class="small-copy">No live action was attempted. The same labelled replay is available from the repository's command line.</p></main>` : `<main class="journey-panel loading" id="journey-content"><p class="eyebrow">Getting the demo ready</p><h2 class="chapter-title">Loading Priya's night...</h2><p class="chapter-copy">Preparing the recorded demo night.</p></main>`;
      return;
    }
    const content = state.view === "dusk" ? dusk() : state.view === "dawn" ? dawn() : state.nightScene === "inventory" ? inventory() : checkout();
    const failure = state.error ? `<div class="inline-error" role="alert"><p>${escape(state.error)}</p>${button("retry-replay", "Retry this choice", "retry", "secondary")}</div>` : "";
    root.innerHTML = `<div class="journey-layout"><main class="journey-panel" id="journey-content">${failure}${state.busy ? "<p class=\"loading-note\">Checking your demo choice...</p>" : ""}${content}</main>${context()}</div>${evidence()}`;
    if (focus) document.getElementById("chapter-heading")?.focus({preventScroll: true});
  }

  function validateReplay(data) {
    if (!data || !data.choices || typeof data.choices.signed !== "boolean" || typeof data.choices.approved !== "boolean" || !Array.isArray(data.orders) || !Array.isArray(data.timeline) || !Array.isArray(data.messages) || !Array.isArray(data.metrics) || !Array.isArray(data.logs) || !data.signature || !data.expiry || !data.morning || !data.counts) throw new Error("The replay returned an incomplete result. Please retry.");
    for (const count of ["pages", "automatic_incidents_handled", "approved_actions"]) if (!Number.isInteger(data.counts[count]) || data.counts[count] < 0) throw new Error("The replay counts could not be read. Please retry.");
    if (data.metrics.some((sample) => !Number.isFinite(sample.old_rate) || !Number.isFinite(sample.new_rate) || sample.old_rate < 0 || sample.new_rate < 0 || sample.old_rate > 1 || sample.new_rate > 1)) throw new Error("The replay metrics could not be read. Please retry.");
    for (const key of ["lines", "kept", "undone", "by_hand"]) if (!Array.isArray(data.morning[key])) throw new Error("The morning record could not be read. Please retry.");
    if (data.messages.some((message) => !Array.isArray(message.lines))) throw new Error("The wake-up record could not be read. Please retry.");
    return data;
  }

  async function load(signed, approved, success) {
    state.controller?.abort();
    const request = ++state.request;
    const controller = new AbortController();
    state.controller = controller;
    state.busy = true;
    state.error = null;
    state.retry = () => load(signed, approved, success);
    live.textContent = "Checking your demo choice.";
    render();
    let timedOut = false;
    const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, 12000);
    try {
      const response = await fetch(`/demo/replay?signed=${signed}&approved=${approved}`, {signal: controller.signal, headers: {Accept: "application/json"}, cache: "no-store"});
      if (!response.ok) throw new Error("The replay is temporarily unavailable. Please retry.");
      const replay = validateReplay(await response.json());
      if (request !== state.request) return;
      if (replay.choices.signed !== signed || replay.choices.approved !== approved) throw new Error("The replay returned a different choice. Please retry.");
      const hadReplay = Boolean(state.replay);
      state.replay = replay;
      state.busy = false;
      state.retry = null;
      success?.();
      render({focus: Boolean(success) && hadReplay});
    } catch (error) {
      if (request !== state.request) return;
      if (error.name === "AbortError" && !timedOut) return;
      state.busy = false;
      state.error = timedOut ? "The replay took too long to respond. Please retry." : error instanceof TypeError ? "The replay could not connect. Please retry." : error.message || "The replay could not be read. Please retry.";
      live.textContent = state.error;
      render();
    } finally {
      clearTimeout(timeout);
      if (request === state.request) state.controller = null;
    }
  }

  function show(view, scene) {
    state.view = view;
    if (scene) state.nightScene = scene;
    state.error = null;
    live.textContent = view === "dusk" ? "Before bed. Review the two demo orders." : view === "dawn" ? "Over coffee. The actual replay counts and morning decisions." : scene === "inventory" ? "During the night. The inventory wake-up needs Priya." : "During the night. The checkout alert and permission checks.";
    render({focus: true});
  }

  document.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action], [data-step]");
    if (!target || target.disabled || state.busy) return;
    if (target.dataset.step) {
      show(target.dataset.step, target.dataset.step === "night" ? "inventory" : undefined);
      return;
    }
    const action = target.dataset.action;
    if (action === "retry") { state.retry?.(); return; }
    if (action === "sign" || action === "unsigned") {
      const signed = action === "sign";
      load(signed, true, () => {
        state.signedChoice = signed;
        state.approvedChoice = null;
        state.view = "night";
        state.nightScene = "inventory";
        live.textContent = signed ? "Demo orders signed. The next event needs Priya's approval." : "Demo orders left unsigned. Watch cannot act alone.";
      });
    } else if (action === "approve" || action === "decline") {
      const approved = action === "approve";
      load(state.signedChoice, approved, () => {
        state.approvedChoice = approved;
        state.view = "night";
        state.nightScene = "inventory";
        live.textContent = approved ? "Demo fallback approved by Priya. Both checkout paths recover." : "Demo fallback declined. The suggestion makes no change.";
      });
    } else if (action === "night" || action === "inventory") show("night", "inventory");
    else if (action === "checkout") show("night", "checkout");
    else if (action === "dawn") show("dawn");
    else if (action === "restart") {
      load(true, true, () => {
        state.signedChoice = null;
        state.approvedChoice = null;
        state.view = "dusk";
        state.nightScene = "inventory";
        live.textContent = "Replay reset. Choose whether to sign the demo orders.";
      });
    }
  });

  window.addEventListener("pagehide", () => {
    ++state.request;
    state.controller?.abort();
  });

  load(true, true, () => { live.textContent = "Demo ready. Review the orders before bed."; });
})();
