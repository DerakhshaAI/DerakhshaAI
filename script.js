/* ===== View Switching ===== */
function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const view = document.getElementById('view-' + name);
  if (view) view.classList.add('active');
  const btn = document.querySelector(`.nav-btn[data-view="${name}"]`);
  if (btn) btn.classList.add('active');
}

/* ===== Chat (User Interface) ===== */
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');

function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  appendMessage('user', text);
  chatInput.value = '';
  chatInput.style.height = 'auto';

  // شبیه‌سازی پاسخ درخشا
  setTimeout(() => {
    const reply = generateReply(text);
    appendMessage('bot', reply);
  }, 600 + Math.random() * 400);
}

function appendMessage(role, text) {
  const div = document.createElement('div');
  div.className = 'message ' + role;

  if (role === 'bot') {
    div.innerHTML = `
      <div class="message-avatar">
        <svg viewBox="0 0 64 64" width="28" height="28">
          <circle cx="32" cy="32" r="30" fill="#134e4a" opacity="0.5"/>
          <path d="M32 50 L32 28" stroke="#2dd4bf" stroke-width="3" stroke-linecap="round"/>
          <path d="M32 36 L44 26" stroke="#2dd4bf" stroke-width="2.2" stroke-linecap="round"/>
          <path d="M32 36 L20 26" stroke="#2dd4bf" stroke-width="2.2" stroke-linecap="round"/>
          <circle cx="44" cy="26" r="4" fill="#5eead4"/>
          <circle cx="20" cy="26" r="4" fill="#5eead4"/>
          <circle cx="32" cy="22" r="5" fill="#2dd4bf"/>
          <circle cx="32" cy="22" r="2" fill="#fff"/>
        </svg>
      </div>
      <div class="message-content">${formatText(text)}</div>
    `;
  } else {
    div.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
  }

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatText(text) {
  return text.split('\n').map(p => `<p>${escapeHtml(p)}</p>`).join('');
}

function generateReply(userText) {
  const t = userText.toLowerCase();

  if (/سلام|درود|هی|hello|hi/.test(t)) {
    return 'سلام! خوشحالم که دوباره پیامتان را دیدم.\nحالتان چطور است؟ چطور می‌توانم کمکتان کنم؟';
  }
  if (/خداحافظ|بای|فعلا|خدا نگهدار/.test(t)) {
    return 'خداحافظ! از گفتگو با شما لذت بردم.\nهر وقت خواستید برگردید، من اینجام. موفق باشید 🌸';
  }
  if (/حالت|چطوری|خوبی|احوال/.test(t)) {
    return 'ممنون که احوال‌پرسی کردید! من همیشه آماده‌ام تا کمکتان کنم.\nشما چطورید؟ اگر سؤالی دارید بفرمایید.';
  }
  if (/درخشا|کیستی|چی هستی|معرفی/.test(t)) {
    return 'من درخشا هستم؛ یک معماری هوش مصنوعی مغز‌محور.\nدانش را به صورت جنگل درخت‌های مفهومی سازمان‌دهی می‌کنم و با جستجوی دوطرفه به سؤالات پاسخ می‌دهم.\nاگر بخواهید می‌توانم بیشتر توضیح دهم.';
  }
  if (/جنگل|درخت|دانش|مفهوم/.test(t)) {
    return 'جنگل دانش درخشا مجموعه‌ای از درخت‌های تخصصی است (مثل فیزیک، زیست‌شناسی، فناوری و ...).\nهر درخت مفاهیم را سلسله‌مراتبی نگه می‌دارد و درخت‌ها از طریق کلیدواژه‌ها به هم متصل می‌شوند.\nبرای افزودن دانش جدید می‌توانید از بخش «ورود دانش» استفاده کنید.';
  }

  return 'سلام! پیام شما را دریافت کردم.\nدر نسخه فعلی، پاسخ‌ها آزمایشی هستند. با گسترش جنگل دانش، پاسخ‌ها دقیق‌تر و مرتبط‌تر خواهند شد.\nاگر سؤال مشخص‌تری دارید یا می‌خواهید سندی اضافه کنید، بفرمایید. از همراهی‌تان سپاسگزاریم.';
}

/* ===== Ingest (Owner Interface) ===== */
let docsCount = 0;
let conceptsCount = 0;

document.getElementById('ingest-form').addEventListener('submit', function (e) {
  e.preventDefault();

  const source = document.getElementById('source-name').value.trim();
  const domain = document.getElementById('domain').value;
  const author = document.getElementById('author').value.trim();
  const content = document.getElementById('content').value.trim();

  if (!source || !content) {
    alert('لطفاً نام منبع و متن سند را وارد کنید.');
    return;
  }

  const wordCount = content.split(/\s+/).filter(Boolean).length;
  const keywords = extractKeywords(content);
  const conceptNum = Math.max(keywords.length, Math.floor(wordCount / 40));

  docsCount += 1;
  conceptsCount += conceptNum;

  document.getElementById('stat-docs').textContent = docsCount;
  document.getElementById('stat-concepts').textContent = conceptsCount;

  const log = document.getElementById('ingest-log');
  if (log.querySelector('.log-empty')) log.innerHTML = '';

  const item = document.createElement('div');
  item.className = 'log-item';
  item.innerHTML = `
    <div class="log-title">✅ ${escapeHtml(source)}</div>
    <div class="log-meta">
      حوزه: ${escapeHtml(domain)}
      ${author ? ' | نویسنده: ' + escapeHtml(author) : ''}
      | ${wordCount} کلمه | حدود ${conceptNum} مفهوم
    </div>
  `;
  log.prepend(item);

  // پاک کردن فرم بعد از موفقیت
  clearIngestForm();
});

function clearIngestForm() {
  document.getElementById('source-name').value = '';
  document.getElementById('author').value = '';
  document.getElementById('content').value = '';
  document.getElementById('domain').selectedIndex = 0;
}

function extractKeywords(text) {
  const candidates = [
    'هوش مصنوعی', 'یادگیری ماشین', 'شبکه عصبی', 'درخت دانش', 'گراف دانش',
    'فیزیک', 'زیست‌شناسی', 'شیمی', 'ریاضی', 'فناوری', 'الگوریتم',
    'داده', 'مدل', 'پردازش', 'زبان', 'مغز', 'حافظه', 'استدلال',
    'مفهوم', 'رابطه', 'جستجو', 'درخت', 'جنگل', 'نورون', 'قشر'
  ];
  const found = [];
  for (const w of candidates) {
    if (text.includes(w)) found.push(w);
  }
  return found;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}

/* Auto-resize chat textarea */
chatInput.addEventListener('input', function () {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 140) + 'px';
});
