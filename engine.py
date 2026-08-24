from dataclasses import dataclass, asdict
import re

@dataclass
class Token:
    text: str
    kind: str = 'unknown'
    role: str = 'unknown'

class Node:
    def __init__(self, name, keywords=(), data=None):
        self.name = name
        self.keywords = set(keywords)
        self.data = data or {}
        self.children = []

    def add(self, child):
        self.children.append(child)
        return child

class KnowledgeTree:
    def __init__(self):
        self.root = Node('دانش')
        self.build()

    def build(self):
        science = self.root.add(Node('علوم', ['علم','علوم']))
        physics = science.add(Node('فیزیک', ['فیزیک','دما','انرژی','نور']))
        physics.add(Node('تغییر حالت ماده', ['ماده','انجماد','یخ','ذوب'], {
            'answer': 'تغییر حالت ماده یعنی تبدیل ماده از یک حالت به حالت دیگر؛ مانند تبدیل آب مایع به یخ جامد.'}))
        biology = science.add(Node('زیست‌شناسی', ['زیست','گیاه','جانور','سلول']))
        biology.add(Node('گیاهان', ['گیاه','گیاهان','رشد','نور'], {
            'answer': 'گیاهان برای رشد به نور نیاز دارند، چون نور انرژی لازم برای فتوسنتز را فراهم می‌کند.'}))
        tech = self.root.add(Node('فناوری', ['فناوری','تکنولوژی']))
        tech.add(Node('هوش مصنوعی', ['هوش','مصنوعی','AI']))
        tech.add(Node('برنامه‌نویسی', ['برنامه','کدنویسی','پایتون','پایتون']))
        language = self.root.add(Node('زبان', ['زبان','فارسی','دستور']))
        language.add(Node('دستور زبان فارسی', ['فاعل','مفعول','فعل','صفت','قید']))

    def flatten(self):
        result = []
        def walk(node, path):
            p = path + [node.name]
            result.append((node, p))
            for child in node.children:
                walk(child, p)
        walk(self.root, [])
        return result

    def search(self, keywords):
        hits = []
        for node, path in self.flatten():
            matched = [k for k in keywords if k in (node.name + ' ' + ' '.join(node.keywords))]
            if matched:
                # Simple transparent scoring: keyword coverage + depth/context bonus.
                coverage = len(set(matched)) / max(1, len(set(keywords)))
                depth_bonus = min(len(path) * 0.03, 0.15)
                score = min(1.0, coverage + depth_bonus)
                hits.append((score, node, path, matched))
        return sorted(hits, key=lambda x: x[0], reverse=True)

    def json_node(self, node):
        return {'name': node.name, 'keywords': sorted(node.keywords), 'children': [self.json_node(c) for c in node.children]}

    def tree_json(self):
        return self.json_node(self.root)

class PersianAnalyzer:
    stop = {'و','در','به','از','با','برای','که','را','این','آن','یک','است','هست','می','شود','شد','چه','چرا','چگونه'}
    verbs = {'است','هست','بود','شد','شدند','رفت','رفتند','خواند','خواندند','خورد','خوردند','می‌رود','می‌خواند','می‌خورد'}

    def normalize(self, text):
        text = text.replace('ي','ی').replace('ك','ک').replace('\u200c',' ')
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def analyze(self, text):
        text = self.normalize(text)
        words = re.findall(r'[آ-یA-Za-z0-9]+', text)
        tokens = []
        for w in words:
            if w == 'را': kind, role = 'نشانه', 'مفعول'
            elif w in {'در','به','از','با','برای'}: kind, role = 'حرف اضافه', 'متمم'
            elif w in self.verbs or w.endswith(('ند','د')) and len(w) > 3: kind, role = 'فعل', 'فعل'
            elif w in {'چرا','چگونه','کجا','کی','چه'}: kind, role = 'پرسشی', 'واژه پرسشی'
            else: kind, role = 'واژه', 'نامشخص'
            tokens.append(Token(w, kind, role))
        keywords = [w for w in words if w not in self.stop and len(w) > 1]
        return {'tokens':[asdict(t) for t in tokens], 'keywords':keywords, 'question':'?' in text or any(t.role == 'واژه پرسشی' for t in tokens)}

class SentenceGenerator:
    def generate(self, text, style):
        if style == 'colloquial':
            return text.replace('می‌باشد','هست').replace('است','هست')
        return text

class DerakhshaEngine:
    def __init__(self):
        self.analyzer = PersianAnalyzer()
        self.tree = KnowledgeTree()
        self.generator = SentenceGenerator()

    def answer(self, text, style='formal'):
        parsed = self.analyzer.analyze(text)
        hits = self.tree.search(parsed['keywords'])
        if hits and hits[0][1].data.get('answer'):
            score, node, path, matched = hits[0]
            answer = self.generator.generate(node.data['answer'], style)
        elif hits:
            score, node, path, matched = hits[0]
            answer = f'درخشا موضوع را در شاخه «{node.name}» پیدا کرد، اما این برگ هنوز پاسخ کامل ندارد.'
        else:
            score, path, matched, answer = 0, [], [], 'در نسخه آزمایشی فعلی، برگ دانش مناسبی برای این پرسش پیدا نشد.'
        return {
            'answer': answer,
            'confidence': round(score * 100, 1),
            'keywords': parsed['keywords'],
            'tokens': parsed['tokens'],
            'knowledge_path': path,
            'search_mode': 'hybrid top-down / bottom-up'
        }
