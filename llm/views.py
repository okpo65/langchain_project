from django.shortcuts import render
from langchain import OpenAI, SQLDatabase
from langchain.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
import os
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch

class GetMRCResultAPIView(APIView):
    permission_classes = [AllowAny]

    tokenizer = AutoTokenizer.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")
    model = AutoModelForQuestionAnswering.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")

    def post(self, request):
        question = request.data['question']
        context = request.data['context']

        inputs = self.tokenizer(question, context, return_tensors="pt")

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

        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_NAME = os.getenv('DB_NAME')
        DB_PORT = os.getenv('DB_PORT')
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

        db = SQLDatabase.from_uri(
            f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
        )

        # setup llm
        # llm = OpenAI(temperature=0, openai_api_key=OPENAI_API_KEY)
        llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name='gpt-4')

        # Create db chain
        QUERY = """
                Given an input question, first create a syntactically correct postgresql query to run, then look at the results of the query and return the answer.

                Make sure to include the unit of measurement from the 'UNIT_NAME' column and 'DATE' column in your final answer with korean.
                Ignore 'UNIT_NAME' if it is None.
                Find the one-word keyword in the question.

                Follow these steps:

                1. Use the identified keyword to formulate a PostgreSQL query. Your query should find rows where the keyword appears in the 'STAT_NAME' column using the LIKE operator with % as wildcards. If specific dates are provided in the question, include them in your query using the = operator to obtain values for each individual date. Limit the row count to 100.
                2. In the SQL results, identify the oldest date as the "Comparison Date" and the latest date as the "Reference Date". Calculate the difference by subtracting the value at the Comparison Date from that at the Reference Date. If the result is positive, it means the value has increased from the Comparison Date to the Reference Date. If the result is negative, it indicates a decrease.
                3. Summarize the answer based on the SQL results with Korean. 

                Here is the format to follow:

                Question: Question here
                SQLQuery: SQL Query to run
                SQLResult: Result of the SQLQuery
                Answer: Final answer here

                {question}
                """
        # Setup the database chain
        db_chain = SQLDatabaseChain(llm=llm, database=db, verbose=True, use_query_checker=True)
        question = QUERY.format(question=question)
        result = db_chain.run(question)
        return Response({'result': result}, status=status.HTTP_200_OK)


class PollForResultAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        return Response({'result': ''}, status=status.HTTP_200_OK)
