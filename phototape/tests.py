from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from phototape.models import UserProfile, Photo


class RegisterPageTest(TestCase):

    def test_register_page(self):
        """Тест что используется нужный шаблон, код ответа 200"""
        url = reverse('register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'phototape/register.html')


class ProfileEditPageTest(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='testuser1', password='12345')
        test_user.save()
        test_user_profile = UserProfile.objects.create(city='SPb', user=test_user)
        test_user_profile.save()

    def test_profile_edit_page(self):
        """Тест что используется нужный шаблон, код ответа 200, в запросе залогиненый пользователь"""
        self.client.login(username='testuser1', password='12345')
        url = reverse('profile_edit')
        response = self.client.get(url)
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'phototape/profile_edit.html')


class UploadPhotoTest(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='testuser1', password='12345')
        test_user.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        test_user_profile2 = UserProfile.objects.create(city='SPb', user=test_user2)
        test_user_profile2.save()

    def test_upload_photo(self):
        """Тест на успешную загрузку фотографии"""
        self.client.login(username='testuser1', password='12345')
        with open('test_file/test_img.jpg', 'rb') as f:
            response = self.client.post('/upload_photo', {'photo': f})
        self.assertEqual(response.status_code, 302)

    def test_view_user_photo(self):
        """Тест на просмотр фотографий пользователя"""
        self.client.login(username='testuser2', password='12345')
        url = reverse('user_photos', args=['testuser1'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class PhotoDetailTest(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='testuser1', password='12345')
        test_user.save()
        test_user_profile = UserProfile.objects.create(city='MSC', user=test_user)
        test_user_profile.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        test_user_profile2 = UserProfile.objects.create(city='SPb', user=test_user2)
        test_user_profile2.save()
        test_user2_photo = Photo.objects.create(photo='test_file/test_img.jpg', user=test_user2,)
        test_user2_photo.save()

    def test_detail_view(self):
        """Тест на успешную загрузку детальной страницы фотографии"""
        self.client.login(username='testuser1', password='12345')
        url = reverse('photo_detail', args=[1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['user']), 'testuser1')

    def test_add_like_and_dislike(self):
        """Тест на добавление лайка и дизлайка"""
        self.client.login(username='testuser1', password='12345')
        photo = Photo.objects.get(id=1)
        url = reverse('like', args=[photo.id])
        self.client.post(url, {'username': 'testuser2'})
        self.assertEqual(photo.likes.all().count(), 1)
        self.assertEqual(photo.dislikes.all().count(), 0)
        url = reverse('dislike', args=[photo.id])
        self.client.post(url, {'username': 'testuser2'})
        self.assertEqual(photo.likes.all().count(), 0)
        self.assertEqual(photo.dislikes.all().count(), 1)


class TestFindPage(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='testuser1', password='12345')
        test_user.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

    def test_find_page(self):
        """Тест на успешный поиск по username"""
        self.client.login(username='testuser1', password='12345')
        response = self.client.get('/find', {'text': 'testuser2'})
        self.assertEqual(response.status_code, 200)
