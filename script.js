/* ===== Navigation ===== */
function showView(name) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  const view = document.getElementById('view-' + name);
  if (view) view.classList.add('active');
  const btn = document.querySelector('.nav-btn[data-view="' + name + '"]');
  if (btn) btn.classList.add('active');
}

/* ===== Chat ===== */
const chatBox = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');

function onChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); }
}

function sendChat() {
  const text = chatInput.value.trim();
  if (!text) return;
  addMsg('user', text);
  chatInput.value = '';
  chatInput.style.height = 'auto';
  setTimeout(() => addMsg('bot', reply(text)), 500 + Math.random() * 500);
}

function addMsg(role, text) {
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  if (role === 'bot') {
    div.innerHTML = `<div class="msg-avatar"><svg viewBox="0 0 64 64" width="26" height="26"><circle cx="32" cy="32" r="28" fill="#134e4a" opacity="0.5"/><path d="M32 48 L32 28" stroke="#2dd4bf" stroke-width="3" stroke-linecap="round"/><path d="M32 34 L43 25" stroke="#2dd4bf" stroke-width="2.2" stroke-linecap="round"/><path d="M32 34 L21 25" stroke="#2dd4bf" stroke-width="2.2" stroke-linecap="round"/><circle cx="43" cy="25" r="3.8" fill="#5eead4"/><circle cx="21" cy="25" r="3.8" fill="#5eead4"/><circle cx="32" cy="22" r="4.8" fill="#2dd4bf"/><circle cx="32" cy="22" r="1.8" fill="#fff"/></svg></div><div class="msg-body">${fmt(text)}</div>`;
  } else {
    div.innerHTML = `<div class="msg-body">${esc(text)}</div>`;
  }
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function fmt(t) { return t.split('\n').map(p => '<p>' + esc(p) + '</p>').join(''); }
function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

function reply(q) {
  const t = q.toLowerCase();

  // Greetings
  if (/^(سلام|درود|هی|hello|hi|صبح بخیر|عصر بخیر|شب بخیر)/.test(t) || /سلام\s/.test(t))
    return 'سلام! خوشحالم که پیامتان را دیدم.\nحالتان چطور است؟ من درخشا هستم و آماده‌ام دربارهٔ معماری، جنگل دانش، جستجوی دوطرفه یا هر موضوع دیگری کمکتان کنم.';

  if (/خداحافظ|بای|فعلا|خدا نگهدار|خداحافظی/.test(t))
    return 'خداحافظ! از گفتگو با شما لذت بردم.\nهر وقت برگشتید، جنگل دانش آماده‌تر خواهد بود. موفق و سربلند باشید 🌸';

  if (/حالت|چطوری|خوبی|احوال|چطورید/.test(t))
    return 'ممنون از احوال‌پرسی‌تان! من همیشه آماده‌ام.\nشما چطورید؟ اگر سؤالی دربارهٔ درخشا یا مفاهیم دانش دارید بفرمایید.';

  // Core architecture
  if (/درخشا چیست|کیستی|چی هستی|معرفی|درباره درخشا|دربارهٔ درخشا/.test(t))
    return 'من درخشا هستم؛ یک معماری هوش مصنوعی ماژولار و مغز‌محور.\nدانش را با جنگل درخت‌های مفهومی سازمان‌دهی می‌کنم و با جستجوی دوطرفه (جزء→کل و کل→جزء) به سؤالات پاسخ می‌دهم.\nقشرهای اصلی من شامل Input Cortex، Language Tree، Forest Builder، Reasoning، Memory و Tree-Neuron هستند.';

  if (/معماری|قشر|cortex|ماژول/.test(t))
    return 'معماری درخشا ماژولار و الهام‌گرفته از مغز است.\nهر قشر وظیفهٔ مستقلی دارد:\n• Input Cortex: دریافت و پاکسازی\n• Language Tree Cortex: ساختار جمله و عبارات مرکب\n• Forest Builder: ساخت دانش از اسناد\n• Reasoning & Conflict Resolution: استدلال و مدیریت تعارض\n• Memory: حافظه کوتاه‌مدت و بلندمدت\n• Response Generation: تولید پاسخ نهایی';

  if (/جنگل دانش|دانش|درخت مفهوم|درخت‌های/.test(t))
    return 'جنگل دانش مجموعه‌ای از درخت‌های تخصصی است؛ مثل فیزیک، زیست‌شناسی، فناوری، شیمی، ریاضی و اطلاعات عمومی.\nهر درخت مفاهیم را سلسله‌مراتبی نگه می‌دارد و درخت‌ها از طریق کلیدواژه‌ها و ریشه‌ها به هم متصل می‌شوند.\nبرای افزودن دانش جدید از بخش «ورود دانش» استفاده کنید.';

  if (/جستجوی هرمی|جزء به کل|جزء→کل|hierarchical/.test(t))
    return 'جستجوی هرمی (جزء → کل) از یک مفهوم جزئی شروع می‌کند و به سمت ریشه و حوزهٔ اصلی حرکت می‌کند.\nمثلاً از «انسان» به «پستاندار ← جانور ← موجود زنده» می‌رسد و زمینه را مشخص می‌کند.';

  if (/جستجوی درختی|کل به جزء|کل→جزء|tree search/.test(t))
    return 'جستجوی درختی (کل → جزء) از ریشه یا یک گره میانی شروع می‌کند و به سمت برگ‌ها و جزئیات پایین می‌رود.\nاین جستجو برای یافتن زیرمفاهیم و جزئیات یک موضوع استفاده می‌شود.';

  if (/جستجوی دوطرفه|دوطرفه|bidirectional/.test(t))
    return 'جستجوی دوطرفه ترکیب جستجوی هرمی و درختی است.\nبا حرکت جزء→کل زمینه را پیدا می‌کنم و با حرکت کل→جزء جزئیات را استخراج می‌کنم.\nاین یکی از نقاط قوت اصلی معماری درخشاست.';

  if (/tree.?neuron|نرون درختی|درخت نرون/.test(t))
    return 'Tree-Neuron ایده‌ای است که هر درخت دانش را به عنوان یک واحد پردازشی مستقل در نظر می‌گیرد.\nاین نرون‌ها می‌توانند موازی فعال شوند و خروجی‌شان (مسیر، معنی محلی و سطح اعتماد) در لایهٔ بالاتر ترکیب می‌شود.';

  if (/تشکیل معنی|معنی|معنا/.test(t))
    return 'تشکیل معنی از ترکیب ساختار جمله (فاعل، فعل، مفعول)، کلیدواژه‌ها، مسیرهای طی‌شده در درخت‌ها و روابط بین‌درختی ساخته می‌شود.\nسپس Reasoning Cortex مسیر را اعتبارسنجی می‌کند و سطح اطمینان را مشخص می‌نماید.';

  if (/استدلال|اعتبارسنجی|تعارض|conflict/.test(t))
    return 'پس از تشکیل معنی، سیستم مسیرهای مختلف را مقایسه می‌کند.\nاگر تعارضی بین درخت‌ها یا منابع باشد، Conflict Resolution Cortex بهترین مسیر را انتخاب یا سؤال روشن‌کننده می‌پرسد.\nامتیاز اعتماد بر اساس عمق مسیر، وزن و تطابق با ساختار جمله محاسبه می‌شود.';

  if (/حافظه|memory|یادگیری|تجربه/.test(t))
    return 'درخشا دو نوع حافظه دارد:\n• Working Memory: مفاهیم فعال در مکالمه جاری\n• Episodic Memory: تجربیات موفق و ناموفق قبلی\nیادگیری از تجربه با تقویت یا تضعیف وزن مسیرها و اتصالات بر اساس بازخورد انجام می‌شود.';

  if (/forest builder|ساخت دانش|ورود سند|اسناد/.test(t))
    return 'Forest Builder Cortex متون، مقالات و کتاب‌ها را دریافت می‌کند، مفاهیم و روابط را استخراج می‌کند و آن‌ها را در درخت مناسب قرار می‌دهد یا درخت جدید می‌سازد.\nاز بخش «ورود دانش» می‌توانید اسناد را اضافه کنید.';

  if (/کلیدواژه|جمله|فاعل|مفعول|language tree/.test(t))
    return 'Language Tree Cortex ساختار هر جمله را از نظر کلیدواژه، فاعل، مفعول و فعل مشخص می‌کند.\nدر بخش «جملات و کلیدواژه» می‌توانید جملات ساخت‌یافته را با نقش‌های دستوری ثبت کنید تا در جنگل دانش ذخیره شوند.';

  if (/مانیتورینگ|رنگ|رنگی/.test(t))
    return 'مانیتورینگ رنگی برای نمایش مسیر پردازش و فعالیت هر قشر و هر درخت استفاده می‌شود.\nهر حوزه و زیرمجموعه رنگ مشخصی دارد تا مسیر استدلال قابل‌ردیابی باشد.';

  if (/نسخه|اول|قابلیت|چی کار/.test(t))
    return 'نسخهٔ اول درخشا شامل این قابلیت‌هاست:\n• گفتگوی مفهومی بر اساس معماری\n• ورود اسناد به جنگل دانش\n• ثبت جملات با کلیدواژه و نقش دستوری\n• جستجوی دوطرفه، Tree-Neuron، حافظه و مدیریت تعارض (در سطح طراحی)\nدر نسخه‌های بعدی پردازش واقعی و یادگیری عمیق‌تر اضافه خواهد شد.';

  // Fallback
  return 'سلام! پیام شما را دریافت کردم.\nمن در نسخهٔ اول بر اساس معماری طراحی‌شده پاسخ می‌دهم. می‌توانید دربارهٔ جنگل دانش، جستجوی هرمی و درختی، Tree-Neuron، قشرها، تشکیل معنی یا ورود اسناد بپرسید.\nاز همراهی‌تان سپاسگزاریم.';
}

chatInput.addEventListener('input', function () {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 130) + 'px';
});

