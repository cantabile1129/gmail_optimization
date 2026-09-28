from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from .models import Message
from .policy import Policy, classify


@dataclass(frozen=True)
class Candidate:
    sender: str
    list_id: str
    message_count: int
    unread_count: int
    protected_count: int
    promotional_count: int
    recommendation: str
    sender_wide_caution: bool


def build_report(messages: Iterable[Message], policy: Policy) -> list[Candidate]:
    groups: dict[tuple[str, str], list[Message]] = defaultdict(list)
    protected_senders: set[str] = set()
    for message in messages:
        groups[(message.sender_address, message.list_id)].append(message)
        if classify(message, policy).protected:
            protected_senders.add(message.sender_address)

    candidates: list[Candidate] = []
    for (sender, list_id), group in groups.items():
        evidence = [classify(message, policy) for message in group]
        protected_count = sum(x.protected for x in evidence)
        promotional_count = sum(x.promotional for x in evidence)
        has_subscription = any(x.subscription for x in evidence)
        if protected_count and (promotional_count or has_subscription):
            recommendation = "review_preferences"
        elif protected_count:
            recommendation = "keep_review"
        elif has_subscription and promotional_count == len(group) and len(group) >= policy.min_unsubscribe_count:
            recommendation = "review_unsubscribe"
        elif has_subscription:
            recommendation = "review_quiet"
        else:
            recommendation = "manual_review"
        candidates.append(
            Candidate(
                sender=sender,
                list_id=list_id,
                message_count=len(group),
                unread_count=sum(x.unread for x in evidence),
                protected_count=protected_count,
                promotional_count=promotional_count,
                recommendation=recommendation,
                sender_wide_caution=(
                    recommendation == "review_unsubscribe" and sender in protected_senders
                ),
            )
        )
    return sorted(candidates, key=lambda x: (-x.message_count, x.sender, x.list_id))
