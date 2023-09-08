from django.shortcuts import render
from langchain import OpenAI, SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
import os
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

from llm.metas.base_model import SQLChainModel, ChatMemoryModel


class GetMRCResultAPIView(APIView):
    permission_classes = [AllowAny]

    tokenizer = AutoTokenizer.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")
    model = AutoModelForQuestionAnswering.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")

    def post(self, request):
        question = request.data['question']
        context = request.data['context']

        inputs = self.tokenizer(question, context, return_tensors="pt")

        input_length = inputs.input_ids.shape[1]
        if input_length > 512:
            raise ValidationError("The total number of tokens in the question and context cannot exceed 512.")

        with torch.no_grad():
            outputs = self.model(**inputs)

        answer_start_index = outputs.start_logits.argmax()
        answer_end_index = outputs.end_logits.argmax()

        predict_answer_tokens = inputs.input_ids[0, answer_start_index: answer_end_index + 1]
        result = self.tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)

        return Response({'result': result}, status=status.HTTP_200_OK)


class GetQAResultAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        question = request.data['question']
        task_type = request.data['task_type']

        if task_type == "sql":
            result = SQLChainModel().get_result(question)
        elif task_type == "search":
            result = ChatMemoryModel().get_result(question)
        return Response({'result': result}, status=status.HTTP_200_OK)


class PollForResultAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        return Response({'result': ''}, status=status.HTTP_200_OK)
