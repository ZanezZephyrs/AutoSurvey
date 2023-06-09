from abc import ABC
from .base import LLMInference


class QueryAugmentor(ABC):
    def __init__(self, agent:LLMInference, few_shot_examples=None) -> None:
        self.agent=agent

        self.system_prompt =[
            {"role": "system", "content": "You Are an expert in translating article titles to keywords to be used in search queries, your job is, given a title, write keywords revelant to the title"},
        ]
        if few_shot_examples:
            self.few_shot_examples=few_shot_examples
        else:
            self.few_shot_examples=[
            {
                "role": "user",
                "content": "NeuralSearchX serving a multi-billion parameter reranking at scale - infrastructure and cost"
            },
            {
                "role": "assistant",
                "content": "multi-billion parameter reranker\ninfrastructure for rerankers\ncost of serving big rerankers"
            },
            ]


    def augment_queries(self,title):
        prompt=self.system_prompt.copy()

        prompt.extend(self.few_shot_examples)

        prompt.append(
            {
            "role": "user",
            "content": title
            }
        )

        return self.agent.complete(prompt).split("\n")
    