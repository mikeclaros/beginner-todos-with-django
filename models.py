from django.db import models
from django.urls import reverse
from django.conf import settings


def todo_id_gen():
    import uuid

    return int(uuid.uuid1())


class List(models.Model):
    @property
    def name(self):
        return self.todo_set.first().text

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE
    )

    @staticmethod
    def create_new(text, owner):
        import uuid

        list_ = List.objects.create(owner=owner)
        Todo.objects.create(text=text, list=list_, todo_id=todo_id_gen())
        return list_

    def __str__(self) -> str:
        return str(self.todo_set.first().text)


class Todo(models.Model):
    text = models.TextField(max_length=140, default="")
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    todo_id = models.CharField(default="")

    class Meta:
        ordering = ("id",)
        unique_together = ("list", "text")

    def __str__(self) -> str:
        return str(self.text)
