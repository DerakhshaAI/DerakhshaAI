# -*- coding: utf-8 -*-
"""قشر زبان درخشا — تحلیل ساختار جمله فارسی"""
from __future__ import annotations
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set

# نوع جمله
SENTENCE_TYPES = {
    "Q": ("پرسشی", ["آیا", "مگر", "چه", "چی", "کی", "کجا", "چرا", "چطور", "چگونه", "کدام", "چند"]),
    "C": ("امری", ["بگو", "بگوئید", "بنویس", "اضافه کن", "یاد بگیر", "لطفا", "کن", "نکن"]),
    "N": ("منفی", ["نه", "نیست", "نمی", "نمی‌", "بدون", "هیچ"]),
    "W": ("تعجبی", ["عجب", "وه"]),
}

TENSE_MARKERS = {
    "PAST": ["دیروز", "پریروز", "قبلا", "بود", "شد", "رفت", "کرد", "گفت", "آمد", "نوشت"],
    "PRES": ["الان", "اکنون", "می‌", "مي", "است", "هست", "دارد"],
    "FUT": ["فردا", "بعدا", "خواهد", "میخواهد", "می‌خواهد", "قرار است"],
}

FORMAL_TO_COLLOQUIAL = {
    "می‌باشد": "هست", "می باشد": "هست", "می‌گردد": "می‌شه", "می گردد": "می‌شه",
    "می‌شود": "می‌شه", "جهتِ": "برای", "جهت": "برای", "نمود": "کرد",
    "ارائه گردید": "داده شد", "ارائه شد": "داده شد", "نمی‌باشد": "نیست",
    "می‌باشد.": "هست.", "است": "هست",
}
COLLOQUIAL_TO_FORMAL = {v: k for k, v in FORMAL_TO_COLLOQUIAL.items() if v not in ("هست", "است")}
COLLOQUIAL_TO_FORMAL.update({"می‌شه": "می‌شود", "واسه": "برای", "چیه": "چیست", "کیه": "کیست"})

PREPOSITIONS = {"به", "از", "با", "برای", "در", "روی", "زیر", "تا", "را", "که", "و", "یا"}

# طبقه کلیدواژه → شاخه درخت
CLASS_MAP: Dict[str, str] = {
    "درخشا": "SELF", "گروک": "SELF", "ایزدی": "SELF", "سازنده": "SELF",
    "درخت": "ARCH", "جنگل": "ARCH", "معماری": "ARCH", "مسیر": "ARCH",
    "هرس": "ARCH", "قیاس": "ARCH", "توجه": "ARCH", "یادگیری": "ARCH", "گره": "ARCH",
    "جمله": "LANG", "فاعل": "LANG", "فعل": "LANG", "مفعول": "LANG",
    "عامیانه": "LANG", "کتابی": "LANG", "کلیدواژه": "LANG", "قشر": "LANG",
    "سلول": "SCI", "شیمی": "SCI", "فیزیک": "SCI", "زیست": "SCI", "dna": "SCI",
    "مولکول": "SCI", "ریاضی": "SCI",
    "هوش": "TECH", "مصنوعی": "TECH", "الگوریتم": "TECH", "داده": "TECH",
    "شبکه": "TECH", "برنامه": "TECH", "فناوری": "TECH", "پایتون": "TECH", "مدل": "TECH",
    "خواب": "BODY", "تغذیه": "BODY", "سلامت": "BODY", "ورزش": "BODY", "استرس": "BODY",
    "تمرکز": "MIND", "حافظه": "MIND", "عادت": "MIND", "خلاقیت": "MIND",
    "فوتبال": "SPORT", "تمرین": "SPORT", "استقامت": "SPORT",
    "فارسی": "CULT", "ایران": "CULT", "تهران": "CULT", "نوروز": "CULT", "ادبیات": "CULT",
    "مقاله": "DOC", "کتاب": "DOC", "سند": "DOC", "یادداشت": "DOC", "متن": "DOC",
    "سلام": "CHAT", "خداحافظ": "CHAT", "ممنون": "CHAT", "متشکرم": "CHAT",
}


@dataclass
class Keyword:
    term: str
    class_id: str


