from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
# from django.utils import timezone
from rest_framework.authtoken.models import Token
from timezone_field.fields import TimeZoneField


def validate_color(value):
    try:
        int(value, 16)
    except ValueError:
        raise ValidationError('{0} is not a hex color!'.format(value))


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    timezone = TimeZoneField(default=settings.TIME_ZONE)


class Tag(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=64, db_index=True)
    color = models.CharField(max_length=6, validators=[validate_color])

    def colored_name(self):
        return format_html('<span style="color: #{};">{}</span>', self.color, self.name)
    colored_name.admin_order_field = 'name'

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['user', 'name']


class Category(models.Model):
    DEFAULT_NAME = '(default category)'

    user = models.ForeignKey(User)
    name = models.CharField(max_length=256, db_index=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_create_default(cls, user):
        return cls.objects.get_or_create(user=user, name=cls.DEFAULT_NAME)[0]

    @classmethod
    def get_default_category(cls, user):
        try:
            return cls.objects.get(user=user, name=cls.DEFAULT_NAME)
        except ObjectDoesNotExist:
            return None

    @classmethod
    def delete_default_if_empty(cls, user):
        category = cls.get_default_category(user)
        if category and not category.todo_set.exists():
            category.delete()

    class Meta:
        unique_together = ['user', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Todo(models.Model):
    user = models.ForeignKey(User)
    category = models.ForeignKey(Category, blank=True, on_delete=models.DO_NOTHING)
    tags = models.ManyToManyField(Tag, blank=True)
    text = models.CharField(max_length=256, db_index=True)
    is_done = models.BooleanField(default=False, db_index=True)
    deadline = models.DateTimeField(null=True, blank=True, db_index=True)

    def mark_done(self, new_state):
        self.is_done = new_state
        self.save()

    def reset_category(self):
        self.category_id = None
        self.save()

    def save(self, *args, **kwargs):
        if self.category_id is None:
            self.category = Category.get_or_create_default(self.user)
        super().save(*args, **kwargs)


@receiver(pre_delete, sender=Category)
def set_default_category_to_todo_set(sender, instance, **kwargs):
    for todo in instance.todo_set.all():
        todo.reset_category()


@receiver((post_delete, post_save), sender=Todo)
def delete_default_category_if_empty(sender, instance=None, **kwargs):
    Category.delete_default_if_empty(instance.user)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
