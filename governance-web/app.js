const buttons = document.querySelectorAll('[data-view-button]');
const views = document.querySelectorAll('[data-view]');
const refreshButton = document.querySelector('#refresh-status');
const liveStatus = document.querySelector('#live-status');
let lastDigest = '';

const setText = (selector, value) => {
  const node = document.querySelector(selector);
  if (node) node.textContent = value;
};

const make = (tag, text, className) => {
  const node = document.createElement(tag);
  node.textContent = text;
  if (className) node.className = className;
  return node;
};

const statusLabel = (state) => {
  if (state === 'accepted') return 'Accepted';
  if (state === 'review') return 'Review';
  return 'Not started';
};

const renderStages = (stages) => {
  const body = document.querySelector('#stage-rows');
  if (!body) return;
  body.replaceChildren();
  stages.forEach((stage) => {
    const row = document.createElement('tr');
    row.append(make('td', stage.stage), make('td', stage.capability), make('td', `${stage.weight}%`));
    const statusCell = document.createElement('td');
    statusCell.append(make('span', statusLabel(stage.state), `status ${stage.state}`));
    row.append(statusCell);
    body.append(row);
  });
};

const renderQuality = (gates) => {
  const list = document.querySelector('#quality-checks');
  if (!list) return;
  list.replaceChildren();
  gates.forEach((gate) => {
    const row = document.createElement('div');
    const detail = document.createElement('span');
    detail.append(make('strong', gate.Gate || 'Unnamed gate'));
    detail.append(make('small', gate['Evidence or remaining action'] || 'No evidence recorded'));
    const result = (gate.Result || 'Open').toLowerCase();
    const passed = result === 'pass';
    const state = passed ? 'pass' : result === 'open' ? 'blocked' : 'pending';
    row.append(detail, make('em', passed ? '✓ PASS' : `! ${gate.Result || 'OPEN'}`, state));
    list.append(row);
  });
};

const renderReviews = (reviews) => {
  const list = document.querySelector('#review-list');
  if (!list) return;
  list.replaceChildren();
  if (!reviews.length) {
    list.append(make('div', 'No independent reviews are currently open.'));
    return;
  }
  reviews.forEach((review) => {
    const row = document.createElement('div');
    row.append(make('strong', review.Gate || 'Independent review'));
    row.append(make('small', review['Evidence or remaining action'] || 'Evidence required'));
    list.append(row);
  });
};

const renderExceptions = (exceptions) => {
  const list = document.querySelector('#deviation-list');
  if (!list) return;
  list.replaceChildren();
  exceptions.forEach((exception) => {
    const card = document.createElement('article');
    card.append(make('span', exception.severity, `severity ${exception.severity}`));
    card.append(make('small', exception.owner));
    card.append(make('h4', exception.title || 'Open evidence exception'));
    card.append(make('p', exception.summary));
    list.append(card);
  });
};

const setProgress = (prefix, value) => {
  const progress = Math.max(0, Math.min(100, Number(value) || 0));
  setText(`#${prefix}-progress`, `${progress}%`);
  setText(`#${prefix}-readiness`, `${progress}%`);
  const bar = document.querySelector(`#${prefix}-bar`);
  if (bar) bar.style.width = `${progress}%`;
};

const renderSnapshot = (snapshot) => {
  const { meta, metrics } = snapshot;
  setText('#source-value', `Source: ${meta.sourceOfTruth}`);
  setText('#current-gate', meta.currentGate);
  setText('#updated-at', `Evidence dated ${meta.statusAsOf}`);
  setText('#deployment-status', meta.deploymentStatus);
  setText('#current-message', `${meta.currentGate}. Repository evidence controls the next authorized action.`);
  setText('#quality-title', meta.reviewSource.replace('.md', '').replaceAll('-', ' '));
  setText('#quality-status', meta.reviewStatus);
  setText('#open-review-count', String(metrics.openReviews));
  setText('#exception-count', String(metrics.activeExceptions));
  setProgress('accepted', metrics.acceptedCompletion);
  setProgress('implemented', metrics.implementedCompletion);
  renderStages(snapshot.stages);
  renderQuality(snapshot.qualityGates);
  renderReviews(snapshot.openReviews);
  renderExceptions(snapshot.exceptions);
  lastDigest = meta.contentDigest;
  liveStatus.className = 'live-state connected';
  liveStatus.textContent = `Live · ${meta.contentDigest} · refresh ${meta.refreshSeconds}s`;
};

const refreshStatus = async () => {
  refreshButton.disabled = true;
  try {
    const response = await fetch('/api/governance', { cache: 'no-store' });
    if (!response.ok) throw new Error(`Snapshot unavailable (${response.status})`);
    const snapshot = await response.json();
    if (snapshot.meta.contentDigest !== lastDigest) renderSnapshot(snapshot);
    else {
      liveStatus.className = 'live-state connected';
      liveStatus.textContent = `Live · ${lastDigest} · checked ${new Date().toLocaleTimeString()}`;
    }
  } catch (_error) {
    liveStatus.className = 'live-state disconnected';
    liveStatus.textContent = 'Update unavailable · showing last evidence';
  } finally {
    refreshButton.disabled = false;
  }
};

buttons.forEach((button) => {
  button.addEventListener('click', () => {
    const target = button.dataset.viewButton;
    buttons.forEach((item) => {
      const active = item === button;
      item.classList.toggle('active', active);
      item.setAttribute('aria-selected', String(active));
    });
    views.forEach((view) => {
      view.hidden = view.dataset.view !== target;
    });
  });
});

refreshButton.addEventListener('click', refreshStatus);
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) refreshStatus();
});
refreshStatus();
window.setInterval(refreshStatus, 15000);
