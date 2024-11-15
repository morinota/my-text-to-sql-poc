# Langchain

## callbacksについて

- 参考:<https://book.st-hakky.com/data-science/langchain-callbacks/>
- callbacksとは
  - LangChainに限らずコールバックは、プログラミングにおいて非常に重要な概念。
  - **特定のイベントが発生したときに実行される関数や手続き**を指す。
- LangChainのコールバック
  - 特定のタスクが完了したとき、または特定のイベントが発生したときに呼び出される。これにより、**開発者は特定のタイミングでカスタムロジックを実行できる**ようになる。
    - ex.)
      - LangChainの学習プロセスが終了したときに通知を送る、
      - 特定の条件下で学習を早期終了する、
      - 学習中のモデルのパフォーマンスをログに記録する、etc.
- callback handler
  - LangchainのCallbacksを管理するためのクラス。
    - アプリケーションの特定のイベントに対して、自分で定義した処理を実行可能にする。
  - callback handlerが対応可能なイベント
    - `on_llm_start`: LLMの動作が開始されたとき
    - `on_chat_model_start`: チャットモデルの動作が開始されたとき
    - `on_llm_new_token`: LLMが新しいトークンを生成したとき
    - `on_llm_end`: LLMの動作が終了したとき
    - `on_chain_start`: チェーンの動作が開始されたとき
    - `on_chain_end`: チェーンの動作が終了したとき
    - `on_chain_error`: チェーンの動作中にエラーが発生したとき

- BaseCallbackHandler
  - 他のコールバックハンドラの親クラスとして機能する。すべてのメソッドはデフォルトで何もしないが、継承先のクラスでオーバーライドされる。
-
