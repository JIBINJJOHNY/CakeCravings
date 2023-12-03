from django.db import models
from django.utils.text import slugify
from cloudinary.models import CloudinaryField
from decimal import Decimal
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Category Name',
        help_text='Format: required, max_length=100'
    )
    slug = models.SlugField(
        max_length=150,
        unique=True,
        verbose_name='Category Slug',
        help_text='Format: required, max_length=150'
    )
    is_active = models.BooleanField(default=False)
    image = CloudinaryField(folder='category', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def category_image(self):
        return mark_safe(f'<img src="{self.image.url}" width="50" height="50" />')

    def __str__(self):
        return self.name
