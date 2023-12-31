from django.db import models
from django.db.models import TextChoices


class LogStateType(TextChoices):
    Pending = 'PENDING'
    Running = 'RUNNING'
    Succeeded = 'SUCCEEDED'
    Failed = 'FAILED'


class LLMTaskType(TextChoices):
    QA_SQL = 'sql'
    QA_SEARCH = 'search'
    MRC = 'mrc'


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_datetime = models.DateTimeField(verbose_name="생성일시", auto_now_add=True)

    objects = models.Manager()

    class Meta:
        abstract = True


class Session(BaseModel):
    params = models.JSONField(default=dict)


class LogLLM(BaseModel):
    task_type = models.CharField(max_length=32, null=True, default=None)

    question = models.TextField()
    context = models.TextField(null=True, default=None)
    answer = models.TextField(null=True, default=None)
    session = models.ForeignKey(Session, related_name='logs', null=True, on_delete=models.CASCADE)

    def add_state(self, state: LogStateType):
        return LogLLMState.objects.create(log=self, state=state)


class LogLLMState(BaseModel):
    log = models.ForeignKey(LogLLM, related_name='states', on_delete=models.CASCADE)
    state = models.CharField(max_length=20)


class Stock(BaseModel):
    symbol = models.CharField(max_length=32)
    name = models.CharField(max_length=64, null=True, default=None)
    date = models.DateTimeField(verbose_name="시세 날짜")
    highest_price = models.FloatField(default=0)
    lowest_price = models.FloatField(default=0)
    close_price = models.FloatField(default=0)