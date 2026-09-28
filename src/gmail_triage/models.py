from __future__ import annotations

from dataclasses import dataclass
from email.utils import parseaddr


@dataclass(frozen=True)
class Message:
    message_id: str
    sender: str
    subject: str
    list_id: str
    labels: frozenset[str]

    @property
    def sender_address(self) -> str:
        address = parseaddr(self.sender)[1].strip().lower()
        return address or self.sender.strip().lower() or "(unknown sender)"

    @classmethod
    def from_gmail(cls, item: dict) -> "Message":
        headers = {
            header.get("name", "").lower(): header.get("value", "")
            for header in item.get("payload", {}).get("headers", [])
        }
        return cls(
            message_id=str(item["id"]),
            sender=headers.get("from", ""),
            subject=headers.get("subject", ""),
            list_id=headers.get("list-id", "").strip().lower(),
            labels=frozenset(item.get("labelIds", [])),
        )

    @classmethod
    def from_fixture(cls, item: dict) -> "Message":
        return cls(
            message_id=str(item["id"]),
            sender=item["from"],
            subject=item.get("subject", ""),
            list_id=item.get("list_id", "").strip().lower(),
            labels=frozenset(item.get("labels", [])),
        )
