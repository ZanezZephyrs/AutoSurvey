
from llm_inference.base import LLMInference
import openai

class OpenAIInference(LLMInference):
    def __init__(self, api_key, engine) -> None:
        self.api_key=api_key
        self.engine=engine 
        openai.api_key = self.api_key
        pass

    def complete(self, messages):
        completion = openai.ChatCompletion.create(model=self.engine, messages=messages)
        return completion.choices[0].message.content
