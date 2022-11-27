from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post
from django.urls import reverse

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для PostURLTests',
        )
        cls.index = reverse('posts:index')
        cls.group_list = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug}
        )
        cls.profile = reverse(
            'posts:profile', kwargs={'username': cls.post.author.username}
        )
        cls.post_detail = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.post_edit = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.post_create = reverse('posts:post_create')
        cls.public_urls = (
            (cls.index, 'posts/index.html'),
            (cls.group_list, 'posts/group_list.html'),
            (cls.profile, 'posts/profile.html'),
            (cls.post_detail, 'posts/post_detail.html'),
        )
        cls.privat_urls = (
            (cls.index, 'posts/index.html'),
            (cls.group_list, 'posts/group_list.html'),
            (cls.profile, 'posts/profile.html'),
            (cls.post_detail, 'posts/post_detail.html'),
            (cls.post_edit, 'posts/create_post.html'),
            (cls.post_create, 'posts/create_post.html'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_visible_for_all(self):
        """Проверка доступности страниц любому пользователю."""
        for address, _ in self.public_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_visible_for_authorized_client(self):
        """Проверка доступности страниц авторизованному пользователю."""
        for address, _ in self.privat_urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.privat_urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """Запрос к несуществующей странице возвращает ошибку 404."""
        responses = {
            self.guest_client.get('/unexisting_page/'),
            self.authorized_client.get('/unexisting_page/'),
        }
        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_page_404_castom_template(self):
        """Страница 404 отдаёт кастомный шаблон."""
        address = '/unexisting_page/'
        responses = {
            self.guest_client.get(address),
            self.authorized_client.get(address),
        }
        template = 'core/404.html'
        for response in responses:
            with self.subTest(response=response):
                self.assertTemplateUsed(response, template)
