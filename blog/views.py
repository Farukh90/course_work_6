from django.urls import reverse_lazy
from django.utils.text import slugify
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from blog.models import BlogPost


class BlogCreateView(CreateView):
    model = BlogPost
    fields = (
        "title",
        "content",
    )
    success_url = reverse_lazy("blog:blog_list")

    def form_valid(self, form):
        blog = form.save()
        blog.slug = slugify(blog.title)
        blog.save()
        return super().form_valid(form)


class BlogListView(ListView):
    model = BlogPost
    extra_context = {"list_name": "Блог"}

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(is_published=True)


class BlogDetailView(DetailView):
    model = BlogPost

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save()
        return obj


class BlogUpdateView(UpdateView):
    model = BlogPost
    fields = (
        "title",
        "content",
    )

    def get_success_url(self):
        return reverse_lazy("blog:blog_detail", kwargs={"slug": self.object.slug})


class BlogDeleteView(DeleteView):
    model = BlogPost

    success_url = reverse_lazy("blog:blog_list")
