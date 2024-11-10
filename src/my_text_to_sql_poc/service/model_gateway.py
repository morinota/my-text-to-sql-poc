import os

import openai
from loguru import logger
from openai.types.chat.chat_completion import ChatCompletion


class ModelGateway:
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        show_usage_cost: bool = True,
    ) -> None:
        # APIキーとモデルの設定
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を確認してください。")

        self.model_name = model_name
        openai.api_key = self.api_key
        self.show_usage_cost = show_usage_cost

    def generate_response(self, prompt: str) -> str:
        """生成AIモデルにプロンプトを送信して応答を取得する関数"""
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            response_text = response.choices[0].message.content
            logger.debug(f"Model response: {response_text}")

            if self.show_usage_cost:
                self._show_usage(response)

            return response_text
        except Exception as e:
            logger.error(f"生成AIモデルのAPI呼び出しに失敗しました: {e}")
            raise

    def _show_usage(self, response: ChatCompletion) -> dict[str, float]:
        """使用トークン数を取得してコストを計算して表示する関数"""
        usage = response.usage
        prompt_tokens = usage.prompt_tokens
        completion_tokens = usage.completion_tokens
        total_tokens = usage.total_tokens

        # コスト計算
        input_cost_dollar = prompt_tokens * (0.15 / 1_000_000)  # $0.15 / 1M tokens
        output_cost_dollar = completion_tokens * (0.60 / 1_000_000)  # $0.60 / 1M tokens
        total_cost_dollar = input_cost_dollar + output_cost_dollar

        logger.info(f"Input tokens: {prompt_tokens}")
        logger.info(f"Output tokens: {completion_tokens}")
        logger.info(f"Total tokens: {total_tokens}")
        logger.info(
            f"Cost - Input: {input_cost_dollar:.6f} USD, Output: {output_cost_dollar:.6f} USD, Total: {total_cost_dollar:.6f} USD"
        )


if __name__ == "__main__":
    gateway = ModelGateway(show_usage_cost=False)
    response = gateway.generate_response("こんにちは!")
    print(response)
