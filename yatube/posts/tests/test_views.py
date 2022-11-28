import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow
from posts.forms import PostForm

User = get_user_model()

POST_ON_PAGE = 10
POST_ON_ANOTER_PAGE = 3

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPageViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )
        cls.small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif", content=cls.small_gif, content_type="image/gif"
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для PostPageViewsTests',
            group=cls.group,
            image=cls.uploaded
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
        cls.add_comment = reverse(
            'posts:add_comment', kwargs={'post_id': cls.post.id}
        )
        cls.templates_pages_names = (
            (cls.index, 'posts/index.html'),
            (cls.group_list, 'posts/group_list.html'),
            (cls.profile, 'posts/profile.html'),
            (cls.post_detail, 'posts/post_detail.html'),
            (cls.post_edit, 'posts/create_post.html'),
            (cls.post_create, 'posts/create_post.html'),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.index)
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_text_0, 'Тестовый пост для PostPageViewsTests')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.group_list)
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_group_slug_0 = first_object.group.slug
        post_group_description_0 = first_object.group.description
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_text_0, 'Тестовый пост для PostPageViewsTests')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_group_slug_0, 'test-slug')
        self.assertEqual(post_group_description_0, 'Тестовое описание')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.profile)
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        post_group_slug_0 = first_object.group.slug
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_text_0, 'Тестовый пост для PostPageViewsTests')
        self.assertEqual(post_group_0, 'Тестовая группа')
        self.assertEqual(post_group_slug_0, 'test-slug')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_detail)
        first_object = response.context['post']
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'TestUser')
        self.assertEqual(post_text_0, 'Тестовый пост для PostPageViewsTests')
        self.assertEqual(post_group_0, 'Тестовая группа')

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_edit)
        self.assertTrue(response.context.get('is_edit'))
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.post_create)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_with_correct_group_on_page(self):
        """Посты с присвоенной группой отображаются на страницах."""
        response_list = (
            self.index,
            self.group_list,
            self.profile,
        )
        for reverse_name in response_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(self.post, response.context['page_obj'])

    def test_post_with_not_correct_group_on_group_list(self):
        """Пост не попал в группу, для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_1.slug})
        )
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_images_on_pages(self):
        """Картинка передается на страницы index, profile, group_list."""
        response_list = {
            self.index,
            self.group_list,
            self.profile,
        }
        for reverse_name in response_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.context['page_obj'][0].image, self.post.image
                )

    def test_images_on_post_detail_pages(self):
        """Картинка передается на страницу post_detail."""
        response = self.authorized_client.get(self.post_detail)
        self.assertEqual(response.context['post'].image, self.post.image)

    def test_check_cache(self):
        """Проверка кеша."""
        response_1 = self.guest_client.get(self.index)
        res_1 = response_1.content
        Post.objects.get(id=1).delete()
        response_2 = self.guest_client.get(self.index)
        res_2 = response_2.content
        self.assertEqual(res_1, res_2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post_list = []
        for i in range(0, 13):
            cls.post_list.append(
                Post.objects.create(
                    author=cls.user,
                    text=f'Тестовый пост - {i} для PostViewsTests',
                    group=cls.group,
                )
            )
        cls.index = reverse('posts:index')
        cls.group_list = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug}
        )
        cls.profile = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        """Проверка пагинатора на первой странице."""
        response_list = {
            self.index: POST_ON_PAGE,
            self.group_list: POST_ON_PAGE,
            self.profile: POST_ON_PAGE,
        }
        for reverse_name, posts in response_list.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), posts)

    def test_second_page_contains_three_records(self):
        """Проверка пагинатора на второй странице."""
        response_list = {
            self.index + '?page=2': POST_ON_ANOTER_PAGE,
            self.group_list + '?page=2': POST_ON_ANOTER_PAGE,
            self.profile + '?page=2': POST_ON_ANOTER_PAGE,
        }
        for reverse_name, posts in response_list.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), posts)


class TestFollowViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.post_follower = User.objects.create(
            username='post_follower',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.post_author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.post_author)
        self.follower_client = Client()
        self.follower_client.force_login(self.post_follower)

    def test_follow_on_user(self):
        """Проверка подписки на пользователя."""
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.post_author}))
        follow = Follow.objects.get(id=self.post_author.id)
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertEqual(follow.author_id, self.post_author.id)
        self.assertEqual(follow.user_id, self.post_follower.id)

    def test_unfollow_on_user(self):
        """Проверка отписки от пользователя."""
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_author)
        count_follow = Follow.objects.count()
        self.follower_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.post_author}))
        self.assertEqual(Follow.objects.count(), count_follow - 1)

    def test_follow_on_authors(self):
        """Проверка записей у тех кто подписан."""
        Follow.objects.create(
            user=self.post_follower,
            author=self.post_author)
        response = self.follower_client.get(
            reverse('posts:follow_index'))
        self.assertIn(self.post, response.context['page_obj'].object_list)

    def test_notfollow_on_authors(self):
        """Проверка записей у тех кто не подписан."""
        response = self.author_client.get(
            reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context['page_obj'].object_list)
