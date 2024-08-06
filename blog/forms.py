from django.forms import ModelForm
from mailing.forms import StyleFormMixin
from blog.models import BlogPost


class BlogPostForm(StyleFormMixin, ModelForm):
    class Meta:
        model = BlogPost
        fields = "__all__"
