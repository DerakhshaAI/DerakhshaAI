# -*- coding: utf-8 -*-
"""درخت دانش درخشا"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Leaf:
    id: str
    text: str
    keywords: List[str] = field(default_factory=list)
    source: str = "core"  # core | user | admin
    confidence_boost: float = 0.0
    use_count: int = 0


@dataclass
class Node:
    id: str
    title: str
    branch: str
    parent_id: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    leaves: List[Leaf] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)  # {target_id, type}
    activation: float = 0.0


@dataclass
class Branch:
    code: str
    name: str
    description: str
    nodes: List[str] = field(default_factory=list)  # node ids


class KnowledgeTree:
    """درخت غول‌پیکر درخشا"""

    def __init__(self):
        self.branches: Dict[str, Branch] = {}
        self.nodes: Dict[str, Node] = {}
        self._init_core()

    def _init_core(self):
        specs = [
            ("SELF", "درباره درخشا", "هویت سامانه و سازندگان"),
            ("ARCH", "معماری دانش", "درخت، مسیر، یادگیری، توجه"),
            ("LANG", "زبان", "ساختار جمله و لحن"),
            ("SCI", "علوم پایه", "زیست، شیمی، فیزیک، ریاضی"),
            ("TECH", "فناوری", "هوش مصنوعی و نرم‌افزار"),
            ("BODY", "بدن و سلامت", "خواب، تغذیه، ورزش"),
            ("MIND", "ذهن و یادگیری", "تمرکز و مهارت"),
            ("SPORT", "ورزش", "رشته‌ها و تمرین"),
            ("CULT", "فرهنگ و ایران", "زبان و تاریخ"),
            ("DOC", "اسناد کاربر", "مقاله، کتاب، سند"),
            ("CHAT", "گفتگو", "تعامل روزمره"),
            ("GEN", "عمومی", "سایر مفاهیم"),
        ]
        for code, name, desc in specs:
            self.branches[code] = Branch(code=code, name=name, description=desc)

        core_qa = [
            ("self_derakhsha", "SELF", "درخشا", ["درخشا"],
             "درخشا یک سامانه هوش مصنوعی فارسی با معماری درخت دانش است که توسط گروک و احمدرضا ایزدی طراحی شده است."),
            ("self_creators", "SELF", "سازندگان", ["گروک", "ایزدی", "سازنده"],
             "درخشا توسط گروک و احمدرضا ایزدی طراحی و توسعه مفهومی یافته است."),
            ("arch_tree", "ARCH", "درخت دانش", ["درخت دانش", "درخت", "جنگل"],
             "درخت دانش ساختار سلسله‌مراتبی با ریشه درخشا است. هر شاخه یک حوزه و هر مفهوم یک گره است."),
            ("arch_lang", "LANG", "قشر زبان", ["قشر زبان", "جمله", "کلیدواژه"],
             "قشر زبان نوع جمله، نقش واژه‌ها، زمان و کلیدواژه را استخراج می‌کند و لحن را تنظیم می‌نماید."),
            ("arch_learn", "ARCH", "یادگیری", ["یادگیری"],
             "یادگیری ورود متن کوتاه یا بلند به درخت با طبقه‌بندی خودکار و پیوند پویا است."),
            ("doc_how", "DOC", "افزودن سند", ["سند", "مقاله", "کتاب"],
             "از بخش دانش، عنوان و متن را وارد کنید تا موتور طبقه‌بندی کند و در گفتگو قابل استفاده شود."),
            ("chat_hi", "CHAT", "سلام", ["سلام"],
             "سلام. سامانه درخشا آماده دریافت پرسش شماست."),
            ("tech_ai", "TECH", "هوش مصنوعی", ["هوش مصنوعی", "هوش", "مصنوعی"],
             "هوش مصنوعی شاخه‌ای از علوم رایانه برای ساخت سامانه‌هایی است که رفتار هوشمندانه نشان می‌دهند."),
            ("body_sleep", "BODY", "خواب", ["خواب"],
             "خواب کافی برای تمرکز، حافظه و سلامت عمومی ضروری است. برنامه خواب منظم توصیه می‌شود."),
        ]
        for nid, branch, title, kws, answer in core_qa:
            leaf = Leaf(id=str(uuid.uuid4())[:8], text=answer, keywords=kws, source="core")
            node = Node(id=nid, title=title, branch=branch, keywords=kws, leaves=[leaf])
            self.nodes[nid] = node
            self.branches[branch].nodes.append(nid)

    def search(self, keywords: List[str], branches: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        kw_set = {k.lower() for k in keywords}
        scored = []
        candidate_branches = set(branches) if branches else set(self.branches.keys())
        # همیشه DOC را هم اگر سند کاربر مهم است در نظر بگیر
        candidate_branches.add("DOC")

        for nid, node in self.nodes.items():
            if node.branch not in candidate_branches and node.branch != "DOC":
                # اگر کلیدواژه مستقیم خورد اجازه بده
                if not any(k.lower() in kw_set for k in node.keywords):
                    continue
            score = 0.0
            for k in node.keywords:
                if k.lower() in kw_set:
                    score += 1.0
            for leaf in node.leaves:
                for k in leaf.keywords:
                    if k.lower() in kw_set:
                        score += 0.8
                # token overlap in text
                for k in kw_set:
                    if k in leaf.text.lower():
                        score += 0.3
                score += leaf.confidence_boost + min(leaf.use_count, 5) * 0.05
            if score > 0:
                scored.append((score, node))

        scored.sort(key=lambda x: -x[0])
        results = []
        for score, node in scored[:limit]:
            leaf = node.leaves[0] if node.leaves else None
            if leaf:
                leaf.use_count += 1
            results.append({
                "node_id": node.id,
                "title": node.title,
                "branch": node.branch,
                "score": round(score, 3),
                "text": leaf.text if leaf else "",
                "source": leaf.source if leaf else "core",
            })
        return results

    def add_document(
        self,
        title: str,
        body: str,
        doc_type: str,
        keywords: List[str],
        branches: List[str],
        source: str = "user",
    ) -> Dict[str, Any]:
        nid = "doc_" + str(uuid.uuid4())[:10]
        # split long text into leaves by paragraphs
        parts = [p.strip() for p in re_split_paragraphs(body) if p.strip()]
        if not parts:
            parts = [body.strip()]
        leaves = []
        for i, part in enumerate(parts[:20]):
            leaves.append(Leaf(
                id=str(uuid.uuid4())[:8],
                text=part[:2000],
                keywords=keywords,
                source=source,
                confidence_boost=0.4,
            ))
        br = branches[0] if branches else "DOC"
        node = Node(
            id=nid,
            title=title,
            branch="DOC",
            keywords=keywords,
            leaves=leaves,
            links=[{"target_id": b, "type": "related-branch"} for b in branches if b != "DOC"],
        )
        self.nodes[nid] = node
        self.branches["DOC"].nodes.append(nid)
        return {"node_id": nid, "title": title, "branches": branches or ["DOC"], "leaves": len(leaves)}

    def to_dict(self) -> Dict:
        return {
            "branches": {c: asdict(b) for c, b in self.branches.items()},
            "nodes": {
                nid: {
                    **{k: v for k, v in asdict(n).items() if k != "leaves"},
                    "leaves": [asdict(l) for l in n.leaves],
                }
                for nid, n in self.nodes.items()
            },
        }

    def save(self, path: str):
        Path(path).write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def re_split_paragraphs(text: str) -> List[str]:
    import re
    return re.split(r"\n\s*\n|\n", text)
