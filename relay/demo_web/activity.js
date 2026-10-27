"use strict";

(() => {
  const root = document.getElementById("activity-root");
  const announce = document.getElementById("activity-announcement");
  const captureTime = document.getElementById("capture-time");
  const source = document.body.dataset.static === "1" ? "activity.json" : "/activity.json";
  const state = {data: null, filter: "all", selected: null, controller: null, request: 0};
  const flows = [["all", "All runs"], ["dusk", "Dusk"], ["watch", "Watch"], ["dawn", "Dawn"]];

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = String(text);
    return element;
  }

  function readable(value) {
    return String(value || "").replace(/_/g, " ").trim();
  }

  function dateText(value) {
    const date = new Date(value);
    return value && Number.isFinite(date.getTime()) ? date.toLocaleString(undefined, {
      day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", timeZoneName: "short",
    }) : "Not recorded";
  }

  function safeUrl(value) {
    try {
      const project = new URL(state.data.project.web_url);
      const target = new URL(String(value));
      const prefix = project.pathname.replace(/\/+$/, "");
      if (project.protocol !== "https:" || project.username || project.password || !prefix || prefix === "/") return null;
      if (target.protocol !== "https:" || target.username || target.password || target.origin !== project.origin) return null;
      if (target.search || (target.hash && !/^#note_\d+$/.test(target.hash))) return null;
      if (target.pathname !== prefix && !target.pathname.startsWith(prefix + "/")) return null;
      return target.href;
    } catch (_) {
      return null;
    }
  }

  function link(value, text, className) {
    const href = safeUrl(value);
    const element = node(href ? "a" : "span", className, text);
    if (href) {
      element.href = href;
      element.target = "_blank";
      element.rel = "noopener noreferrer";
    }
    return element;
  }

  function statusBadge(value) {
    const status = String(value || "unknown").toLowerCase();
    const finished = ["finished", "completed", "success"].includes(status);
    const failed = ["failed", "error"].includes(status);
    const pending = ["running", "created", "pending", "stopped", "cancelled", "canceled"].includes(status);
    const badge = node("span", "activity-badge" + (finished ? " is-finished" : failed ? " is-failed" : pending ? " is-pending" : ""),
      readable(status).replace(/^./, (letter) => letter.toUpperCase()));
    badge.setAttribute("aria-label", "Recorded status: " + readable(status));
    return badge;
  }

  function empty(title, message) {
    const section = node("section", "activity-empty");
    section.append(node("h2", "", title), node("p", "", message));
    return section;
  }

  function artifactCard(artifact) {
    const card = node("article", "activity-artifact");
    const heading = node("div", "activity-artifact-head");
    const title = artifact.title || "Merge request !" + String(artifact.iid || "");
    heading.append(link(artifact.web_url, title, "activity-artifact-title"));
    heading.append(node("span", "activity-badge", artifact.draft ? "Draft" : readable(artifact.state || "State not recorded")));
    card.append(heading);
    if (artifact.iid) card.append(node("p", "", "GitLab merge request !" + String(artifact.iid)));
    if (artifact.validation) card.append(node("p", "activity-validation", "Code check: " + readable(artifact.validation)));
    if (artifact.text) {
      const details = node("details", "activity-step-details");
      details.append(node("summary", "", "Read the posted response"), node("pre", "", artifact.text));
      card.append(details);
    }
    if (Array.isArray(artifact.changed_files) && artifact.changed_files.length) {
      const files = node("div", "activity-artifact-files");
      artifact.changed_files.slice(0, 20).forEach((path) => files.append(node("code", "", path)));
      card.append(files);
    }
    if (artifact.sha) card.append(node("p", "", "Source commit " + String(artifact.sha).slice(0, 12)));
    return card;
  }

  function stepItem(step, index) {
    const failed = ["failed", "error"].includes(String(step.status).toLowerCase());
    const item = node("li", "activity-step" + (step.kind === "agent" ? " is-agent" : "") + (failed ? " is-failed" : ""));
    item.dataset.stepIndex = String(index);
    item.append(node("span", "activity-step-number", index + 1));
    const meta = node("div", "activity-step-meta");
    meta.append(node("span", "activity-component", readable(step.component) || (step.kind === "agent" ? "Agent" : "Tool")));
    if (step.name) meta.append(node("span", "", readable(step.name)));
    if (step.status) meta.append(node("span", "", readable(step.status)));
    item.append(meta, node("h4", "activity-step-title", step.title || (step.kind === "agent" ? "Agent decision" : "Tool call")));
    if (step.text) {
      const details = node("details", "activity-step-details");
      details.append(node("summary", "", step.kind === "agent" ? "Read the agent's recorded answer" : "Read captured details"),
        node("pre", "", String(step.text)));
      item.append(details);
    }
    return item;
  }

  function runDetail(run) {
    const article = node("article", "activity-detail");
    article.setAttribute("aria-labelledby", "run-title");
    const head = node("header", "activity-detail-head");
    const top = node("div", "activity-detail-topline");
    top.append(node("span", "activity-run-flow", readable(run.flow) + " · Session " + String(run.id)), statusBadge(run.status));
    const title = node("h2", "", run.title || "GitLab Duo session " + String(run.id));
    title.id = "run-title";
    title.tabIndex = -1;
    head.append(top, title, link(run.web_url, "Open the original GitLab session", "activity-external"));
    const facts = node("div", "activity-detail-facts");
    facts.append(node("span", "", "Started " + dateText(run.created_at)));
    if (run.execution_status) facts.append(node("span", "", "Execution: " + String(run.execution_status)));
    head.append(facts);
    article.append(head);

    const artifacts = node("section", "activity-artifacts");
    artifacts.setAttribute("aria-label", "Work produced");
    artifacts.append(node("h3", "activity-section-title", "What this run produced"));
    if (run.artifacts.length) run.artifacts.forEach((artifact) => artifacts.append(artifactCard(artifact)));
    else artifacts.append(node("p", "activity-no-artifact", "No linked artifact is included in this capture. A finished run alone does not establish that a change was created."));
    article.append(artifacts);

    if (run.errors.length) {
      const errors = node("section", "activity-errors");
      errors.append(node("h3", "", "Errors in the captured record"));
      run.errors.forEach((error) => errors.append(node("p", "", String(error))));
      article.append(errors);
    }
    const trace = node("section", "activity-trace");
    trace.append(node("h3", "activity-section-title", "The execution, step by step"),
      node("p", "activity-trace-intro", "Recorded component and tool events, in the order returned by GitLab."));
    if (run.steps.length) {
      const steps = node("ol", "activity-steps");
      steps.setAttribute("aria-label", "Recorded execution steps");
      run.steps.forEach((step, index) => steps.append(stepItem(step, index)));
      trace.append(steps);
    } else trace.append(node("p", "activity-no-artifact", "This capture has no step details. Open the original session for GitLab's record."));
    article.append(trace, node("p", "activity-record-note", "This view preserves the captured result. It does not start an agent, approve a merge request or change a service."));
    return article;
  }

  function render() {
    const data = state.data;
    root.replaceChildren();
    root.setAttribute("aria-busy", "false");
    const runs = data.runs;
    const summary = node("div", "activity-summary");
    const finished = runs.filter((run) => ["finished", "completed"].includes(run.status.toLowerCase())).length;
    const artifactCount = runs.reduce((count, run) => count + run.artifacts.length, 0);
    for (const [number, label] of [[runs.length, "sessions captured"], [finished, "finished sessions"], [artifactCount, "linked artifacts"]]) {
      const stat = node("div", "activity-stat");
      stat.append(node("strong", "", number), node("span", "", label));
      summary.append(stat);
    }
    root.append(summary);
    const tools = node("div", "activity-tools");
    const filters = node("nav", "activity-filters");
    filters.setAttribute("aria-label", "Filter executions by flow");
    flows.forEach(([value, label]) => {
      const button = node("button", "activity-filter" + (state.filter === value ? " active" : ""), label);
      button.type = "button";
      button.dataset.flow = value;
      button.setAttribute("aria-pressed", String(state.filter === value));
      button.append(node("span", "activity-filter-count", value === "all" ? runs.length : runs.filter((run) => run.flow === value).length));
      filters.append(button);
    });
    const reload = node("button", "activity-reload", "Reload saved snapshot");
    reload.type = "button";
    reload.dataset.action = "reload";
    tools.append(filters, reload);
    root.append(tools);
    const shown = runs.filter((run) => state.filter === "all" || run.flow === state.filter);
    if (!shown.length) {
      const flow = state.filter === "all" ? "agent" : readable(state.filter);
      root.append(empty("No " + flow + " run captured yet.", "This snapshot contains no execution for that selection. An installed flow is not evidence that it ran. Choose another flow or inspect the project on GitLab."));
      announce.textContent = "No captured " + flow + " runs.";
    } else {
      const selected = shown.find((run) => String(run.id) === String(state.selected)) || shown[0];
      state.selected = selected.id;
      const layout = node("div", "activity-layout");
      const list = node("nav", "activity-run-list");
      list.setAttribute("aria-label", "Choose a captured session");
      shown.forEach((run) => {
        const choice = node("button", "activity-run-choice" + (run.id === selected.id ? " selected" : ""));
        choice.type = "button";
        choice.dataset.runId = String(run.id);
        choice.setAttribute("aria-pressed", String(run.id === selected.id));
        choice.append(node("span", "activity-run-flow", readable(run.flow)),
          node("strong", "", run.title || "GitLab Duo session"));
        const meta = node("span", "activity-run-meta");
        meta.append(node("span", "", "#" + String(run.id)), statusBadge(run.status));
        choice.append(meta);
        list.append(choice);
      });
      layout.append(list, runDetail(selected));
      root.append(layout);
      announce.textContent = String(shown.length) + " captured sessions. Showing session " + String(selected.id) + ".";
    }
    const project = node("p", "activity-project", "Source project: ");
    project.append(link(data.project.web_url, data.project.name || data.project.web_url || "GitLab project", ""));
    root.append(project);
  }

  function normalize(data) {
    if (!data || data.version !== 1 || !data.project || !Array.isArray(data.runs)) throw new Error("The captured record is incomplete.");
    data.runs = data.runs.filter((run) => run && (typeof run.id === "number" || typeof run.id === "string")).slice(0, 100).map((run) => ({
      ...run,
      flow: ["dusk", "watch", "dawn"].includes(run.flow) ? run.flow : "other",
      status: String(run.status || "unknown"),
      steps: (Array.isArray(run.steps) ? run.steps : []).filter((step) => step && typeof step === "object"),
      artifacts: (Array.isArray(run.artifacts) ? run.artifacts : []).filter((item) => item && typeof item === "object"),
      errors: Array.isArray(run.errors) ? run.errors : [],
    }));
    return data;
  }

  async function load() {
    const request = ++state.request;
    state.controller?.abort();
    const controller = new AbortController();
    state.controller = controller;
    const timeout = setTimeout(() => controller.abort(), 12000);
    root.setAttribute("aria-busy", "true");
    root.querySelectorAll("button").forEach((button) => { button.disabled = true; });
    announce.textContent = "Loading the saved GitLab execution record.";
    try {
      const response = await fetch(source, {signal: controller.signal, cache: "no-store", credentials: "same-origin"});
      if (!response.ok) throw new Error("The saved execution record is unavailable.");
      const data = normalize(await response.json());
      if (request !== state.request) return;
      state.data = data;
      captureTime.textContent = dateText(data.captured_at);
      if (data.captured_at && Number.isFinite(new Date(data.captured_at).getTime())) captureTime.dateTime = data.captured_at;
      render();
    } catch (_) {
      if (request !== state.request) return;
      root.replaceChildren(empty("The execution record could not be loaded.", "The capture may still be publishing, or the connection may have failed. Retry to read the saved record."));
      const button = node("button", "button secondary", "Retry loading record");
      button.type = "button";
      button.dataset.action = "reload";
      root.firstChild.append(button);
      captureTime.textContent = "Unavailable";
      root.setAttribute("aria-busy", "false");
      announce.textContent = "Execution record unavailable. Retry loading the record.";
    } finally {
      clearTimeout(timeout);
    }
  }

  root.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button || button.disabled) return;
    if (button.dataset.action === "reload") { load(); return; }
    if (button.dataset.flow) {
      state.filter = button.dataset.flow;
      render();
      Array.from(root.querySelectorAll("[data-flow]")).find((item) => item.dataset.flow === state.filter)?.focus({preventScroll: true});
    } else if (button.dataset.runId) {
      state.selected = button.dataset.runId;
      render();
      Array.from(root.querySelectorAll("[data-run-id]")).find((item) => item.dataset.runId === String(state.selected))?.focus({preventScroll: true});
    }
  });
  window.addEventListener("pagehide", () => { ++state.request; state.controller?.abort(); });
  load();
})();
