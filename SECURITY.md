# Privacy and security

This repository contains synthetic messages only. Live mode requests the Gmail metadata OAuth scope and displays suggestions locally. It does not request bodies or attachments and cannot modify mail with its requested scope.

**Never commit** OAuth client JSON, refresh/access tokens, real sender lists, real subjects, private policy files, live output, mailbox exports, or screenshots of live output. Store them in `private/` or outside the repository. The ignore rules are a backup safeguard; review staged files before every push.

If a token is accidentally published, revoke the app's access in your Google Account and rotate affected credentials. Removing a file in a later commit does not erase the exposed Git history. See [GitHub's guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

The tool makes suggestions, never executes unsubscribe, delete, archive, read-state, or label changes. A sender can use one address for both marketing and transactional mail. Review each suggestion in Gmail before acting.