@dataclass
class LanguageResult:
    text: str
    sentence_type: str
    tense: str
    style: str  # formal | colloquial | mixed
    tokens: List[str]
    keywords: List[Keyword] = field(default_factory=list)
    target_branches: List[str] = field(default_factory=list)
    roles: Dict[str, str] = field(default_factory=dict)
    nature: str = "TELL"  # ASK REQ TELL CONT FIX NEW

    def to_dict(self):
        d = asdict(self)
        return d


class LanguageCortex:
    """قشر زبان — ورودی متن، خروجی ساختار و کلیدواژه"""

    def analyze(self, text: str, previous_keywords: Optional[Set[str]] = None) -> LanguageResult:
        text = (text or "").strip()
        tokens = self._tokenize(text)
        stype = self._sentence_type(text, tokens)
        tense = self._tense(text, tokens)
        style = self._style(text)
        keywords = self._keywords(text, tokens)
        branches = sorted({k.class_id for k in keywords}) or ["CHAT"]
        roles = self._roles(tokens)
        nature = self._nature(stype, text, previous_keywords, {k.term for k in keywords})
        return LanguageResult(
            text=text,
            sentence_type=stype,
            tense=tense,
            style=style,
            tokens=tokens,
            keywords=keywords,
            target_branches=branches,
            roles=roles,
            nature=nature,
        )

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"[\w\u0600-\u06FF]+", text)

    def _sentence_type(self, text: str, tokens: List[str]) -> str:
        if "?" in text or "؟" in text:
            return "Q"
        low = text.lower()
        for code, (_, markers) in SENTENCE_TYPES.items():
            if any(m in low or m in tokens for m in markers):
                return code
        return "S"

    def _tense(self, text: str, tokens: List[str]) -> str:
        low = text.lower()
        for code, markers in TENSE_MARKERS.items():
            if any(m in low or m in tokens for m in markers):
                return code
        return "UNK"

    def _style(self, text: str) -> str:
        formal_hits = sum(1 for k in FORMAL_TO_COLLOQUIAL if k in text)
        colloq_hits = sum(1 for k in COLLOQUIAL_TO_FORMAL if k in text)
        if formal_hits > colloq_hits and formal_hits > 0:
            return "formal"
        if colloq_hits > 0:
            return "colloquial"
        return "mixed"

    def _keywords(self, text: str, tokens: List[str]) -> List[Keyword]:
        found: List[Keyword] = []
        low = text.lower()
        seen = set()
        # multi-word / map keys first
        for term, cls in sorted(CLASS_MAP.items(), key=lambda x: -len(x[0])):
            if term.lower() in low and term not in seen:
                found.append(Keyword(term=term, class_id=cls))
                seen.add(term)
        for t in tokens:
            if t in PREPOSITIONS or len(t) < 2:
                continue
            if t in CLASS_MAP and t not in seen:
                found.append(Keyword(term=t, class_id=CLASS_MAP[t]))
                seen.add(t)
        return found

    def _roles(self, tokens: List[str]) -> Dict[str, str]:
        roles: Dict[str, str] = {}
        if not tokens:
            return roles
        # heuristic: first content token ~ subject, last verb-like ~ verb
        content = [t for t in tokens if t not in PREPOSITIONS]
        if content:
            roles["subject_guess"] = content[0]
            roles["focus"] = content[-1]
        for t in tokens:
            if t.endswith("د") or t.startswith("می") or t.startswith("می‌"):
                roles["verb_guess"] = t
                break
        return roles

    def _nature(self, stype: str, text: str, prev: Optional[Set[str]], current: Set[str]) -> str:
        if stype == "Q":
            return "ASK"
        if stype == "C":
            return "REQ"
        if any(x in text for x in ["نه", "منظورم", "اشتباه"]):
            return "FIX"
        if prev and current & prev:
            return "CONT"
        if prev and not (current & prev) and current:
            return "NEW"
        return "TELL"

    def convert_style(self, text: str, target: str) -> str:
        out = text
        mapping = FORMAL_TO_COLLOQUIAL if target == "colloquial" else COLLOQUIAL_TO_FORMAL
        for a, b in mapping.items():
            out = out.replace(a, b)
        return out
