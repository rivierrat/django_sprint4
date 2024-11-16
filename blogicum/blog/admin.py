from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Category, Location, Post


admin.site.empty_value_display = 'Не задано'

admin.site.unregister(Group)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'created_at', 'pub_date', 'is_published',
                    'category', 'location',)
    list_editable = ('is_published', 'pub_date', 'category', 'location',)
    list_display_links = ('title', )


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
