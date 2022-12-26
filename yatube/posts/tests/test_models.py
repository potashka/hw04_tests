from django.contrib.auth import get_user_model
from django.test import TestCase

from django.conf import settings


from ..models import Group, Post

User = get_user_model()

LEN_OF_POSTS = settings.LEN_OF_POSTS


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='random_name')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )


    def test_model_post_have_correct_object_names(self):
        """Проверяем, что у модели Пост корректно работает __str__."""
        post = PostModelTest.post
        error_name = f"Вывод не имеет {LEN_OF_POSTS} символов"
        self.assertEqual(self.post.__str__(),
                         post.text[:LEN_OF_POSTS],
                         error_name)
    
    def test_model_group_have_correct_object_names(self):
        """Проверяем, что у модели Группа корректно работает __str__."""
        group = PostModelTest.group
        error_name = f"Название {group.title} не совпадает с моделью {self.group.__str__()}"
        self.assertEqual(self.group.__str__(),
                         group.title,
                         error_name)
 
    def test_title_label(self):
        '''Проверка заполнения verbose_name в модели Post'''
        post = PostModelTest.post
        field_verboses = {'text': 'Текст поста',
                          'pub_date': 'Дата публикации',
                          'group': 'Группа',
                          'author': 'Автор'}
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value, error_name)
    
    def test_title_help_text(self):
        '''Проверка заполнения help_text в модели Пост'''
        post = PostModelTest.post
        field_help_texts = {'text': 'Введите текст поста',
                            'group': 'Группа, к которой будет относиться пост'}
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                error_name = f'Поле {field} ожидало значение {expected_value}'
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value, error_name)
