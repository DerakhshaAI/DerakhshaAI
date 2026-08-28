/* اپ درخشا — منطق رابط کاربری */

const MARK = `<img src="logo.png" alt="" class="logo-mark" width="22" height="22">`;
const MARK_HERO = `<img src="logo.png" alt="درخشا" class="logo-hero" width="96" height="96">`;

const CAP = {
  tree: {
    name: "درخت دانش",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="1.8"><path d="M12 20V10"/><path d="M12 10L7 5M12 10l5-5M12 14L6 12M12 14l6-2"/><circle cx="7" cy="5" r="1.5" fill="#22d3ee"/><circle cx="17" cy="5" r="1.5" fill="#a78bfa"/><circle cx="6" cy="12" r="1.3" fill="#3b82f6"/><circle cx="18" cy="12" r="1.3" fill="#22d3ee"/></svg>`
  },
  relations: {
    name: "روابط مفاهیم",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.8"><circle cx="6" cy="6" r="2.2" fill="#a78bfa"/><circle cx="18" cy="6" r="2.2" fill="#22d3ee"/><circle cx="12" cy="18" r="2.2" fill="#3b82f6"/><path d="M8 7.5L10.5 15M16 7.5L13.5 15M8.5 6h7"/></svg>`
  },
  multi_step: {
    name: "استدلال چندمرحله‌ای",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.8"><path d="M5 6h6v4H5zM13 10h6v4h-6zM5 14h6v4H5z" fill="rgba(59,130,246,.2)"/><path d="M11 8h2M11 12h2" stroke-linecap="round"/></svg>`
  },
  consistency_check: {
    name: "کنترل صحت",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="1.8"><path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M9 12l2 2 4-4" stroke-linecap="round"/></svg>`
  },
  clarify: {
    name: "مدیریت ابهام",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="1.8"><circle cx="12" cy="12" r="9"/><path d="M12 16h.01M10 9a2 2 0 013.5 1.5c0 1.5-2 2-2 3" stroke-linecap="round"/></svg>`
  },
  discovery: {
    name: "کشف واژه",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="1.8"><circle cx="11" cy="11" r="6"/><path d="M20 20l-3.5-3.5" stroke-linecap="round"/><path d="M11 8v6M8 11h6" stroke-linecap="round"/></svg>`
  },
  language: {
    name: "قشر زبان",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#a78bfa" stroke-width="1.8"><path d="M4 6h16M4 12h10M4 18h13"/><circle cx="18" cy="12" r="2" fill="#a78bfa"/></svg>`
  },
  default: {
    name: "موتور درخشا",
    svg: `<svg viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="1.6"><path d="M12 2l7 5v7c0 4-3 6.5-7 7.5C8 20.5 5 18 5 14V7l7-5z"/></svg>`
  }
};

function capFor(route, source) {
  const r = (route || "").toLowerCase();
  const s = (source || "");
  if (r === "relations" || s.includes("روابط")) return CAP.relations;
  if (r === "multi_step" || s.includes("استدلال")) return CAP.multi_step;
  if (r === "consistency_check" || s.includes("صحت")) return CAP.consistency_check;
  if (r === "clarify" || s.includes("شفاف") || s.includes("ابهام")) return CAP.clarify;
  if (s.includes("کشف") || r === "discovery") return CAP.discovery;
  if (r === "tree" || s.includes("هسته") || s.includes("سند") || s.includes("درخت")) return CAP.tree;
  if (s.includes("معنا") || s.includes("زبان")) return CAP.language;
  return CAP.default;
}

let user = JSON.parse(localStorage.getItem("derakhsha_user") || "null");
let sessions = JSON.parse(localStorage.getItem("derakhsha_sessions") || "[]");
let currentId = localStorage.getItem("derakhsha_current") || null;
let authPhase = "form";
let typingLock = false;

const sid = () => (user && user.phone ? "u_" + user.phone : "anon") + "_" + (currentId || "x");

function save() {
  localStorage.setItem("derakhsha_sessions", JSON.stringify(sessions));
  if (currentId) localStorage.setItem("derakhsha_current", currentId);
}
function cur() {
  return sessions.find((s) => s.id === currentId) || null;
}
function ensure() {
  if (currentId && cur()) return cur();
  const s = { id: "s_" + Date.now(), title: "گفتگوی جدید", messages: [], updated: Date.now() };
  sessions.unshift(s);
  currentId = s.id;
  save();
  return s;
}

