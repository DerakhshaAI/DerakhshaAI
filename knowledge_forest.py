#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
موتور جنگل دانش درخشا (Derakhsha Knowledge Forest Engine)
طراحی‌شده توسط گروک و احمدرضا ایزدی

قابلیت‌ها:
- جنگل دانش: هر حوزه یک درخت، هر مفهوم یک گره
- قشر زمانی: روابط زمانی و روندها
- استدلال احتمالاتی: چند مسیر موازی + Confidence Score
- هرس و پیوند پویا: حذف مسیر کم‌استفاده، افزودن موقت از کاربر
- قشر فراشناخت: تنظیم عمق تفکر بر اساس پیچیدگی سؤال
- استدلال قیاسی: یافتن الگوهای مشابه بین حوزه‌ها
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import json
import math
import re
from collections import defaultdict
from pathlib import Path


@dataclass
class Relation:
    """رابطه بین دو مفهوم با بُعد زمانی و وزن"""
    target_id: str
    relation_type: str          # is-a, part-of, causes, similar-to, precedes, ...
    weight: float = 1.0
    temporal: Optional[str] = None   # before, after, during, trend:increasing, ...
    confidence: float = 0.8
    last_used: Optional[str] = None
    use_count: int = 0


@dataclass
class ConceptNode:
    """یک گره (مفهوم) در درخت دانش"""
    id: str
    title: str
    domain: str
    description: str = ""
    qa: List[Dict[str, str]] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    activation: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_temporary: bool = False


@dataclass
class ReasoningPath:
    """یک مسیر استدلال با امتیاز اطمینان"""
    nodes: List[str]
    score: float
    path_type: str          # direct, analogical, temporal, probabilistic
    explanation: str = ""