/* ===== Knowledge Ingest ===== */
let docs = 0, concepts = 0;
document.getElementById('form-knowledge').addEventListener('submit', function (e) {
  e.preventDefault();
  const source = document.getElementById('k-source').value.trim();
  const domain = document.getElementById('k-domain').value;
  const author = document.getElementById('k-author').value.trim();
  const content = document.getElementById('k-content').value.trim();
  if (!source || !content) return;

  const words = content.split(/\s+/).filter(Boolean).length;
  const cNum = Math.max(3, Math.floor(words / 35));
  docs++; concepts += cNum;
  document.getElementById('s-docs').textContent = docs;
  document.getElementById('s-concepts').textContent = concepts;

  const log = document.getElementById('k-log');
  if (log.querySelector('.log-empty')) log.innerHTML = '';
  const item = document.createElement('div');
  item.className = 'log-item';
  item.innerHTML = `<div class="t">✅ ${esc(source)}</div><div class="m">حوزه: ${esc(domain)}${author ? ' | ' + esc(author) : ''} | ${words} کلمه | ≈${cNum} مفهوم</div>`;
  log.prepend(item);
  resetKnowledgeForm();
});

function resetKnowledgeForm() {
  document.getElementById('k-source').value = '';
  document.getElementById('k-author').value = '';
  document.getElementById('k-content').value = '';
  document.getElementById('k-domain').selectedIndex = 0;
}

