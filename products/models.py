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

class Tag(models.Model):
    """Cake Cravings Tag model"""
    name = models.CharField(
        max_length=100,
        null=False,
        unique=True,
        blank=False,
        verbose_name='Tag Name',
        help_text='The name of the tag (e.g., "Offer 10%", "New", "International Shipping").'
    )
    slug = models.SlugField(
        max_length=150,
        null=False,
        unique=True,
        blank=False,
        verbose_name='Tag Slug',
        help_text='A slugified version of the tag name (e.g., "offer-10", "new", "international-shipping").'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Is Active',
        help_text='Is this tag currently active and displayed on the website?'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at',
        help_text='The date and time when this tag was created.'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at',
        help_text='The date and time when this tag was last updated.'
    )

    class Meta:
        """Meta class for Cake Cravings Tag model"""
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']

    def __str__(self):
        """String representation of Cake Cravings Tag model"""
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    @classmethod
    def get_active_tags(cls):
        """Get active tags"""
        return cls.objects.filter(is_active=True)

    @classmethod
    def get_not_active_tags(cls):
        """Get not active tags"""
        return cls.objects.filter(is_active=False)
