from django import forms
from mywebsite.todos.models import Todo, List, todo_id_gen
from django.core.exceptions import ValidationError


# todo move these constants to their own file
EMPTY_ITEM_ERROR = "You can't have an empty list item"
DUPLICATE_ITEM_ERROR = "This item has already been entered"
TODO_TITLE_DUPE = "Can't save a todo that has the same text as title"


class GenericForm(forms.models.ModelForm):
    placeholder_text = None

    class Meta:
        model = None
        widgets = None

        fields = ("text",)
        labels = {
            "text": "",
        }
        error_messages = {
            "text": {"required": EMPTY_ITEM_ERROR},
        }

    def validate_unique(self) -> None:
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {"text": [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)


def create_widget(placeholder_text, extra_attr: dict = None):
    attrs = {
        "placeholder": f"{placeholder_text}",
        "class": "form-control input-lg",
    }
    if extra_attr:
        attrs = attrs | extra_attr
    return {"text": forms.TextInput(attrs=attrs)}


class TodoForm(GenericForm):

    def __init__(self, for_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.list = for_list
        # self.fields["text"].validators.append(validate_unique)

    class Meta(GenericForm.Meta):
        model = Todo
        placeholder_text = "Enter a todo"
        widgets = create_widget(placeholder_text)

    def save(self, owner, pk):
        if owner and pk:
            return Todo.objects.create(
                text=self.cleaned_data["text"],
                list=owner.list_set.get(id=pk),
                todo_id=todo_id_gen(),
            )

    def validate_unique(self) -> None:
        try:
            val = self.data.get("text")
            todos_for_list = list(self.instance.list.todo_set.all())
            if val == todos_for_list[0].text:
                raise ValidationError(TODO_TITLE_DUPE)
            for todo in todos_for_list[1:]:
                if todo.text == val:
                    raise ValidationError(DUPLICATE_ITEM_ERROR)
        except ValidationError as e:
            self._update_errors(e)


class ListForm(GenericForm):
    def __init__(self, queryset=None, *args, **kwargs):
        self.queryset = queryset
        super().__init__(*args, **kwargs)

    class Meta(GenericForm.Meta):
        model = Todo
        widgets = create_widget("Enter a title for list. Press enter to submit.")

    def save(self, owner):
        if owner:
            return List.create_new(text=self.cleaned_data["text"], owner=owner)

    def validate_unique(self) -> None:
        try:
            val = self.data.get("text")
            tmp_list = list(self.queryset)
            all_lists_name = []
            for list_obj in tmp_list:
                try:
                    if list_obj.name:
                        all_lists_name.append(list_obj.name)
                except AttributeError as e:
                    """list_obj does not yet exist and thus does not have name"""
                    continue

            if val in all_lists_name:
                raise ValidationError(DUPLICATE_ITEM_ERROR)
        except ValidationError as e:
            self._update_errors(e)


class EditForm(GenericForm):
    class Meta(GenericForm.Meta):
        model = Todo
        widgets = create_widget("Enter a new title", extra_attr={"id": "edit-form"})


class EditTodoForm(GenericForm):
    class Meta(GenericForm.Meta):
        model = Todo
        widgets = create_widget("Edit Todo entry", extra_attr={"id": "edit-todo-form"})
