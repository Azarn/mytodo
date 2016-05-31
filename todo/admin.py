from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import Todo, Category, Tag, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(UserAdmin):
    inlines = (ProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class MembershipInline(admin.TabularInline):
    model = Todo.tags.through


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    date_hierarchy = 'deadline'
    list_display = ('text', 'category', 'user', 'deadline', 'is_done')
    list_editable = ('is_done',)
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
        ('is_done', admin.BooleanFieldListFilter),
    )
    search_fields = ('text', 'user__username', 'category__name',)
    inlines = [
        MembershipInline
    ]
    exclude = ('tags', )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name', 'user')
    list_display = ('name', 'user')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    fields = ('name', 'user', 'color')
    list_display = ('colored_name', 'user', 'color')
    list_filter = (
        ('user', admin.RelatedOnlyFieldListFilter),
    )

