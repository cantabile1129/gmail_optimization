import unittest
from unittest.mock import MagicMock

from gmail_triage.gmail_reader import HEADERS, read_recent_metadata


class GmailReaderTests(unittest.TestCase):
    def test_metadata_only_and_no_mutation(self):
        service = MagicMock()
        api = service.users.return_value.messages.return_value
        api.list.return_value.execute.return_value = {"messages": [{"id": "m1"}]}
        api.get.return_value.execute.return_value = {
            "id": "m1", "labelIds": ["UNREAD"],
            "payload": {"headers": [
                {"name": "From", "value": "Demo <demo@example.net>"},
                {"name": "Subject", "value": "Sample"},
            ]},
        }
        messages = read_recent_metadata(service, 1)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].sender_address, "demo@example.net")
        api.get.assert_called_once_with(
            userId="me", id="m1", format="metadata", metadataHeaders=HEADERS,
        )
        api.list.assert_called_once_with(
            userId="me", maxResults=1, pageToken=None,
            labelIds=["INBOX"], includeSpamTrash=False,
        )
        api.trash.assert_not_called()
        api.modify.assert_not_called()
        api.delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()
