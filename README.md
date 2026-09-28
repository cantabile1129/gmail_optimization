# Gmail Triage Lab

**受信量の多い配信を先に見つけ、重要メールを守りながらGmailを整理するためのローカル分析ツール。**

就職活動向けの公開可能な開発事例として、個人情報を含まない架空データのデモを同梱しています。実際のGmailを扱う場合も、アプリは受信トレイのメタデータを読み、候補を画面に表示するだけです。メールの削除・既読化・ラベル付け・配信停止は実行しません。

## デモ

Python 3.11以降で、リポジトリ内から実行します。

**画面で試す:** [メール整理シミュレーター](demo/index.html)をブラウザで開いてください。架空の受信トレイで表示方法、スター、保護、既読、アーカイブ、削除、配信停止を操作できます。「次の週を受信」で新着メールへの影響を確認できます。画面は完全にオフラインで動き、操作内容も外部送信・保存しません。

このデモは設定を理解するための模型です。実アカウントでの誤分類率や配信停止の動作を再現しきれません。[網羅できない点と確認計画](docs/coverage.md)を併せて読んでください。

操作の順序は[デモで初期設定を試す手順](docs/trial.md)にまとめています。
設計の根拠は[参照資料と判断](docs/research.md)にまとめています。

**候補判定を試す:** 以下を実行します。

```powershell
python -m pip install -e .
gmail-triage demo
```

デモは`examples/demo_messages.json`の架空メールのみを使い、Googleへの接続は行いません。送信者別の件数、未読数、保護候補数と、配信停止・通知設定変更・後で読む・維持の**検討候補**を表示します。

## 実際のGmailで試す場合

1. 自分のGoogle CloudプロジェクトでGmail APIを有効化し、デスクトップアプリ用OAuthクライアントを作成します。[Google公式のPythonクイックスタート](https://developers.google.com/workspace/gmail/api/quickstart/python)を参照してください。
2. OAuthクライアントのJSONを`private/credentials.json`として保存します。このディレクトリはGitの追跡対象外です。OAuthテストユーザーに自分のアカウントを追加します。
3. 追加ライブラリを入れて実行します。

```powershell
python -m pip install -e ".[gmail]"
gmail-triage scan --max-messages 500
```

初回のみブラウザでGoogleの許可画面が開きます。許可情報は`private/token.json`にローカル保存されます。標準設定では**受信トレイの新しい500通まで**を対象とします。本文と添付ファイルは取得せず、`From`、`Subject`、`List-Id`とGmailラベルだけを処理します。件名も結果には表示・保存しません。ただし、送信者名や件名自体が個人情報になり得るため、実アカウントの画面出力やスクリーンショットは公開しないでください。

`gmail.metadata`は本文を読めない権限ですが、Googleの分類では**制限付きOAuthスコープ**です。コードをGitHubに公開することと、多人数向けにOAuthアプリを公開することは別です。個人利用・テスト利用では確認画面や人数制限などの条件があります。第三者向けサービスに拡大する前に、Googleの審査要件を確認してください。[権限一覧](https://developers.google.com/workspace/gmail/api/auth/scopes)・[審査不要の場合](https://support.google.com/cloud/answer/13464323?hl=en)

## 自分の判断基準に合わせる

`examples/policy.example.json`を参考に、**個人用の設定ファイルを`private/policy.json`**に作れます。`protected_senders`に必ず守るアドレス、`protect_keywords`に請求・認証などの語、`promo_keywords`に販促語を設定します。

```powershell
gmail-triage demo --policy private/policy.json
gmail-triage scan --policy private/policy.json --top 20
```

初期ルールは[docs/architecture.md](docs/architecture.md)に記載しています。提案が誤る可能性を前提とし、判断が難しいものや保護条件に当たるものは人が確認する設計です。

## 公開範囲と安全設計

- 公開対象: ソースコード、架空メール、説明書、テスト。
- 公開対象外: 実メール、送信者一覧、OAuthクライアント情報、トークン、個人用ポリシー、実アカウントの出力。
- Gmailへの変更操作は実装していません。配信停止もGmail画面で本人が判断します。
- Gmail以外の分析サービスやAI APIにはメール情報を送りません。
- `.gitignore`に加えて、コミット前に追跡ファイルを目視で確認してください。GitHubでは、一度公開した認証情報を履歴から完全に消す作業が難しくなります。[GitHub公式の注意事項](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

## 開発事例として説明できる点

大量の未読を個別に開く代わりに送信者・配信リスト単位で優先順位を付けること、請求や認証のメールが混ざる送信者の一括解除を警告すること、最小限の取得範囲と読み取り専用の設計が主眼です。テストでは、保護対象の優先判定と、Gmail本文を要求せず変更操作を呼ばないことを確認します。

```powershell
python -m unittest discover -s tests -v
```

## 制約

- 件名の語とGmailラベルを使う単純な推定です。価値判断の自動化や見落としゼロは保証できません。
- `gmail.metadata`ではGmailの検索文字列をAPIで使えないため、対象は受信トレイの新しい順に指定件数を取得します。[Gmail API仕様](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list)
- 購読解除の最終判断はGmailで行います。企業単位の一括解除では、必要な配信も止まる場合があります。[Gmail公式ヘルプ](https://support.google.com/mail/answer/15621070?co=GENIE.Platform%3DDesktop&hl=en-GB)

