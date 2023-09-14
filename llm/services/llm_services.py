from safetensors import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

from llm.models import LogStateType
import torch
import numpy as np


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls) \
                .__call__(*args, **kwargs)
        return cls._instances[cls]


class HuggingfaceBERTInstance(metaclass=Singleton):
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")
        self.model = AutoModelForQuestionAnswering.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")

    def get_tokenizer_input(self, question, context):
        inputs = self.tokenizer(question, context, return_tensors="pt")
        return inputs

    def decode(self, inputs):
        with torch.no_grad():
            outputs = self.model(**inputs)

        answer_start_index = outputs.start_logits.argmax()
        answer_end_index = outputs.end_logits.argmax()

        predict_answer_tokens = inputs.input_ids[0, answer_start_index: answer_end_index + 1]
        result = self.tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)
        return result

    def check_length(self, inputs):
        input_length = inputs.input_ids.shape[1]
        if input_length > 512:
            return False
        return True
