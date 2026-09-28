# 設計判断に使った資料

Gmailの仕様は変更されることがあります。次のGoogle公式資料を基に、デモと実アカウントでの確認手順を分けました。

| 根拠 | 設計への反映 |
|---|---|
| [受信トレイの表示方法](https://support.google.com/mail/answer/18522?hl=en) | 「デフォルト」のカテゴリ、「優先トレイ」「未読優先」を別の見方として再現。 |
| [重要マークの判定](https://support.google.com/mail/answer/186543?hl=en) | 重要マークはGmailの推定であり、必ず手動の例外確認を行う。 |
| [ラベル・スター・アーカイブ・フィルタ](https://support.google.com/mail/answer/9259770?hl=en) | 対応を追うスターと、保存用の個人ラベルを分ける。既読とアーカイブも別の操作にする。 |
| [購読の管理](https://support.google.com/mail/answer/15621070?co=GENIE.Platform%3DDesktop) | 送信者単位の解除には関連リストと迷惑メールへの影響があるため、履歴を見てから判断する。 |
| [ワンクリック解除と配信リスト](https://support.google.com/mail/answer/14229414?hl=en) | メール単位の解除はリスト単位。送信者単位との違いをデモで見せる。 |
| [Gmail検索演算子](https://support.google.com/mail/answer/7190?hl=en-IN) | 古い未読や大きな添付は、現版の分析対象外としてGmail検索で別途確認する。 |
| [Gmailストレージ管理](https://support.google.com/mail/answer/6374270/manage-files-in-your-google-drive-storage?hl=en) | 容量不足が目的なら、大容量添付を別途優先する。単に受信箱の件数を減らしても容量対策にならない。 |
| [Gmail APIの権限](https://developers.google.com/workspace/gmail/api/auth/scopes)・[messages.list](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/list) | 本文を取得しない`gmail.metadata`を使用。検索文字列をこの権限で使えないため、新しい受信トレイの指定件数に限定。 |

上記から導いた優先順位は、**重要メールを見つけられること → 新着の不要配信を減らすこと → 古いメールや容量の整理**です。個人ごとの「重要」「不要」は公式資料から決められないので、架空データで操作を理解した後、自分のメールを少量だけ確認して決めます。
