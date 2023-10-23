from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from llm.metas.base_model import SQLChainModel
from llm.models import Session, LogLLM, LogStateType, LLMTaskType


class RequestMRCAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        question = request.data['question']
        context = request.data['context']
        session_id = request.data['session_id']

        log = LogLLM.objects.create(question=question, session_id=session_id, context=context,
                                    task_type=LLMTaskType.MRC)
        log.add_state(state=LogStateType.Pending)
        from llm.tasks import task_llm_log_processing
        task_llm_log_processing.apply_async(
            (log.id,)
        )

        return Response({'log_id': log.id}, status=status.HTTP_200_OK)


class RequestQAAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        question = request.data['question']
        task_type = request.data['task_type']
        session_id = request.data['session_id']

        log = LogLLM.objects.create(question=question, session_id=session_id, task_type=task_type)
        log.add_state(state=LogStateType.Pending)

        # result = SQLChainModel().get_result(question)
        #
        # log.answer = result
        # log.save()
        # log.add_state(LogStateType.Succeeded)

        from llm.tasks import task_llm_log_processing
        task_llm_log_processing.apply_async(
            (log.id,)
        )

        return Response({'log_id': log.id}, status=status.HTTP_200_OK)


class GetResultLLMLog(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        log_id = request.query_params['log_id']
        log = LogLLM.objects.get(id=log_id)
        answer = log.answer
        state = log.states.last().state

        return Response({'answer': answer, 'state': state}, status=status.HTTP_200_OK)


class PollForResultAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        log_id = request.query_params['log_id']
        log = LogLLM.objects.get(id=log_id)

        state = log.states.last().state
        return Response({'state': state}, status=status.HTTP_200_OK)


class CreateSessionAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        session = Session.objects.create()
        return Response({'session_id': session.id}, status=status.HTTP_200_OK)
