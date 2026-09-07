let state = { extensions: {} };
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function refresh() {
  try {
    const response = await fetch('/api/status', { cache: 'no-store' });
    state = await response.json();
    document.getElementById('extensions-count').textContent = state.summary.extensions;
    document.getElementById('endpoints-count').textContent = state.summary.endpoints;
    document.getElementById('channels-count').textContent = state.summary.active_channels;
    const health = document.getElementById('ami-health');
    health.textContent = state.health.ami_connected ? 'AMI connecté' : 'AMI déconnecté';
    health.className = 'badge ' + (state.health.ami_connected ? 'ok' : 'bad');
    render();
  } catch (error) {
    const health = document.getElementById('ami-health');
    health.textContent = 'Agent indisponible'; health.className = 'badge bad';
  }
}

function render() {
  const search = document.getElementById('search').value.toLowerCase();
  const filter = document.getElementById('status-filter').value;
  const rows = Object.values(state.extensions || {})
    .filter(item => item.extension.toLowerCase().includes(search))
    .filter(item => !filter || item.class === filter)
    .sort((a,b) => a.priority - b.priority || a.extension.localeCompare(b.extension, undefined, {numeric:true}));
  const tbody = document.getElementById('extensions');
  tbody.innerHTML = rows.length ? rows.map(item => `<tr><td><strong>${esc(item.extension)}</strong></td><td>${esc(item.context)}</td><td><span class="${esc(item.class)}">${esc(item.text)}</span></td><td>${esc(new Date(item.updated_at).toLocaleTimeString())}</td></tr>`).join('') : '<tr><td colspan="4">Aucune extension correspondante.</td></tr>';
}

document.getElementById('search').addEventListener('input', render);
document.getElementById('status-filter').addEventListener('change', render);
setInterval(refresh, 1000); refresh();
