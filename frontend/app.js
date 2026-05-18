const API = '/api/tasks';

// ── 전역 상태 ─────────────────────────────────────────────────────────────────
let tasks = [];
let editingTaskId = null;

// ── 초기화 ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  updateThemeIcon();
  fetchAndRender();
  setInterval(fetchAndRender, 3000);

  document.getElementById('addForm').addEventListener('submit', handleAdd);
  document.getElementById('editForm').addEventListener('submit', handleEdit);
  document.getElementById('cancelBtn').addEventListener('click', closeModal);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
});

// ── 테마 ──────────────────────────────────────────────────────────────────────
function toggleTheme() {
  const isDark = document.documentElement.classList.toggle('dark');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
  updateThemeIcon();
}

function updateThemeIcon() {
  const isDark = document.documentElement.classList.contains('dark');
  document.getElementById('themeIcon').textContent = isDark ? '☀️' : '🌙';
}

// ── API ───────────────────────────────────────────────────────────────────────
async function fetchAndRender() {
  try {
    const res = await fetch(API);
    if (!res.ok) return;
    tasks = await res.json();
    renderList();
  } catch { /* 폴링 중 네트워크 오류 — 조용히 무시 */ }
}

async function handleAdd(e) {
  e.preventDefault();
  const btn = document.getElementById('addBtn');
  const errEl = document.getElementById('addError');
  errEl.classList.add('hidden');
  btn.disabled = true;

  const dueAtRaw = document.getElementById('newDueAt').value;
  const body = {
    title: document.getElementById('newTitle').value.trim(),
    status: document.getElementById('newStatus').value,
    ...(dueAtRaw && { due_at: dueAtRaw + ':00' }),
  };

  try {
    const res = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const data = await res.json();
      showError(errEl, data.error || '추가에 실패했습니다');
      return;
    }
    document.getElementById('addForm').reset();
    await fetchAndRender();
  } catch {
    showError(errEl, '서버에 연결할 수 없습니다');
  } finally {
    btn.disabled = false;
  }
}

