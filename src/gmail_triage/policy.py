from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path

from .models import Message


DEFAULT_PROTECT = (
    "請求", "領収", "支払", "注文", "予約", "契約", "認証", "確認コード",
    "セキュリティ", "invoice", "receipt", "payment", "order",
    "reservation", "booking", "contract", "verification", "security",
    "password", "one-time code",
)
DEFAULT_PROMO = (
    "セール", "クーポン", "割引", "キャンペーン", "特価",
    "sale", "coupon", "discount", "promotion", "special offer",
)


@dataclass(frozen=True)
class Policy:
    protect_keywords: tuple[str, ...] = DEFAULT_PROTECT
    promo_keywords: tuple[str, ...] = DEFAULT_PROMO
    protected_senders: tuple[str, ...] = ()
    min_unsubscribe_count: int = 2

    @classmethod
    def load(cls, path: Path | None) -> "Policy":
        if path is None:
            return cls()
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("Policy must be a JSON object")
        valid_names = {field.name for field in fields(cls)}
        unknown = set(raw) - valid_names
        if unknown:
            raise ValueError(f"Unknown policy keys: {', '.join(sorted(unknown))}")
        if "min_unsubscribe_count" in raw:
            count = raw["min_unsubscribe_count"]
            if type(count) is not int or count < 1:
                raise ValueError("min_unsubscribe_count must be a positive integer")
        for name in ("protect_keywords", "promo_keywords", "protected_senders"):
            if name in raw:
                value = raw[name]
                if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
                    raise ValueError(f"{name} must be a list of strings")
                raw[name] = tuple(x.strip().lower() for x in value if x.strip())
        return cls(**raw)


@dataclass(frozen=True)
class Evidence:
    protected: bool
    promotional: bool
    subscription: bool
    unread: bool
    reasons: tuple[str, ...]


def classify(message: Message, policy: Policy) -> Evidence:
    subject = message.subject.casefold()
    reasons: list[str] = []
    protected = False
    if message.sender_address in {s.casefold() for s in policy.protected_senders}:
        protected = True
        reasons.append("protected sender")
    if {"STARRED", "IMPORTANT", "CATEGORY_PERSONAL"} & message.labels:
        protected = True
        reasons.append("priority label")
    if any(word.casefold() in subject for word in policy.protect_keywords):
        protected = True
        reasons.append("protected subject")
    promotional = (
        "CATEGORY_PROMOTIONS" in message.labels
        or any(word.casefold() in subject for word in policy.promo_keywords)
    )
    subscription = bool(message.list_id)
    return Evidence(
        protected=protected,
        promotional=promotional,
        subscription=subscription,
        unread="UNREAD" in message.labels,
        reasons=tuple(reasons),
    )
