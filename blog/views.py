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
from blog.forms import BlogPostForm  # Импортируйте вашу форму


class BlogCreateView(CreateView):
    model = BlogPost
    form_class = BlogPostForm
    success_url = reverse_lazy("blog:blog_list")

    def form_valid(self, form):
        blog = form.save(commit=False)
        if not blog.slug:
            base_slug = slugify(blog.title)
            slug = base_slug
            num = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            blog.slug = slug
        blog.save()
        return super().form_valid(form)


class BlogListView(ListView):
    model = BlogPost
    template_name = "blog/blogpost_list.html"  # Укажите ваш шаблон
    context_object_name = "blogpost_list"
    form_class = BlogPostForm  # Если используете форму
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
    form_class = BlogPostForm  # Используйте вашу форму

    def get_success_url(self):
        return reverse_lazy("blog:blog_detail", kwargs={"slug": self.object.slug})


class BlogDeleteView(DeleteView):
    model = BlogPost
    success_url = reverse_lazy("blog:blog_list")
