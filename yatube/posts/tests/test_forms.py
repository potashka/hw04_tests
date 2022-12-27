from http import HTTPStatus
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание группы'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='random_name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_form(self):
        '''Проверка формы создания новой записи'''
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст',
                     'group': PostFormTests.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
                        text='Текст',
                        group=PostFormTests.group.id,
                        author=self.user
                        ).exists(),
                        'Ошибка: данные не совпадают.')
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         'Ошибка: поcт не добавлен.')

    def test_edit_post_form(self):
        '''Проверка формы редактирования записи'''
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
            group=PostFormTests.group
        )
        group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group2',
            description='Тестовое описание группы'
        )
        form_data = {'text': 'Текст',
                     'group': group2.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                group=group2.id,
                author=self.user,
                pub_date=post.pub_date).exists(),
            'Ошибка: данные не совпадают.'
        )
        self.assertNotEqual(
            post.text,
            form_data['text'],
            'Ошибка: пользователь не может изменить содержание поста.'
        )
        self.assertNotEqual(
            post.group,
            form_data['group'],
            'Ошибка: пользователь не может изменить группу поста.'
        )
