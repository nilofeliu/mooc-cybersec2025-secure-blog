from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q
from .models import Post, Category, Tag, Comment, Newsletter


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(post_count=Count('posts', filter=Q(posts__is_published=True, posts__deleted_at__isnull=True)))

    def post_count(self, obj):
        return obj.post_count
    post_count.admin_order_field = 'post_count'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_link', 'is_published', 'created_at', 'deleted_at')
    list_filter = ('is_published', 'deleted_at', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    actions = ['soft_delete_posts']

    def author_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = 'Author'
    author_link.admin_order_field = 'author'

    def soft_delete_posts(self, request, queryset):
        count = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{count} post(s) were soft-deleted.")
    soft_delete_posts.short_description = "Soft delete selected posts"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('short_content', 'author_link', 'post_link', 'created_at', 'deleted_at')
    list_filter = ('deleted_at', 'author', 'post')
    search_fields = ('content',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')
    actions = ['soft_delete_comments']

    def author_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = 'Author'

    def post_link(self, obj):
        url = reverse('admin:blog_post_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_link.short_description = 'Post'

    def short_content(self, obj):
        return (obj.content[:75] + '...') if len(obj.content) > 75 else obj.content
    short_content.short_description = 'Content'

    def soft_delete_comments(self, request, queryset):
        count = queryset.update(deleted_at=timezone.now())
        self.message_user(request, f"{count} comment(s) were soft-deleted.")
    soft_delete_comments.short_description = "Soft delete selected comments"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'post_count')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(post_count=Count('posts', filter=Q(posts__is_published=True, posts__deleted_at__isnull=True)))

    def post_count(self, obj):
        return obj.post_count
    post_count.admin_order_field = 'post_count'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
