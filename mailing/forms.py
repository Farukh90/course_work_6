from django.forms import ModelForm, BooleanField
from mailing.models import Client, Message, Mailing, MailingAttempt


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class ClientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Client
        exclude = ("owner",)

    def save(self, commit=True, owner=None):
        instance = super().save(commit=False)
        if owner:
            instance.owner = owner
        if commit:
            instance.save()
        return instance


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        exclude = ("owner",)

    def save(self, commit=True, owner=None):
        instance = super().save(commit=False)
        if owner:
            instance.owner = owner
        if commit:
            instance.save()
        return instance


class MailingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        exclude = ("owner",)

    def save(self, commit=True, owner=None):
        instance = super().save(commit=False)
        if owner:
            instance.owner = owner
        if commit:
            instance.save()
        return instance


class MailingModeratorForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        fields = ("status",)

    def save(self, commit=True, owner=None):
        instance = super().save(commit=False)
        if owner:
            instance.owner = owner
        if commit:
            instance.save()
        return instance


class MailingAttemptForm(StyleFormMixin, ModelForm):
    class Meta:
        model = MailingAttempt
        fields = "__all__"
