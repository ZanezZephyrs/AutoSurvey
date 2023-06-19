from typing import List
from math import exp

from tqdm.auto import tqdm

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)
import torch

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
      yield lst[i:i + n]


class MonoT5():
    def __init__(self, model_name_or_path: str = 'castorini/monot5-base-msmarco-10k', fp16: bool = False):
        """
        Loads the T5 model from the given path.
        Args:
            model_name_or_path: path to the model
            fp16: whether the model should be loaded using FP16
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        # The training was carried out using two specific tokens for relevant and non-relevant passages
        self.token_false_id = self.tokenizer.get_vocab()['▁false']
        self.token_true_id  = self.tokenizer.get_vocab()['▁true']

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Loads the model with model_args
        model_args = {}
        if fp16:
            model_args["torch_dtype"] = torch.float16

        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name_or_path, **model_args).to(self.device)

    @torch.no_grad()
    def rescore(self, query: str, docs: List[str], batch_size: int = 8):
        """
        Adapted from Pygaggle's repo.
        Rescore all documents for the given query.
        Args:
            query: the query for ranking
            batch: list of passages for ranking
        """
        scores = []
        for batch in tqdm(chunks(docs, batch_size), total=len(docs)//batch_size, desc="Rescoring documents"):
            # Creates the inputs to the model
            queries_documents = [f"Query: {query} Document: {text} Relevant:" for text in batch]
            tokenized = self.tokenizer(
                queries_documents,
                padding=True,
                truncation="longest_first",
                return_tensors="pt",
                max_length=512,
            ).to(self.device)
            input_ids = tokenized["input_ids"].to(self.device)
            attention_mask = tokenized["attention_mask"].to(self.device)
            _ , batch_scores = self.greedy_decode(model=self.model,
                                                input_ids=input_ids,
                                                length=1,
                                                attention_mask=attention_mask,
                                                return_last_logits=True)
            batch_scores = batch_scores[:, [self.token_false_id, self.token_true_id]]
            batch_scores = torch.nn.functional.log_softmax(batch_scores, dim=1)
            batch_log_probs = batch_scores[:, 1].tolist()
            batch_probs = [exp(log_prob) for log_prob in batch_log_probs]
            scores.extend(batch_probs)
        return scores

    @torch.no_grad()
    def greedy_decode(
        self,
        model,
        input_ids: torch.Tensor,
        length: int,
        attention_mask: torch.Tensor = None,
        return_last_logits: bool = True
    ):
        """
        Adapted from Pygaggle's repo.
        Performs the greedy_decode on t5's output.
        """
        decode_ids = torch.full((input_ids.size(0), 1),
                                model.config.decoder_start_token_id,
                                dtype=torch.long).to(input_ids.device)
        encoder_outputs = model.get_encoder()(input_ids, attention_mask=attention_mask)
        next_token_logits = None
        for _ in range(length):
            model_inputs = model.prepare_inputs_for_generation(
                decode_ids,
                encoder_outputs=encoder_outputs,
                past=None,
                attention_mask=attention_mask,
                use_cache=True)
            outputs = model(**model_inputs)  # (batch_size, cur_len, vocab_size)
            next_token_logits = outputs[0][:, -1, :]  # (batch_size, vocab_size)
            decode_ids = torch.cat([decode_ids,
                                    next_token_logits.max(1)[1].unsqueeze(-1)],
                                dim=-1)
        if return_last_logits:
            return decode_ids, next_token_logits
        return decode_ids
     