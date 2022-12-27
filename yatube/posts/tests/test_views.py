from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django import forms

from ..models import Group, Post

User = get_user_model()

QUANTITY_OF_POSTS = settings.QUANTITY_OF_POSTS


class PostViewsTests(TestCase):
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
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = PostViewsTests.user 
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:main_page'):
                'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug':
                            f'{PostViewsTests.group.slug}'}):
                'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.user.username}'}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            self.post.pk}): 'posts/create_post.html'
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                error = f'Ошибка: {reverse_name} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error)

    def test_index_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        post_text_0 = {response.context['post'].text: self.post.text,
                       response.context['post'].group: PostViewsTests.group,
                       response.context['post'].author: self.user.username}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_group_list_shows_correct_context(self):
        """Шаблон группы сформирован с правильным контектсом"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{PostViewsTests.group.slug}'})
        )
        post_text_0 = {response.context['group'].title:
                       'Тестовая группа',
                       response.context['group'].slug:
                       PostViewsTests.group.slug}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username':
                            f'{self.user.username}'}))
        self.assertEqual(
            response.context['author']
            .username,
            self.user.username,
            'Ошибка: шаблон сформирован с неправильным контекстом'
        )
        self.assertEqual(self.post, response.context['page_obj'][0],
                         'Ошибка: шаблон сформирован с неправильным контекстом'
                         )

    def test_post_detail_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        post_text_0 = {response.context['post'].text: 'Тестовый пост',
                       response.context['post'].group: PostViewsTests.group,
                       response.context['post'].author: self.user.username}
        for value, expected in post_text_0.items():
            self.assertEqual(post_text_0[value], expected)

    def test_create_post_shows_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_another_group_conflict(self):
        """Пост не попал в другую группу"""
        response_index = self.authorized_client.get(
            reverse('posts:main_page'))
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{PostViewsTests.group.slug}'})
        )
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}))
        self.assertIn(self.post, response_index.context['page_obj'],
                      'Ошибка: тестового поста нет на главной странице')
        self.assertIn(self.post, response_group.context['page_obj'],
                      'Ошибка: тестового поста нет в группе')
        self.assertIn(self.post, response_profile.context['page_obj'],
                      'Ошибка: тестового поста нет в профиле пользователя')


class PaginatorViewsTest(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='random_name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        posts = []
        for i in range(QUANTITY_OF_POSTS):
            posts.append(
                Post(text=f'Тестовый пост {i}',
                     group=self.group,
                     author=self.user)
            )
        Post.objects.bulk_create(posts)

    def test_first_page_contains_ten_records(self):
        '''Проверка количества постов на странице'''
        pages = (
            reverse('posts:main_page'),
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}),
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}))
        for page in pages:
            response = self.client.get(page)
            self.assertEqual(
                len(response.context['page_obj']),
                QUANTITY_OF_POSTS,
                'Ошибка:неверное количество постов.'
            )
