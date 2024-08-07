from django.db import models
from django.utils.text import slugify

NULLABLE = {"blank": True, "null": True}


class BlogPost(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.CharField(max_length=200, unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="Содержание", blank=True)
    preview_image = models.ImageField(
        upload_to="blog/preview", verbose_name="Изображение превью", **NULLABLE
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=True, verbose_name="Признак публикации")
    views_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество просмотров"
    )

    class Meta:
        verbose_name = "Пост в блоге"
        verbose_name_plural = "Посты в блоге"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