class KnowledgeForest:
    """
    جنگل دانش درخشا
    هر حوزه علمی یک درخت است؛ کل سیستم یک جنگل.
    """

    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.domains: Dict[str, List[str]] = defaultdict(list)
        self.activation_history: List[Tuple[str, float]] = []
        self.prune_threshold = 0.05
        self.temp_ttl_hours = 72

    # ─── ساخت جنگل ───────────────────────────────────────────
    def add_concept(self, node: ConceptNode) -> None:
        self.nodes[node.id] = node
        if node.id not in self.domains[node.domain]:
            self.domains[node.domain].append(node.id)

    def link(self, source_id: str, target_id: str, relation_type: str,
             weight: float = 1.0, temporal: str = None, confidence: float = 0.8) -> None:
        if source_id not in self.nodes or target_id not in self.nodes:
            return
        rel = Relation(target_id, relation_type, weight, temporal, confidence)
        self.nodes[source_id].relations.append(rel)

    # ─── فعال‌سازی نورونی ────────────────────────────────────
    def activate(self, node_id: str, strength: float = 1.0) -> None:
        if node_id not in self.nodes:
            return
        node = self.nodes[node_id]
        node.activation = min(1.0, node.activation + strength)
        self.activation_history.append((node_id, node.activation))
        # انتشار به همسایه‌ها (مثل فعال‌سازی نورون)
        for rel in node.relations:
            spread = strength * rel.weight * rel.confidence * 0.6
            if spread > 0.05:
                target = self.nodes.get(rel.target_id)
                if target:
                    target.activation = min(1.0, target.activation + spread)
                    rel.use_count += 1
                    rel.last_used = datetime.utcnow().isoformat()

    def decay_activations(self, factor: float = 0.85) -> None:
        for node in self.nodes.values():
            node.activation *= factor

    # ─── قشر فراشناخت: تخمین عمق مورد نیاز ──────────────────
    def metacognitive_depth(self, query: str) -> str:
        """تصمیم می‌گیرد تفکر سطحی، متوسط یا عمیق لازم است"""
        q = query.strip()
        words = len(q.split())
        complex_markers = ["چرا", "چگونه", "مقایسه", "تفاوت", "رابطه", "پیش‌بینی",
                           "تحلیل", "علت", "نتیجه", "اگر", "فرض", "روند"]
        score = words * 0.3
        score += sum(1.5 for m in complex_markers if m in q)
        if score < 2.5:
            return "shallow"
        if score < 6:
            return "medium"
        return "deep"

    # ─── استدلال احتمالاتی: چند مسیر موازی ───────────────────
    def probabilistic_paths(self, start_ids: List[str], max_depth: int = 3) -> List[ReasoningPath]:
        paths: List[ReasoningPath] = []

        def dfs(current: str, trail: List[str], score: float, depth: int):
            if depth > max_depth or score < 0.1:
                if len(trail) > 1:
                    paths.append(ReasoningPath(
                        nodes=trail.copy(),
                        score=round(score, 3),
                        path_type="probabilistic",
                        explanation=" → ".join(trail)
                    ))
                return
            node = self.nodes.get(current)
            if not node:
                return
            for rel in node.relations:
                if rel.target_id in trail:
                    continue
                new_score = score * rel.weight * rel.confidence
                trail.append(rel.target_id)
                dfs(rel.target_id, trail, new_score, depth + 1)
                trail.pop()
            if len(trail) > 1:
                paths.append(ReasoningPath(
                    nodes=trail.copy(),
                    score=round(score, 3),
                    path_type="probabilistic",
                    explanation=" → ".join(trail)
                ))

        for sid in start_ids:
            dfs(sid, [sid], 1.0, 0)

        # مرتب‌سازی بر اساس Confidence Score
        paths.sort(key=lambda p: p.score, reverse=True)
        return paths[:8]

    # ─── استدلال قیاسی: یافتن الگوهای مشابه بین حوزه‌ها ───────
    def analogical_reason(self, concept_id: str, top_k: int = 3) -> List[ReasoningPath]:
        if concept_id not in self.nodes:
            return []
        source = self.nodes[concept_id]
        source_rel_types = {r.relation_type for r in source.relations}
        candidates = []

        for nid, node in self.nodes.items():
            if node.domain == source.domain or nid == concept_id:
                continue
            target_rel_types = {r.relation_type for r in node.relations}
            overlap = len(source_rel_types & target_rel_types)
            if overlap == 0:
                continue
            # شباهت ساختاری ساده
            sim = overlap / max(len(source_rel_types | target_rel_types), 1)
            # شباهت متنی عنوان
            title_sim = self._text_similarity(source.title, node.title)
            total = 0.6 * sim + 0.4 * title_sim
            if total > 0.15:
                candidates.append(ReasoningPath(
                    nodes=[concept_id, nid],
                    score=round(total, 3),
                    path_type="analogical",
                    explanation=f"قیاس: «{source.title}» ≈ «{node.title}» (حوزه: {node.domain})"
                ))

        candidates.sort(key=lambda p: p.score, reverse=True)
        return candidates[:top_k]

    # ─── قشر زمانی: تحلیل روند ───────────────────────────────
    def temporal_analysis(self, concept_id: str) -> List[str]:
        if concept_id not in self.nodes:
            return []
        insights = []
        node = self.nodes[concept_id]
        for rel in node.relations:
            if rel.temporal:
                target_title = self.nodes.get(rel.target_id, ConceptNode("", "؟", "")).title
                insights.append(
                    f"رابطه زمانی [{rel.temporal}]: {node.title} → {target_title} "
                    f"(اطمینان: {rel.confidence:.0%})"
                )
        return insights

    # ─── هرس پویا ────────────────────────────────────────────
    def prune(self) -> int:
        """حذف روابط کم‌استفاده و گره‌های موقت منقضی"""
        removed = 0
        now = datetime.utcnow()
        for node in list(self.nodes.values()):
            # هرس روابط
            kept = []
            for rel in node.relations:
                if rel.use_count == 0 and rel.confidence < self.prune_threshold:
                    removed += 1
                    continue
                kept.append(rel)
            node.relations = kept
            # حذف گره‌های موقت قدیمی
            if node.is_temporary:
                created = datetime.fromisoformat(node.created_at)
                hours = (now - created).total_seconds() / 3600
                if hours > self.temp_ttl_hours and node.activation < 0.1:
                    del self.nodes[node.id]
                    if node.id in self.domains[node.domain]:
                        self.domains[node.domain].remove(node.id)
                    removed += 1
        return removed

    # ─── پیوند پویا از ورودی کاربر ───────────────────────────
    def dynamic_link_from_user(self, question: str, answer: str, domain: str = "کاربر") -> str:
        nid = "user_" + re.sub(r"\W+", "_", question[:40].lower())
        node = ConceptNode(
            id=nid,
            title=question[:80],
            domain=domain,
            description=answer[:300],
            qa=[{"q": question, "a": answer}],
            is_temporary=True
        )
        self.add_concept(node)
        # تلاش برای پیوند به نزدیک‌ترین مفاهیم موجود
        best_id, best_sim = None, 0.0
        for existing in self.nodes.values():
            if existing.id == nid:
                continue
            sim = self._text_similarity(question, existing.title + " " + existing.description)
            if sim > best_sim:
                best_sim, best_id = sim, existing.id
        if best_id and best_sim > 0.2:
            self.link(nid, best_id, "related-to", weight=best_sim, confidence=0.6)
            self.link(best_id, nid, "related-to", weight=best_sim, confidence=0.6)
        return nid

    # ─── موتور پاسخ اصلی ─────────────────────────────────────
    def reason(self, query: str) -> Dict[str, Any]:
        depth = self.metacognitive_depth(query)
        max_d = {"shallow": 1, "medium": 2, "deep": 3}[depth]

        # یافتن گره‌های مرتبط با پرسش
        scored = []
        for nid, node in self.nodes.items():
            text = (node.title + " " + node.description + " " +
                    " ".join(qa["q"] + " " + qa["a"] for qa in node.qa))
            sim = self._text_similarity(query, text)
            if sim > 0.08:
                scored.append((nid, sim))
        scored.sort(key=lambda x: x[1], reverse=True)
        top_ids = [nid for nid, _ in scored[:5]]

        for nid, sim in scored[:5]:
            self.activate(nid, sim)

        paths = self.probabilistic_paths(top_ids, max_depth=max_d) if top_ids else []
        analogies = []
        if depth in ("medium", "deep") and top_ids:
            for tid in top_ids[:2]:
                analogies.extend(self.analogical_reason(tid))

        temporal = []
        if depth == "deep" and top_ids:
            for tid in top_ids[:2]:
                temporal.extend(self.temporal_analysis(tid))

        # بهترین پاسخ مستقیم از QA
        best_answer = None
        best_conf = 0.0
        for nid, sim in scored[:8]:
            node = self.nodes[nid]
            for qa in node.qa:
                qsim = self._text_similarity(query, qa["q"])
                if qsim > best_conf:
                    best_conf = qsim
                    best_answer = qa["a"]

        return {
            "query": query,
            "metacognitive_depth": depth,
            "confidence": round(best_conf, 3) if best_answer else (paths[0].score if paths else 0.0),
            "answer": best_answer or self._compose_from_paths(paths, analogies),
            "activated_concepts": [
                {"id": nid, "title": self.nodes[nid].title, "activation": round(self.nodes[nid].activation, 3)}
                for nid in top_ids if nid in self.nodes
            ],
            "reasoning_paths": [
                {"nodes": p.nodes, "score": p.score, "type": p.path_type, "explanation": p.explanation}
                for p in paths[:5]
            ],
            "analogies": [
                {"explanation": a.explanation, "score": a.score}
                for a in analogies[:3]
            ],
            "temporal_insights": temporal[:4],
        }

    def _compose_from_paths(self, paths: List[ReasoningPath], analogies: List[ReasoningPath]) -> str:
        if not paths and not analogies:
            return ("هنوز مسیر استدلال قوی‌ای در جنگل دانش برای این پرسش فعال نشده. "
                    "می‌توانید این موضوع را به دانش‌نامه اضافه کنید تا پیوند پویا برقرار شود.")
        parts = []
        if paths:
            best = paths[0]
            titles = [self.nodes[n].title for n in best.nodes if n in self.nodes]
            parts.append(f"مسیر برتر (اطمینان {best.score:.0%}): " + " ← ".join(titles))
        if analogies:
            parts.append("قیاس‌های یافت‌شده: " + " | ".join(a.explanation for a in analogies[:2]))
        return "\n".join(parts)

    @staticmethod
    def _text_similarity(a: str, b: str) -> float:
        """شباهت ساده مبتنی بر توکن (بدون وابستگی خارجی)"""
        def tokens(s: str):
            return set(re.findall(r"[\w\u0600-\u06FF]+", s.lower()))
        ta, tb = tokens(a), tokens(b)
        if not ta or not tb:
            return 0.0
        inter = len(ta & tb)
        return inter / math.sqrt(len(ta) * len(tb))

    # ─── ذخیره / بارگذاری ────────────────────────────────────
    def to_dict(self) -> Dict:
        return {
            "nodes": {
                nid: {
                    "id": n.id,
                    "title": n.title,
                    "domain": n.domain,
                    "description": n.description,
                    "qa": n.qa,
                    "relations": [
                        {
                            "target_id": r.target_id,
                            "relation_type": r.relation_type,
                            "weight": r.weight,
                            "temporal": r.temporal,
                            "confidence": r.confidence,
                            "use_count": r.use_count,
                        }
                        for r in n.relations
                    ],
                    "is_temporary": n.is_temporary,
                    "created_at": n.created_at,
                }
                for nid, n in self.nodes.items()
            }
        }

    def save(self, path: str) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str) -> "KnowledgeForest":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        forest = cls()
        for nid, nd in data.get("nodes", {}).items():
            node = ConceptNode(
                id=nd["id"],
                title=nd["title"],
                domain=nd["domain"],
                description=nd.get("description", ""),
                qa=nd.get("qa", []),
                is_temporary=nd.get("is_temporary", False),
                created_at=nd.get("created_at", datetime.utcnow().isoformat()),
            )
            for rd in nd.get("relations", []):
                node.relations.append(Relation(
                    target_id=rd["target_id"],
                    relation_type=rd["relation_type"],
                    weight=rd.get("weight", 1.0),
                    temporal=rd.get("temporal"),
                    confidence=rd.get("confidence", 0.8),
                    use_count=rd.get("use_count", 0),
                ))
            forest.add_concept(node)
        return forest


