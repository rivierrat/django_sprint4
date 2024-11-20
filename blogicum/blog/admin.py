from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from . import settings
from .models import Category, Comment, Location, Post


admin.site.empty_value_display = 'Не задано'

admin.site.unregister(Group)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'trim_text', 'created_at', 'pub_date',
                    'is_published', 'category', 'location', 'image_tag',)
    list_editable = ('is_published', 'pub_date', 'category', 'location',)
    list_display_links = ('title', 'image_tag',)
    readonly_fields = ('image_tag',)

    @admin.display(description='Превью изображения')
    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src={obj.image.url} '
                             f'{settings.ADMIN_IMAGE_PREVIEW_SIZE}>')

    @admin.display(description='Текст')
    # Для поля 'text' создаём превью заданной длины:
    def trim_text(self, obj):
        return u"%s..." % (obj.text[:settings.ADMIN_POST_PREVIEV_LENGTH],)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'posts_count',)
    list_editable = ('is_published', 'title', )
    list_display_links = ('posts_count',)

    @admin.display(description='Постов в категории')
    def posts_count(self, obj):
        return obj.posts.count()


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'posts_count',)
    list_editable = ('is_published', 'name',)
    list_display_links = ('posts_count', )

    @admin.display(description='Постов в локации')
    def posts_count(self, obj):
        return obj.posts.count()


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('trim_text', 'author', 'created_at', 'post',)
    list_display_links = ('trim_text', 'author', 'post')

    @admin.display(description='Комментарий')
    # Для поля 'text' создаём превью заданной длины:
    def trim_text(self, obj):
        return u"%s..." % (obj.text[:settings.ADMIN_COMMENT_PREVIEV_LENGTH],)