/* ===== Keywords / Sentences ===== */
let sentCount = 0, keyCount = 0;
document.getElementById('form-keywords').addEventListener('submit', function (e) {
  e.preventDefault();
  const sentence = document.getElementById('kw-sentence').value.trim();
  const keys = document.getElementById('kw-keys').value.trim();
  const domain = document.getElementById('kw-domain').value;
  const subject = document.getElementById('kw-subject').value.trim();
  const verb = document.getElementById('kw-verb').value.trim();
  const object = document.getElementById('kw-object').value.trim();
  const relation = document.getElementById('kw-relation').value;
  if (!sentence || !keys) return;

  const keyArr = keys.split(/[,،]/).map(k => k.trim()).filter(Boolean);
  sentCount++;
  keyCount += keyArr.length;
  document.getElementById('s-sentences').textContent = sentCount;
  document.getElementById('s-keywords').textContent = keyCount;

  const list = document.getElementById('kw-list');
  if (list.querySelector('.log-empty')) list.innerHTML = '';
  const item = document.createElement('div');
  item.className = 'log-item';
  let structure = '';
  if (subject || verb || object) structure = ` | ${subject || '—'} / ${verb || '—'} / ${object || '—'}`;
  item.innerHTML = `<div class="t">📝 ${esc(sentence)}</div><div class="m">کلیدواژه: ${esc(keyArr.join('، '))} | حوزه: ${esc(domain)} | رابطه: ${esc(relation)}${esc(structure)}</div>`;
  list.prepend(item);
  resetKeywordForm();
});

function resetKeywordForm() {
  ['kw-sentence','kw-keys','kw-subject','kw-verb','kw-object'].forEach(id => document.getElementById(id).value = '');
  document.getElementById('kw-domain').selectedIndex = 0;
  document.getElementById('kw-relation').selectedIndex = 0;
}
