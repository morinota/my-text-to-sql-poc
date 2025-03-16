# Streamlit メモ

- refs:
  - nikkieさんがlink貼ってたので参考になりそう??: [Python Web UIフレームワーク Streamlitの基本](https://gihyo.jp/article/2024/10/monthly-python-2410)
    - 入力と出力のコンポーネント達を紹介してる感じ
  - ワークショップで紹介されてた参考文献: [Streamlit in Snowflakeについて](https://docs.snowflake.com/ja/developer-guide/streamlit/about-streamlit)
  - ワークショップで、pdfをmarkdownに変換するのに使ってたパッケージ!: [pymupdf4llm](https://pymupdf.readthedocs.io/ja/latest/pymupdf4llm/)

- StreamlitでUI作る時のディレクトリ構成って??
  - app.pyとかで全部書くのでいい??
    - そもそもStreamlit自体は、複雑なアプリケーションを作るためのフレームワークではない。xxx
    - -> 複雑性管理のモチベーションが低い。
    - -> だから、app.pyに全部書いてもそこまで問題はないのかも。
