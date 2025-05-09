import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TodosConfig(AppConfig):
    name = "mywebsite.todos"
    verbose_name = _("Todos")

    def ready(self):
        with contextlib.suppress(ImportError):
            import mywebsite.todos.signals
