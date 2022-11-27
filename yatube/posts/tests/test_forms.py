import shutil
import tempfile
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.form_data = {
            'text': 'Текст из формы',
            'group': cls.group.id,
        }
        cls.profile = reverse(
            'posts:profile', kwargs={'username': cls.user.username}
        )
        cls.post_create = reverse('posts:post_create')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_in_db(self):
        """Валидная форма создает пост в базе данных."""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        created_post = Post.objects.get(id=self.group.id)
        self.assertRedirects(response, self.profile)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(created_post.text, self.form_data['text'])
        self.assertEqual(created_post.group.title, 'Тестовая группа')

    def test_create_post_with_picture_in_db(self):
        """Валидная форма создает пост c картинкой в базе данных."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            self.post_create,
            data=form_data,
            follow=True
        )
        created_post = Post.objects.get(id=self.group.id)
        self.assertRedirects(response, self.profile)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(created_post.text, self.form_data['text'])
        self.assertEqual(created_post.group.title, 'Тестовая группа')

    def test_edit_post_in_db(self):
        """При отправке валидной формы происходит изменение поста в БД."""
        self.authorized_client.post(
            self.post_create,
            data=self.form_data,
            follow=True
        )
        created_post = Post.objects.get(id=self.group.id)
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Изменяем текст в форме',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=({created_post.id})),
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.get(id=created_post.id)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': edit_post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.title, 'Тестовая группа')

    def test_comment_on_post_page(self):
        """После отправки комментарий появляется на странице поста."""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            author=self.user,
            text="Тестовая пост",
            group=self.group,
        )
        form_data = {'text': 'Тестовый комментарий'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        created_comment = Comment.objects.get(id=post.id)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id}
        ))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(created_comment.text, 'Тестовый комментарий')

    def test_add_comment_guest(self):
        """Гость не может писать комментарии."""
        comments_count = Comment.objects.count()
        post = Post.objects.create(
            author=self.user,
            text="Тестовая пост",
            group=self.group,
        )
        form_data = {'text': 'Тестовый комментарий'}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, ('/auth/login/?next=/posts/1/comment/')
        )
        self.assertEqual(Comment.objects.count(), comments_count)