async function handleEdit(e) {
  e.preventDefault();
  if (!editingTaskId) return;
  const btn = document.getElementById('saveBtn');
  const errEl = document.getElementById('editError');
  errEl.classList.add('hidden');
  btn.disabled = true;

  const dueAtRaw = document.getElementById('editDueAt').value;
  const body = {
    title: document.getElementById('editTitle').value.trim(),
    description: document.getElementById('editDescription').value || null,
    status: document.getElementById('editStatus').value,
    due_at: dueAtRaw ? dueAtRaw + ':00' : null,
  };

  try {
    const res = await fetch(`${API}/${editingTaskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const data = await res.json();
      showError(errEl, data.error || '수정에 실패했습니다');
      return;
    }
    closeModal();
    await fetchAndRender();
  } catch {
    showError(errEl, '서버에 연결할 수 없습니다');
  } finally {
    btn.disabled = false;
  }
}

async function handleDelete(taskId) {
  try {
    const res = await fetch(`${API}/${taskId}`, { method: 'DELETE' });
    if (!res.ok) return;
    await fetchAndRender();
  } catch { /* 삭제 실패 시 목록 유지 */ }
}

// ── 렌더링 ────────────────────────────────────────────────────────────────────
function renderList() {
  const list = document.getElementById('taskList');
  const empty = document.getElementById('emptyState');

  if (tasks.length === 0) {
    list.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');
  list.innerHTML = tasks.map(renderCard).join('');
}

function renderCard(task) {
  const due = formatDueAt(task.due_at);
  const st = statusInfo(task.status);

  return `
    <div
      class="rounded-xl shadow-lg bg-white/90 dark:bg-gray-800/90 backdrop-blur-md p-4 cursor-pointer hover:shadow-xl transition-shadow"
      onclick="openEditModal(${task.id})"
    >
      <div class="flex justify-between items-start gap-2">
        <h3 class="text-sm font-medium leading-snug flex-1 break-words">${escHtml(task.title)}</h3>
        <button
          class="shrink-0 min-h-[44px] min-w-[44px] flex items-center justify-center rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-300 hover:text-red-400 transition-colors"
          onclick="event.stopPropagation(); toggleConfirm(${task.id})"
          aria-label="삭제"
        >🗑</button>
      </div>

      <div class="flex justify-between items-center mt-3">
        <span class="text-xs font-medium px-2.5 py-1 rounded-full ${st.cls}">${st.label}</span>
        ${due
          ? `<span class="text-xs font-mono ${due.overdue ? 'text-red-500 font-semibold' : 'text-gray-400 dark:text-gray-500'}">${due.label}</span>`
          : '<span class="text-xs text-gray-300 dark:text-gray-600">—</span>'
        }
      </div>

      <div id="confirm-${task.id}" class="hidden mt-3 pt-3 border-t border-gray-100 dark:border-gray-700" onclick="event.stopPropagation()">
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">정말 삭제할까요?</p>
        <div class="flex gap-2">
          <button
            onclick="handleDelete(${task.id})"
            class="flex-1 rounded-xl bg-red-500 hover:bg-red-600 text-white text-xs font-medium py-2 min-h-[44px] transition-colors"
          >삭제</button>
          <button
            onclick="toggleConfirm(${task.id})"
            class="flex-1 rounded-xl border border-gray-200 dark:border-gray-600 text-xs py-2 min-h-[44px] hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >취소</button>
        </div>
      </div>
    </div>
  `;
}

// ── 모달 ──────────────────────────────────────────────────────────────────────
function openEditModal(taskId) {
  const task = tasks.find(t => t.id === taskId);
  if (!task) return;
  editingTaskId = taskId;

  document.getElementById('editTitle').value = task.title;
  document.getElementById('editDescription').value = task.description || '';
  document.getElementById('editStatus').value = task.status;
  // API 응답 '2026-05-12T18:00:00' → datetime-local 형식 '2026-05-12T18:00'
  document.getElementById('editDueAt').value = task.due_at ? task.due_at.slice(0, 16) : '';
  document.getElementById('editError').classList.add('hidden');

  document.getElementById('modalOverlay').classList.remove('hidden');
  document.getElementById('editTitle').focus();
}

function closeModal() {
  document.getElementById('modalOverlay').classList.add('hidden');
  editingTaskId = null;
}

// ── 삭제 확인 토글 ────────────────────────────────────────────────────────────
function toggleConfirm(taskId) {
  const el = document.getElementById(`confirm-${taskId}`);
  if (el) el.classList.toggle('hidden');
}

// ── 유틸 ──────────────────────────────────────────────────────────────────────
function formatDueAt(dueAtStr) {
  if (!dueAtStr) return null;
  // 백엔드가 UTC로 저장 — 'Z'를 붙여 UTC로 명시 파싱
  const dueDate = new Date(dueAtStr.endsWith('Z') ? dueAtStr : dueAtStr + 'Z');
  if (isNaN(dueDate)) return null;

  const now = new Date();
  const todayUtc = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  const dueUtc  = Date.UTC(dueDate.getUTCFullYear(), dueDate.getUTCMonth(), dueDate.getUTCDate());
  const days = Math.round((dueUtc - todayUtc) / 86400000);

  const hh = String(dueDate.getUTCHours()).padStart(2, '0');
  const mm = String(dueDate.getUTCMinutes()).padStart(2, '0');
  const prefix = days >= 0 ? `D-${days}` : `D+${Math.abs(days)}`;

  return { label: `${prefix} ${hh}:${mm}`, overdue: days < 0 };
}

function statusInfo(status) {
  const map = {
    todo:        { label: 'Todo',        cls: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300' },
    in_progress: { label: 'In Progress', cls: 'bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300' },
    done:        { label: 'Done',        cls: 'bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300' },
  };
  return map[status] || map.todo;
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove('hidden');
}
