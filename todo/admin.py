from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as OldUserAdmin

from .models import Todo, Category, Tag, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserAdmin(OldUserAdmin):
    inlines = (ProfileInline, )


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class MembershipInline(admin.TabularInline):
    model = Todo.tags.through

    def get_formset(self, request, obj=None, **kwargs):
        request.saved_user_pk = obj.user.pk
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'tag':
            kwargs['queryset'] = Tag.objects.filter(user__pk=request.saved_user_pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TodoAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user__pk=self.instance.user.pk)


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    form = TodoAdminForm
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

