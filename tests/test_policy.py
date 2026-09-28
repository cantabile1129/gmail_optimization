import json
import tempfile
import unittest
from pathlib import Path

from gmail_triage.models import Message
from gmail_triage.policy import Policy, classify
from gmail_triage.report import build_report


def msg(identifier, sender, subject, list_id="", labels=()):
    return Message(identifier, sender, subject, list_id, frozenset(labels))


class PolicyTests(unittest.TestCase):
    def test_transactional_message_overrides_promotions_category(self):
        item = msg("1", "x@example.com", "注文確認", labels=["CATEGORY_PROMOTIONS"])
        evidence = classify(item, Policy())
        self.assertTrue(evidence.protected)
        self.assertTrue(evidence.promotional)
        self.assertEqual(build_report([item], Policy())[0].recommendation, "review_preferences")

    def test_subscription_from_sender_with_receipt_warns_on_sender_wide_unsubscribe(self):
        messages = [
            msg("1", "News <news@shop.example>", "セール", "news.shop.example", ["CATEGORY_PROMOTIONS"]),
            msg("2", "News <news@shop.example>", "割引", "news.shop.example", ["CATEGORY_PROMOTIONS"]),
            msg("3", "News <news@shop.example>", "領収書"),
        ]
        report = build_report(messages, Policy())
        mailing = next(x for x in report if x.list_id)
        self.assertEqual(mailing.recommendation, "review_unsubscribe")
        self.assertTrue(mailing.sender_wide_caution)

    def test_unknown_messages_are_never_unsubscribe_candidates(self):
        report = build_report([msg("1", "person@example.net", "こんにちは")], Policy())
        self.assertEqual(report[0].recommendation, "manual_review")

    def test_promotional_sender_without_mailing_list_needs_manual_review(self):
        report = build_report([
            msg("1", "news@shop.example", "セール", labels=["CATEGORY_PROMOTIONS"]),
            msg("2", "news@shop.example", "クーポン", labels=["CATEGORY_PROMOTIONS"]),
        ], Policy())
        self.assertEqual(report[0].recommendation, "manual_review")

    def test_custom_sender_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "policy.json"
            path.write_text(json.dumps({"protected_senders": ["VIP@example.net"]}), encoding="utf-8")
            policy = Policy.load(path)
        self.assertTrue(classify(msg("1", "vip@example.net", "hello"), policy).protected)


if __name__ == "__main__":
    unittest.main()
