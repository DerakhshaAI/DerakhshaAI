# -*- coding: utf-8 -*-
"""پیوند گفتگو — ماهیت جمله و حافظه کوتاه‌مدت نشست"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Set, Any


@dataclass
class Turn:
    role: str  # user | assistant
    text: str
    keywords: List[str] = field(default_factory=list)
    branches: List[str] = field(default_factory=list)
    nature: str = "TELL"


@dataclass
class SessionMemory:
    session_id: str
    turns: List[Turn] = field(default_factory=list)
    active_keywords: Set[str] = field(default_factory=set)
    active_branches: List[str] = field(default_factory=list)
    last_node_id: Optional[str] = None
    topic: Optional[str] = None

    def add_user(self, text: str, keywords: List[str], branches: List[str], nature: str):
        self.turns.append(Turn("user", text, keywords, branches, nature))
        self.active_keywords = set(keywords) | (self.active_keywords if nature == "CONT" else set(keywords))
        if branches:
            self.active_branches = branches
        if keywords:
            self.topic = keywords[0]

    def add_assistant(self, text: str, node_id: Optional[str] = None):
        self.turns.append(Turn("assistant", text))
        if node_id:
            self.last_node_id = node_id

    def previous_keyword_set(self) -> Set[str]:
        if len(self.turns) < 1:
            return set()
        # last user turn keywords before current
        for t in reversed(self.turns[:-1] if self.turns else []):
            if t.role == "user" and t.keywords:
                return set(t.keywords)
        return set()


class DialogueLinker:
    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}

    def get(self, session_id: str) -> SessionMemory:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory(session_id=session_id)
        return self.sessions[session_id]

    def route(self, nature: str, has_tree_hit: bool, confidence: float) -> str:
        """tree | dialogue | learn | clarify"""
        if nature == "REQ" and not has_tree_hit:
            return "learn_hint"
        if confidence >= 0.4 and has_tree_hit:
            return "tree"
        if nature in ("CONT", "FIX") and has_tree_hit:
            return "tree"
        if confidence < 0.25:
            return "clarify"
        if has_tree_hit:
            return "tree"
        return "dialogue"
