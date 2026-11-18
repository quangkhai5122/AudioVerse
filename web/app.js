'use strict';
const $ = id => document.getElementById(id);
const LOCAL_KEY = 'audioverse-demo-run-id-v1';
const HEADERS = {'Content-Type': 'application/json', 'X-Demo-Actor': 'demo-local'};
let current = null;
let busy = false;
let pendingChoice = null;

async function api(path, options={}) {
  const response = await fetch(path, {...options, headers:{...HEADERS, ...(options.headers || {})}});
  const data = await response.json();
  if (!response.ok) {
    const msg = typeof data.detail === 'string'
      ? data.detail
      : (data.detail && data.detail.message ? data.detail.message : `HTTP ${response.status}`);
    const err = new Error(msg);
    err.status = response.status;
    throw err;
  }
  return data;
}
function el(tag, text, cls) {
  const node = document.createElement(tag);
  node.textContent = text;
  if(cls) node.className = cls;
  return node;
}
async function updateHistory() {
  if (!current) return;
  try {
    const events = await api(`/api/v1/runs/${current.run_id}/events`);
    $('timeline').replaceChildren(...events.map(e => el('li', `${e.from_scene} → ${e.to_scene} (${e.choice_id})`)));
  } catch (error) { $('status').textContent = error.message; }
}
function render(state, preserveStatus = false) {
  current = state;
  $('hint').textContent = `CẢNH ${state.scene.id.toUpperCase()} · PHIÊN BẢN ${state.version}`;
  $('scene-title').textContent = state.scene.title;
  $('scene-text').textContent = state.scene.text;
  $('notes').replaceChildren(...state.scene.memory_notes.map(note => el('li', note)));
  const nodes = state.scene.choices.map(choice => {
    const button = el('button', choice.label, 'choice');
    button.type = 'button';
    button.disabled = false;
    button.addEventListener('click', () => choose(choice.id));
    return button;
  });
  $('choices').replaceChildren(...nodes);
  $('player').pause();
  $('player').src = `/api/v1/audio/${encodeURIComponent(state.scene.id)}.mp3`;
  $('player').load();
  $('start').hidden = true;
  $('reset').hidden = false;
  if (!preserveStatus) {
    $('status').textContent = state.scene.ending ? 'Bạn đã đến một kết cục. Chọn “Chơi lại” để khám phá nhánh khác.' : 'Nghe truyện hoặc chọn cách hành động tiếp.';
  }
  updateHistory();
}
async function newRun() {
  if (busy) return;
  busy = true;
  pendingChoice = null;
  $('status').textContent = 'Đang bắt đầu...';
  try {
    const state = await api('/api/v1/runs', {method:'POST', body:JSON.stringify({story_id:'ben-kia-canh-cua'})});
    localStorage.setItem(LOCAL_KEY, state.run_id);
    render(state);
  } catch (error) { $('status').textContent = `Lỗi: ${error.message}`; }
  finally { busy = false; }
}
async function choose(choiceId) {
  if (!current || busy) return;
  busy = true;
  $('choices').querySelectorAll('button').forEach(b => b.disabled = true);
  $('status').textContent = 'Đang xác nhận lựa chọn...';
  const key = (pendingChoice && pendingChoice.choiceId === choiceId && pendingChoice.version === current.version)
    ? pendingChoice.key
    : crypto.randomUUID().replaceAll('-', '');
  pendingChoice = {choiceId, version: current.version, key};
  try {
    const next = await api(`/api/v1/runs/${current.run_id}/choices`, {method:'POST', body:JSON.stringify({choice_id:choiceId, expected_version:current.version, idempotency_key:key})});
    pendingChoice = null;
    render(next);
  } catch (error) {
    if (error.status) pendingChoice = null;
    if (error.status === 409 && current) {
      try {
        const refreshed = await api(`/api/v1/runs/${encodeURIComponent(current.run_id)}`);
        render(refreshed, true);
        $('status').textContent = 'Phiên truyện đã thay đổi (409); đã đồng bộ trạng thái mới nhất.';
        return;
      } catch (_) {}
    }
    if(current) render(current, true);
    $('status').textContent = `Lỗi: ${error.message}. Tải lại trang nếu phiên đã thay đổi.`;
  } finally {busy=false;}
}
$('start').addEventListener('click',newRun);
$('reset').addEventListener('click',newRun);
(async()=>{
  const rid = localStorage.getItem(LOCAL_KEY);
  if(!rid) return;
  try {render(await api(`/api/v1/runs/${encodeURIComponent(rid)}`));}
  catch (_) {localStorage.removeItem(LOCAL_KEY);}
})();
