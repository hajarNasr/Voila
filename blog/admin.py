from django.contrib import admin
from .models import Post, Category,Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # automatically create the post's slug from its title
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Category)
admin.site.register(Comment)
