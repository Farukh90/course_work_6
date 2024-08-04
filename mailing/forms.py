from django.forms import ModelForm, forms, BooleanField
from mailing.models import Client, Message, Mailing, MailingAttempt


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name,  fild in self.fields.items():
            if isinstance(fild, BooleanField):
                fild.widget.attrs['class']  = 'form-check-input'
            else:
                fild.widget.attrs['class'] = 'form-control'


class ClientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Client
        fields = "__all__"
        # exclude = ("views_counter", "owner")


class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = "__all__"


class MailingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Mailing
        fields = "__all__"


class MailingAttemptForm(StyleFormMixin, ModelForm):
    class Meta:
        Mailing = MailingAttempt
        fields = "__all__"


# class ProductModeratorForm(StyleFormMixin, ModelForm):
#     class Meta:
#         model = Product
#         fields = ("is_published", "description", "category")


