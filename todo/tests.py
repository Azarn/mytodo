from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Category, Todo


class DefaultCategoryTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username='1', password='2')

    def tearDown(self):
        Category.objects.all().delete()
        Todo.objects.all().delete()

    def _check_exists(self):
        return Category.objects.filter(user=self.user, name=Category.DEFAULT_NAME).exists()

    def test_default_category_getting(self):
        self.assertIsNone(Category.get_default_category(self.user))
        category = Category.get_or_create_default(self.user)
        self.assertEqual(category, Category.get_default_category(self.user))
        Category.delete_default_if_empty(self.user)
        self.assertIsNone(Category.get_default_category(self.user))

    def test_default_category_creation_deletion(self):
        self.assertFalse(self._check_exists())
        Category.get_or_create_default(self.user)
        self.assertTrue(self._check_exists())
        Category.delete_default_if_empty(self.user)
        self.assertFalse(self._check_exists())

    def test_todo_empty_category(self):
        todo = Todo.objects.create(user=self.user, text='Test todo', deadline=timezone.now())
        self.assertEqual(todo.category, Category.objects.get(user=self.user, name=Category.DEFAULT_NAME))

        test_category = Category.objects.create(user=self.user, name='Test category')
        todo.category = test_category
        todo.save()
        self.assertFalse(self._check_exists())

        todo.reset_category()
        self.assertTrue(self._check_exists())

        todo.category = test_category
        todo.save()
        self.assertFalse(self._check_exists())
        test_category.delete()
        self.assertTrue(self._check_exists())
        todo = Todo.objects.get(pk=todo.pk)
        self.assertEqual(todo.category, Category.get_default_category(todo.user))

        todo.delete()
        self.assertFalse(self._check_exists())
