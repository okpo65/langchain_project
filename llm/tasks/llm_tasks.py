from celery import shared_task
from llm.metas.base_model import SQLChainModel, ChatMemoryModel
from llm.models import LogLLM, LogStateType, LLMTaskType
from llm.services.llm_services import HuggingfaceBERTInstance


@shared_task(queue='default')
def task_llm_log_processing(log_id: int):
    log = LogLLM.objects.get(id=log_id)

    if log.task_type == LLMTaskType.MRC:
        question = log.question
        context = log.context
        bert_instance = HuggingfaceBERTInstance()
        inputs = bert_instance.get_tokenizer_input(question, context)
        valid_length = bert_instance.check_length(inputs)
        if valid_length is False:
            log.add_state(LogStateType.Failed)
            return

        answer = bert_instance.decode(inputs)
        log.answer = answer
        log.save()
        log.add_state(LogStateType.Succeeded)

    elif log.task_type == LLMTaskType.QA_SQL:
        question = log.question
        try:
            result = SQLChainModel().get_result(question)
        except:
            log.add_state(LogStateType.Failed)
            return
        log.answer = result
        log.save()
        log.add_state(LogStateType.Succeeded)
    elif log.task_type == LLMTaskType.QA_SEARCH:
        question = log.question
        session_id = log.session.id
        try:
            result = ChatMemoryModel(session_id=session_id).get_result(question)
        except:
            log.add_state(LogStateType.Failed)
            return
        log.answer = result
        log.save()
        log.add_state(LogStateType.Succeeded)
    else:
        log.add_state(LogStateType.Failed)
