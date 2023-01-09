from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='random_name')
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Тестовое описание группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_author = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author.force_login(self.author)

    def test_create_post_form(self):
        '''Проверка формы создания новой записи'''
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст',
                     'group': self.group.id}
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(),
                         posts_count + 1,
                         'Ошибка: поcт не добавлен.')
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertTrue(Post.objects.filter(
                        text='Текст',
                        group=self.group.id,
                        author=self.user,
                        ).exists(),
                        'Ошибка: данные не совпадают.')

    def test_edit_post_form(self):
        '''Проверка формы редактирования записи'''
        group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group2',
            description='Тестовое описание группы'
        )
        form_data = {'text': 'Текст',
                     'group': group2.id}
        self.assertEqual(
            Post.objects.count(),
            1,
            'Постов больше одного'
        )
        response = self.authorized_author.post(
            reverse('posts:post_edit', args=(self.post.pk,)),
            data=form_data,
            follow=True)
        self.assertEqual(
            Post.objects.count(),
            1,
            'Количество постов изменилось при редактировании'
        )
        post = Post.objects.latest('id')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(post.text == form_data['text'])
        self.assertTrue(post.author == self.author)
        self.assertTrue(post.group.id == form_data['group'])
        self.assertFalse(
            Post.objects.filter(
                group=self.group.id,
                text=self.post.text
            ).exists(),
            'Ошибка: данные после редактирования не изменились'
        )

    def test_nopermission_create_post(self):
        '''Проверка запрета создания поста неавторизованным пользователем'''
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст записанный в форму',
                     'group': self.group.id}
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(Post.objects.count(),
                            posts_count + 1,
                            'Неваторизованный пользователь добавил пост')
