from django.urls import path

from blog.apps import BlogConfig
from blog.views import (
    BlogCreateView,
    BlogListView,
    BlogDetailView,
    BlogUpdateView,
    BlogDeleteView,
)

app_name = BlogConfig.name


urlpatterns = [
    path("create/", BlogCreateView.as_view(), name="blog_create"),
    path("", BlogListView.as_view(), name="blog_list"),
    path("view/<slug:slug>/", BlogDetailView.as_view(), name="blog_detail"),
    path("edit/<slug:slug>/", BlogUpdateView.as_view(), name="blog_edit"),
    path("delete/<slug:slug>/", BlogDeleteView.as_view(), name="blog_delete"),
]
