Bug Report

BTAは現段階で以下の既知の問題があります。

* Mac版では、うまく図を生成することができず解析途中で落ちます。

  => しばらくの間、Mac版ではMake Figureにチェックを入れずにご使用ください。

* Mac版において、初回起動のときのマイク使用許可確認ダイアログとドキュメントフォルダ
  保存許可確認ダイアログの出現タイミングを制御することができていません。

  => 初回起動時はマイク使用許可確認ダイアログとドキュメントフォルダ保存許可確認ダイアログを
     OKするためだけにとどめて、2回目の起動から本格的にご使用ください。

* Mac版は現時点では動作が不安定ですのでWindows版の使用をお勧めします。


============================================================================

Version変更履歴


* Ver0.9.6

  〇 Excelテンプレート各種発話時間の単純集計を仕上げました。

  〇 入力が小さすぎる場合に記録が「0.00」と表示される問題に対して表示を「Low Input」と改め、計算に入れないようにしました。

  〇 解析MethodのMFCCでは、音声の取りこぼしが頻発する問題があるため、改善Methodとして、より高精度が期待できる「Mix」を追加しました。
  
  〇 検査開始前に課題語をシャフルする機能を追加しました。


* Ver0.9.5

  初回リリース