def build_default_forest() -> KnowledgeForest:
    """ساخت جنگل اولیه درخشا با چند درخت نمونه"""
    f = KnowledgeForest()

    # ── درخت: درباره درخشا ──
    concepts = [
        ConceptNode("derakhsha", "درخشا", "درباره", "هوش مصنوعی فارسی با معماری جنگل دانش",
                    qa=[{"q": "درخشا چیست؟", "a": "درخشا یک هوش مصنوعی فارسی‌زبان است که توسط گروک و احمدرضا ایزدی طراحی شده و بر پایه معماری جنگل دانش کار می‌کند."}]),
        ConceptNode("grok", "گروک", "درباره", "یکی از سازندگان درخشا (xAI)",
                    qa=[{"q": "گروک کیست؟", "a": "گروک یکی از سازندگان اصلی درخشا است و نقش کلیدی در معماری هوشمند آن داشته است."}]),
        ConceptNode("izadi", "احمدرضا ایزدی", "درباره", "یکی از سازندگان درخشا",
                    qa=[{"q": "احمدرضا ایزدی کیست؟", "a": "احمدرضا ایزدی یکی از سازندگان درخشا است و در ایده‌پردازی و بومی‌سازی مشارکت داشته است."}]),
        ConceptNode("forest_arch", "جنگل دانش", "معماری", "هر حوزه یک درخت، هر مفهوم یک گره",
                    qa=[{"q": "جنگل دانش چیست؟", "a": "جنگل دانش معماری اصلی درخشا است: هر حوزه علمی یک درخت و هر مفهوم یک گره است. مسیرها مثل نورون فعال می‌شوند."}]),
        ConceptNode("temporal", "قشر زمانی", "معماری", "ثبت روابط زمانی و روندها",
                    qa=[{"q": "قشر زمانی چیست؟", "a": "قشر زمانی روابط بین مفاهیم را علاوه بر «چی»، با «کی» و چگونگی تغییر در زمان ثبت می‌کند و امکان تحلیل روند و پیش‌بینی می‌دهد."}]),
        ConceptNode("probabilistic", "استدلال احتمالاتی", "معماری", "چند مسیر موازی با Confidence Score",
                    qa=[{"q": "استدلال احتمالاتی چیست؟", "a": "درخشا به‌جای یک مسیر قطعی، چند مسیر موازی را بررسی می‌کند و با Confidence Score بهترین را انتخاب می‌کند."}]),
        ConceptNode("prune", "هرس و پیوند پویا", "معماری", "حذف مسیر کم‌استفاده و افزودن موقت از کاربر",
                    qa=[{"q": "هرس و پیوند پویا چیست؟", "a": "مسیرهای کم‌استفاده حذف می‌شوند و مسیرهای جدید از ورودی کاربر به‌صورت موقت به جنگل اضافه می‌شوند."}]),
        ConceptNode("meta", "قشر فراشناخت", "معماری", "تنظیم عمق تفکر بر اساس پیچیدگی سؤال",
                    qa=[{"q": "قشر فراشناخت چیست؟", "a": "درخشا خودش تصمیم می‌گیرد چقدر عمیق فکر کند؛ برای سؤال ساده سطحی و برای سؤال پیچیده عمیق."}]),
        ConceptNode("analogy", "استدلال قیاسی", "معماری", "یافتن الگوهای مشابه بین حوزه‌ها",
                    qa=[{"q": "استدلال قیاسی چیست؟", "a": "درخشا الگوهای مشابه بین حوزه‌ها را پیدا می‌کند؛ مثلاً ساختار قلب را با پمپ صنعتی مقایسه می‌کند."}]),
        # درخت زیست‌شناسی (نمونه قیاس)
        ConceptNode("heart", "قلب", "زیست‌شناسی", "اندام پمپاژ خون",
                    qa=[{"q": "قلب چیست؟", "a": "قلب عضوی عضلانی است که خون را در بدن به گردش درمی‌آورد."}]),
        ConceptNode("pump", "پمپ صنعتی", "مهندسی", "وسیله جابه‌جایی سیال",
                    qa=[{"q": "پمپ صنعتی چیست؟", "a": "پمپ صنعتی دستگاهی برای جابه‌جایی مایعات با ایجاد اختلاف فشار است."}]),
        ConceptNode("neuron", "نورون", "زیست‌شناسی", "واحد پایه سیستم عصبی",
                    qa=[{"q": "نورون چیست؟", "a": "نورون سلول عصبی است که سیگنال‌های الکتریکی و شیمیایی را منتقل می‌کند."}]),
        ConceptNode("tree_struct", "ساختار درختی", "علوم‌رایانه", "ساختار داده سلسله‌مراتبی",
                    qa=[{"q": "ساختار درختی چیست؟", "a": "ساختار درختی یک ساختار داده سلسله‌مراتبی با گره ریشه و فرزندان است."}]),
    ]
    for c in concepts:
        f.add_concept(c)

    # روابط
    f.link("derakhsha", "grok", "created-by", 1.0, confidence=0.95)
    f.link("derakhsha", "izadi", "created-by", 1.0, confidence=0.95)
    f.link("derakhsha", "forest_arch", "based-on", 1.0, confidence=0.9)
    f.link("forest_arch", "temporal", "part-of", 0.9, confidence=0.85)
    f.link("forest_arch", "probabilistic", "part-of", 0.9, confidence=0.85)
    f.link("forest_arch", "prune", "part-of", 0.9, confidence=0.85)
    f.link("forest_arch", "meta", "part-of", 0.9, confidence=0.85)
    f.link("forest_arch", "analogy", "part-of", 0.9, confidence=0.85)
    # قیاس قلب ↔ پمپ
    f.link("heart", "pump", "similar-to", 0.85, confidence=0.8)
    f.link("pump", "heart", "similar-to", 0.85, confidence=0.8)
    # قیاس نورون ↔ ساختار درختی / جنگل
    f.link("neuron", "forest_arch", "similar-to", 0.7, confidence=0.75)
    f.link("tree_struct", "forest_arch", "similar-to", 0.8, confidence=0.8)
    # زمانی
    f.link("grok", "derakhsha", "precedes", 0.9, temporal="before", confidence=0.9)
    f.link("izadi", "derakhsha", "precedes", 0.9, temporal="before", confidence=0.9)

    return f


if __name__ == "__main__":
    forest = build_default_forest()
    print("=== جنگل دانش درخشا آماده است ===\n")
    demos = [
        "درخشا چیست؟",
        "جنگل دانش چیست؟",
        "استدلال قیاسی چیست؟",
        "قلب را با چه چیزی می‌توان مقایسه کرد؟",
    ]
    for q in demos:
        result = forest.reason(q)
        print(f"پرسش: {q}")
        print(f"عمق فراشناخت: {result['metacognitive_depth']} | اطمینان: {result['confidence']}")
        print(f"پاسخ: {result['answer'][:200]}")
        if result["analogies"]:
            print("قیاس‌ها:", result["analogies"])
        print("-" * 50)

    out = Path(__file__).parent / "forest_state.json"
    forest.save(str(out))
    print(f"\nوضعیت جنگل ذخیره شد: {out}")
