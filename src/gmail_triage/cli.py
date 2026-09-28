from __future__ import annotations

import argparse
import json
from pathlib import Path

from .gmail_reader import connect, read_recent_metadata
from .models import Message
from .policy import Policy
from .report import Candidate, build_report


RECOMMENDATIONS = {
    "review_unsubscribe": "配信停止を検討",
    "review_preferences": "配信設定を個別に確認",
    "review_quiet": "後で読む設定を検討",
    "keep_review": "保護・維持を確認",
    "manual_review": "個別確認",
}


def render(candidates: list[Candidate], limit: int) -> str:
    lines = [
        "送信者ごとの候補（提案のみ。Gmailへの変更は行いません）",
        "件数  未読  保護候補  提案  送信元 / 配信リスト",
    ]
    for item in candidates[:limit]:
        suffix = " ※送信者一括解除に注意" if item.sender_wide_caution else ""
        group = f" / {item.list_id}" if item.list_id else ""
        lines.append(
            f"{item.message_count:>4}  {item.unread_count:>4}  "
            f"{item.protected_count:>8}  {RECOMMENDATIONS[item.recommendation]}  "
            f"{item.sender}{group}{suffix}"
        )
    lines.append("※件名とメール本文は表示・保存しません。提案には必ず人の確認が必要です。")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Gmail triage candidate finder")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Run on entirely synthetic example data")
    demo.add_argument("--fixture", type=Path, default=Path(__file__).resolve().parents[2] / "examples" / "demo_messages.json")
    scan = sub.add_parser("scan", help="Read Gmail metadata locally; no changes")
    scan.add_argument("--credentials", type=Path, default=Path("private/credentials.json"))
    scan.add_argument("--token", type=Path, default=Path("private/token.json"))
    scan.add_argument("--max-messages", type=int, default=500)
    for command in (demo, scan):
        command.add_argument("--policy", type=Path, help="Private local JSON policy file")
        command.add_argument("--top", type=int, default=20)
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error("--top must be positive")
    policy = Policy.load(args.policy)
    if args.command == "demo":
        raw = json.loads(args.fixture.read_text(encoding="utf-8"))
        messages = [Message.from_fixture(item) for item in raw]
    else:
        if args.max_messages < 1:
            parser.error("--max-messages must be positive")
        service = connect(args.credentials, args.token)
        messages = read_recent_metadata(service, args.max_messages)
    print(f"分析対象: {len(messages)} 通（最新から）")
    print(render(build_report(messages, policy), args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