function show(v) {
  document.querySelectorAll(".view").forEach((e) => e.classList.remove("on"));
  document.getElementById("v-" + v).classList.add("on");
  if (v === "auth") renderAuth();
  closeAll();
}

function hero() {
  return `<div class="hero" id="welcome">
    ${MARK_HERO}
    <h1>درخشا</h1>
    <p>سامانه هوش مصنوعی فارسی با معماری درخت دانش</p>
    <div class="chips">
      <button type="button" onclick="ask(this)">درخشا چیست؟</button>
      <button type="button" onclick="ask(this)">درخت دانش چیست؟</button>
      <button type="button" onclick="ask(this)">سازندگان کیانند؟</button>
    </div>
  </div>`;
}

function renderMsgs() {
  const box = document.getElementById("msgs");
  const s = cur();
  if (!s || !s.messages.length) {
    box.innerHTML = hero();
    return;
  }
  box.innerHTML = "";
  s.messages.forEach((m) => {
    if (m.role === "user") addU(m.text, false);
    else addBInstant(m.text, m.meta);
  });
  box.scrollTop = box.scrollHeight;
}

function renderHist() {
  const list = document.getElementById("hist");
  if (!sessions.length) {
    list.innerHTML = '<p style="color:var(--muted);font-size:.85rem;padding:12px;text-align:center">هنوز گفتگویی نیست</p>';
    return;
  }
  list.innerHTML = sessions
    .map((s) => {
      const d = new Date(s.updated).toLocaleString("fa-IR", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
      return `<div class="hi ${s.id === currentId ? "active" : ""}">
        <button type="button" class="pick" onclick="load('${s.id}')">
          <div class="t">${esc(s.title)}</div>
          <div class="d">${d}</div>
        </button>
        <button type="button" class="del" onclick="delS('${s.id}',event)">×</button>
      </div>`;
    })
    .join("");
}

function load(id) {
  currentId = id;
  save();
  renderMsgs();
  renderHist();
  show("chat");
}

function delS(id, ev) {
  if (ev) ev.stopPropagation();
  sessions = sessions.filter((x) => x.id !== id);
  if (currentId === id) {
    currentId = sessions[0] ? sessions[0].id : null;
    if (!currentId) ensure();
  }
  save();
  renderHist();
  renderMsgs();
  toast("حذف شد");
}

function newChat() {
  const s = { id: "s_" + Date.now(), title: "گفتگوی جدید", messages: [], updated: Date.now() };
  sessions.unshift(s);
  currentId = s.id;
  save();
  show("chat");
  renderMsgs();
  renderHist();
  toast("گفتگوی جدید");
}

function openHist() {
  document.getElementById("dr").classList.add("on");
  document.getElementById("ov").classList.add("on");
  renderHist();
}

function closeAll() {
  document.getElementById("dr").classList.remove("on");
  document.getElementById("ov").classList.remove("on");
  document.getElementById("modal").classList.remove("on");
}

async function send() {
  if (typingLock) return;
  const inp = document.getElementById("inp");
  const text = inp.value.trim();
  if (!text) return;

  const s = ensure();
  if (s.title === "گفتگوی جدید") s.title = text.slice(0, 36) + (text.length > 36 ? "…" : "");
  const w = document.getElementById("welcome");
  if (w) w.remove();

  s.messages.push({ role: "user", text });
  addU(text, true);
  inp.value = "";
  autoH(inp);
  s.updated = Date.now();
  save();

  typingLock = true;
  document.getElementById("sendBtn").disabled = true;
  showTyping(CAP.default);

  try {
    const data = await chat(text, sid());
    const cap = capFor(data.route, data.source);
    updateTypingCap(cap);
    await sleep(200);
    hideTyping();
    const meta = { src: data.source, conf: data.confidence, branch: data.branch, route: data.route };
    const answer = data.answer || "پاسخی دریافت نشد";
    s.messages.push({ role: "bot", text: answer, meta });
    s.updated = Date.now();
    save();
    await typeBot(answer, meta, cap);
    renderHist();
  } catch (err) {
    hideTyping();
    const msg = "اتصال به موتور برقرار نشد. سرور را بررسی کنید یا از حالت آفلاین استفاده کنید.";
    s.messages.push({ role: "bot", text: msg, meta: { src: "خطا", conf: 0, route: "clarify" } });
    await typeBot(msg, { src: "خطا", conf: 0, route: "clarify" }, CAP.clarify);
  } finally {
    typingLock = false;
    document.getElementById("sendBtn").disabled = false;
  }
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function showTyping(cap) {
  const box = document.getElementById("msgs");
  const el = document.createElement("div");
  el.className = "typing";
  el.id = "ty";
  el.innerHTML = `
    <div class="av">${MARK}</div>
    <div>
      <div class="typing-cap" id="tyCap">
        <div class="cap-logo" title="${esc(cap.name)}">${cap.svg} ${esc(cap.name)}</div>
      </div>
      <div class="dots"><i></i><i></i><i></i></div>
    </div>`;
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
}

function updateTypingCap(cap) {
  const el = document.getElementById("tyCap");
  if (!el) return;
  el.innerHTML = `<div class="cap-logo" title="${esc(cap.name)}">${cap.svg} ${esc(cap.name)}</div>`;
}

function hideTyping() {
  const t = document.getElementById("ty");
  if (t) t.remove();
}

function addU(text, sc) {
  const box = document.getElementById("msgs");
  const t = new Date().toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" });
  const d = document.createElement("div");
  d.className = "u";
  d.innerHTML = esc(text) + `<div class="meta">${t}</div>`;
  box.appendChild(d);
  if (sc) box.scrollTop = box.scrollHeight;
}

function addBInstant(text, meta) {
  const cap = capFor(meta && meta.route, meta && meta.src);
  const box = document.getElementById("msgs");
  const t = new Date().toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" });
  const row = document.createElement("div");
  row.className = "bwrap";
  let h = `<div class="av">${MARK}</div><div class="b">`;
  h += `<div class="cap-row"><div class="cap-logo" title="${esc(cap.name)}">${cap.svg} ${esc(cap.name)}</div></div>`;
  h += `<div class="typed">${esc(text)}</div>`;
  if (meta) {
    h += `<div class="pills">`;
    if (meta.src) h += `<span class="pill">${esc(meta.src)}</span>`;
    if (meta.conf != null) h += `<span class="pill">${meta.conf}٪</span>`;
    if (meta.branch) h += `<span class="pill">${esc(meta.branch)}</span>`;
    h += `</div>`;
  }
  h += `<div class="meta">درخشا · ${t}</div></div>`;
  row.innerHTML = h;
  box.appendChild(row);
}

async function typeBot(text, meta, cap) {
  const box = document.getElementById("msgs");
  const t = new Date().toLocaleTimeString("fa-IR", { hour: "2-digit", minute: "2-digit" });
  const row = document.createElement("div");
  row.className = "bwrap";
  let h = `<div class="av">${MARK}</div><div class="b">`;
  h += `<div class="cap-row"><div class="cap-logo" title="${esc(cap.name)}">${cap.svg} ${esc(cap.name)}</div></div>`;
  h += `<div class="typed" id="typingText"></div>`;
  h += `<div class="pills" id="typingPills" style="display:none"></div>`;
  h += `<div class="meta">درخشا · ${t}</div></div>`;
  row.innerHTML = h;
  box.appendChild(row);

  const el = document.getElementById("typingText");
  const pills = document.getElementById("typingPills");
  el.removeAttribute("id");
  pills.removeAttribute("id");

  // تایپ تدریجی
  const step = Math.max(1, Math.floor(text.length / 40));
  for (let i = 0; i < text.length; i += step) {
    el.textContent = text.slice(0, i + step);
    box.scrollTop = box.scrollHeight;
    await sleep(12);
  }
  el.textContent = text;

  if (meta) {
    let ph = "";
    if (meta.src) ph += `<span class="pill">${esc(meta.src)}</span>`;
    if (meta.conf != null) ph += `<span class="pill">${meta.conf}٪</span>`;
    if (meta.branch) ph += `<span class="pill">${esc(meta.branch)}</span>`;
    pills.innerHTML = ph;
    pills.style.display = "flex";
  }
  box.scrollTop = box.scrollHeight;
}

function ask(b) {
  document.getElementById("inp").value = b.textContent;
  send();
}

function autoH(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 140) + "px";
}

function renderAuth() {
  const logged = !!user;
  document.getElementById("authForm").style.display = logged ? "none" : "block";
  document.getElementById("authLogged").style.display = logged ? "block" : "none";
  document.getElementById("authBtnTop").textContent = logged ? (user.name || "حساب") : "ورود";

  if (logged) {
    document.getElementById("authTitle").textContent = "حساب کاربری";
    document.getElementById("authSub").textContent = "وضعیت ورود شما";
    document.getElementById("userInfo").textContent = (user.name || "") + " · " + (user.phone || "");
  } else {
    document.getElementById("authTitle").textContent = "ورود به درخشا";
    document.getElementById("authSub").textContent = "با شماره همراه وارد شوید";
    document.getElementById("otpF").style.display = authPhase === "otp" ? "block" : "none";
    document.getElementById("authBtn").textContent = authPhase === "otp" ? "ورود" : "دریافت کد";
  }
}

function doAuth() {
  if (authPhase === "form") {
    const name = document.getElementById("nameIn").value.trim();
    const phone = document.getElementById("phoneIn").value.trim();
    if (!name) {
      toast("نام را وارد کنید");
      return;
    }
    if (!/^09\d{9}$/.test(phone)) {
      toast("شماره نامعتبر (مثال: 09123456789)");
      return;
    }
    sessionStorage.setItem("p", JSON.stringify({ name, phone }));
    authPhase = "otp";
    document.getElementById("otpF").style.display = "block";
    document.getElementById("authBtn").textContent = "ورود";
    toast("کد: 123456");
  } else {
    if (document.getElementById("otpIn").value.trim() !== "123456") {
      toast("کد نادرست");
      return;
    }
    const p = JSON.parse(sessionStorage.getItem("p") || "{}");
    user = { name: p.name, phone: p.phone };
    localStorage.setItem("derakhsha_user", JSON.stringify(user));
    authPhase = "form";
    renderAuth();
    toast("ورود موفق");
    setTimeout(() => show("chat"), 600);
  }
}

function logout() {
  user = null;
  localStorage.removeItem("derakhsha_user");
  authPhase = "form";
  document.getElementById("otpF").style.display = "none";
  renderAuth();
  toast("خارج شدید");
}

function theme() {
  const n = (document.documentElement.getAttribute("data-theme") || "dark") === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", n);
  localStorage.setItem("derakhsha_theme", n);
  const b = document.getElementById("th");
  if (n === "dark") {
    b.textContent = "☾";
    b.style.color = "#fff";
  } else {
    b.textContent = "☀";
    b.style.color = "#09090b";
  }
}

function rules() {
  document.getElementById("mt").textContent = "قوانین درخشا";
  document.getElementById("mb").innerHTML =
    "<ul style='padding-right:18px;text-align:right'><li>استفاده قانونی و اخلاقی</li><li>مسئولیت محتوا با کاربر</li><li>پاسخ‌ها راهنما هستند و جایگزین مشاوره تخصصی نیستند</li><li>سوءاستفاده ممنوع است</li></ul>";
  document.getElementById("modal").classList.add("on");
  document.getElementById("ov").classList.add("on");
}

function creators() {
  document.getElementById("mt").textContent = "سازندگان";
  document.getElementById("mb").innerHTML =
    "<p style='text-align:right'><strong style='color:var(--accent)'>گروک</strong> و <strong style='color:var(--accent)'>احمدرضا ایزدی</strong></p><p style='margin-top:10px;text-align:right;color:var(--muted)'>طراحی و توسعه مفهومی سامانه استدلال فارسی با معماری درخت دانش.</p>";
  document.getElementById("modal").classList.add("on");
  document.getElementById("ov").classList.add("on");
}

function toast(m) {
  const t = document.getElementById("toast");
  t.textContent = m;
  t.classList.add("on");
  setTimeout(() => t.classList.remove("on"), 2200);
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("y").textContent = new Date().getFullYear();
  const savedTheme = localStorage.getItem("derakhsha_theme");
  if (savedTheme === "light") {
    document.documentElement.setAttribute("data-theme", "light");
    document.getElementById("th").textContent = "☀";
    document.getElementById("th").style.color = "#09090b";
  }
  if (!sessions.length) ensure();
  else if (!currentId || !cur()) currentId = sessions[0].id;
  renderMsgs();
  renderHist();
  renderAuth();
});
