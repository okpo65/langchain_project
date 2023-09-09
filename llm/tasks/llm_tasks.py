import torch
from celery import shared_task
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

from llm.metas.base_model import SQLChainModel, ChatMemoryModel
from llm.models import LogLLM, LogStateType, LLMTaskType


@shared_task(queue='default')
def task_llm_log_processing(log_id: int):
    log = LogLLM.objects.get(id=log_id)

    if log.task_type == LLMTaskType.MRC:
        # TODO: tokenizer, model to Singleton Class
        tokenizer = AutoTokenizer.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")
        model = AutoModelForQuestionAnswering.from_pretrained("Kdogs/klue-finetuned-squad_kor_v1")

        question = log.question
        context = log.context

        inputs = tokenizer(question, context, return_tensors="pt")

        input_length = inputs.input_ids.shape[1]
        if input_length > 512:
            log.add_state(LogStateType.Failed)
            return

        with torch.no_grad():
            outputs = model(**inputs)

        answer_start_index = outputs.start_logits.argmax()
        answer_end_index = outputs.end_logits.argmax()

        predict_answer_tokens = inputs.input_ids[0, answer_start_index: answer_end_index + 1]
        result = tokenizer.decode(predict_answer_tokens, skip_special_tokens=True)
        log.answer = result
        log.save()
        log.add_state(LogStateType.Succeeded)

    elif log.task_type == LLMTaskType.QA_SQL:
        question = log.question
        result = SQLChainModel().get_result(question)
        log.answer = result
        log.save()
        log.add_state(LogStateType.Succeeded)
    elif log.task_type == LLMTaskType.QA_SEARCH:
        question = log.question
        session_id = log.session.id
        result = ChatMemoryModel(session_id=session_id).get_result(question)
        log.answer = result
        log.save()
        log.add_state(LogStateType.Succeeded)
    else:
        log.add_state(LogStateType.Failed)
