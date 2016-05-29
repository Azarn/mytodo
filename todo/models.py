from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html


def validate_color(value):
    try:
        int(value, 16)
    except ValueError:
        raise ValidationError('{0} is not a hex color!'.format(value))


class Tag(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=64, db_index=True)
    color = models.CharField(max_length=6, validators=[validate_color])

    def colored_name(self):
        return format_html('<span style="color: #{};">{}</span>', self.color, self.name)
    colored_name.admin_order_field = 'name'

    def __str__(self):
        return self.name


class Category(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=256, db_index=True)

    def __str__(self):
        return self.name


class Todo(models.Model):
    user = models.ForeignKey(User)
    category = models.ForeignKey(Category)
    tags = models.ManyToManyField(Tag, blank=True)
    text = models.CharField(max_length=256, db_index=True)
    is_done = models.BooleanField(default=False, db_index=True)
    deadline = models.DateTimeField(blank=True, db_index=True)
