from django import forms
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from posts.forms import PostForm

NUM_POSTS_PAG_TEST = settings.NUM_POSTS_PAG_TEST

QUANTITY_OF_POSTS = settings.QUANTITY_OF_POSTS


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='random_name')
        cls.author = cls.user
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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def sample_context_test_func(self, context, post=False):
        """Шаблон фнукции для тестирования контекста"""
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page_obj', context)
            post = context['page_obj'][0]
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.group, self.post.group)

    def test_index_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        self.sample_context_test_func(response.context)

    def test_group_list_shows_correct_context(self):
        """Шаблон группы сформирован с правильным контектсом"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    args=(self.group.slug,))
        )
        self.assertEqual(
            response.context['group'].slug,
            self.group.slug
        )
        self.sample_context_test_func(response.context)

    def test_profile_shows_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    args=(self.user.username,))
        )
        self.assertEqual(
            response.context['author']
            .username,
            self.user.username,
            'Ошибка: шаблон сформирован с неправильным контекстом'
        )
        self.sample_context_test_func(response.context)

    def test_post_detail_shows_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=(self.post.pk,))
        )
        self.sample_context_test_func(response.context, post=True)

    def test_create_edit_post_shows_correct_context(self):
        """Шаблоны post_create и eidt_post сформированы
            с правильным контекстом"""
        pages = (
            ('posts:post_create', None,),
            ('posts:post_edit', (self.post.pk,),),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for page, args in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(reverse(page, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value)
                        self.assertIsInstance(form_field, expected)

    def test_post_another_group_conflict(self):
        """Пост не попал в другую группу"""
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-group2',
            description='Тестовое описание группы',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', args=(group2.slug,))
        )
        self.assertEqual(len(response.context['page_obj']), 0)
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text='Тестовый пост ',
            author=self.user,
            group=group2)
        self.assertTrue(post.group, 'У поста есть группа')
        group1 = Post.objects.filter(group=self.group).count()
        group2 = Post.objects.filter(group=self.group).count()
        self.assertEqual(group1, posts_count, 'Пост попал в первую группу')
        self.assertEqual(group2, 1, 'Нет поста')
        self.assertNotEqual(self.group, post.group, 'Другая группа')


class PaginatorViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='random_name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        posts = []
        for post in range(NUM_POSTS_PAG_TEST):
            posts.append(
                Post(text=f'Тестовый пост {post}',
                     group=self.group,
                     author=self.user)
            )
        Post.objects.bulk_create(posts)

    def test__page_contains__records(self):
        '''Проверка количества постов на странице'''
        page_urls = (
            ('posts:main_page', None),
            ('posts:profile',
                (self.user.username,)),
            ('posts:group_list',
                (self.group.slug,)),
        )
        pages = (
            ('?page=1', 10),
            ('?page=2', 5),
        )
        for url, args in page_urls:
            with self.subTest():
                for page, count in pages:
                    with self.subTest():
                        response = self.client.get(
                            reverse(url, args=args)
                            + page
                        )
                        self.assertEqual(
                            len(response.context['page_obj']),
                            count,
                            'Ошибка:неверное количество постов.'
                        )
