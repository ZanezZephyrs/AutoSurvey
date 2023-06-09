import time
from .base import LLMInference
import openai

class OpenAIInference(LLMInference):
    def __init__(self, api_key, engine) -> None:
        self.api_key=api_key
        self.engine=engine 
        openai.api_key = self.api_key
        pass

    def complete(self, messages, max_tries=3):

        for i in range(max_tries):
            try:
                completion = openai.ChatCompletion.create(model=self.engine, messages=messages)
                break
            except Exception as e:
                print(e)
                print("trying again")
                time.sleep(2)
                if i==max_tries-1:
                    raise e
                else:
                    continue
        return completion.choices[0].message.content
