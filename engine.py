# -*- coding: utf-8 -*-
"""
موتور اصلی درخشا
قشر زبان + درخت دانش + یادگیری + پیوند گفتگو + اعتماد
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from .language import LanguageCortex
from .tree import KnowledgeTree
from .dialogue import DialogueLinker


class DerakhshaEngine:
    def __init__(self):
        self.language = LanguageCortex()
        self.tree = KnowledgeTree()
        self.dialogue = DialogueLinker()

    def chat(self, message: str, session_id: str = "default", style: Optional[str] = None) -> Dict[str, Any]:
        mem = self.dialogue.get(session_id)
        prev_kw = mem.previous_keyword_set()
        analysis = self.language.analyze(message, previous_keywords=prev_kw)

        kw_terms = [k.term for k in analysis.keywords]
        mem.add_user(message, kw_terms, analysis.target_branches, analysis.nature)

        hits = self.tree.search(kw_terms, analysis.target_branches, limit=5)
        best = hits[0] if hits else None
        conf = min(0.99, (best["score"] / 3.0)) if best else 0.0
        # normalize rough confidence 0-100 later
        has_hit = best is not None and best["score"] >= 0.8

        route = self.dialogue.route(analysis.nature, has_hit, conf)

        if route == "clarify":
            answer = (
                "برای پاسخ دقیق‌تر، موضوع را با یک کلیدواژه مشخص‌تر بیان کنید "
                "یا سند مرتبط را در بخش دانش اضافه نمایید."
            )
            src = "شفاف‌سازی"
            conf_pct = 20
            branch = analysis.target_branches[0] if analysis.target_branches else "—"
            node_id = None
        elif route == "learn_hint":
            answer = (
                "درخواست شما ثبت شد. برای افزودن دانش، از بخش «دانش من» عنوان و متن را ارسال کنید "
                "تا در درخت دانش طبقه‌بندی شود."
            )
            src = "یادگیری"
            conf_pct = 40
            branch = "DOC"
            node_id = None
        elif best:
            answer = best["text"]
            src = "سند کاربر" if best["source"] == "user" else "هسته دانش"
            conf_pct = int(min(98, 50 + best["score"] * 15))
            branch = best["branch"]
            node_id = best["node_id"]
        else:
            answer = (
                "مسیر مطمئنی در درخت دانش فعال نشد. "
                "پرسش را دقیق‌تر کنید یا دانش مرتبط را بیفزایید."
            )
            src = "سامانه"
            conf_pct = 15
            branch = analysis.target_branches[0] if analysis.target_branches else "—"
            node_id = None

        # style adapt
        target_style = style or ("colloquial" if analysis.style == "colloquial" else None)
        if target_style:
            answer = self.language.convert_style(answer, target_style)

        mem.add_assistant(answer, node_id)

        return {
            "answer": answer,
            "confidence": conf_pct,
            "source": src,
            "branch": branch,
            "route": route,
            "analysis": {
                "sentence_type": analysis.sentence_type,
                "tense": analysis.tense,
                "style": analysis.style,
                "nature": analysis.nature,
                "keywords": [{"term": k.term, "class": k.class_id} for k in analysis.keywords],
                "target_branches": analysis.target_branches,
                "roles": analysis.roles,
            },
            "session_id": session_id,
        }

    def learn_document(
        self,
        title: str,
        body: str,
        doc_type: str = "مقاله",
        keywords: Optional[List[str]] = None,
        source: str = "user",
    ) -> Dict[str, Any]:
        analysis = self.language.analyze(f"{title}\n{body}")
        auto_kw = [k.term for k in analysis.keywords]
        merged = list(dict.fromkeys((keywords or []) + auto_kw))
        branches = analysis.target_branches or ["DOC"]
        if "DOC" not in branches:
            branches = list(branches) + ["DOC"]
        result = self.tree.add_document(title, body, doc_type, merged, branches, source=source)
        result["keywords"] = merged
        result["branches"] = branches
        result["doc_type"] = doc_type
        return result

    def list_branches(self) -> List[Dict[str, Any]]:
        out = []
        for code, b in self.tree.branches.items():
            out.append({
                "code": code,
                "name": b.name,
                "description": b.description,
                "node_count": len(b.nodes),
            })
        return out

    def analyze_only(self, text: str) -> Dict[str, Any]:
        return self.language.analyze(text).to_dict()
