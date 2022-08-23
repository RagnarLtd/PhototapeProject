from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.forms import HiddenInput
from django.shortcuts import render, redirect
from django.views import View, generic

from PetProject import settings
from phototape.forms import UserForm, ProfileForm, UploadRecordsFrom, CommentForm, SingUpForm
from phototape.models import UserProfile, Photo, PhotoComment


class UserRegisterFormView(View):
    """
    Регистрация пользователя с отправкой приветственного письма на почту
    """
    def get(self, request):
        form = SingUpForm()
        return render(request, 'phototape/register.html', context={'form': form})

    def post(self, request):
        form = SingUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            # Welcome Email
            subject = 'Welcome to Phototape'
            message = 'Hello ' + username + '! \n' + 'Welcome to Phototape! \n Thank you for visiting our website!'
            from_email = settings.EMAIL_HOST_USER
            to_list = [form.cleaned_data.get('email')]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            return redirect('/profile')
        else:
            form = SingUpForm()
        return render(request, 'phototape/register.html', context={'form': form})


class MyLoginView(LoginView):
    template_name = 'phototape/login.html'


class MyLogoutView(LogoutView):
    next_page = 'main'


class MainPageView(View):
    """ Вывод фотографий всех пользователей, на которых подписан зарегестрированный пользователь"""
    def get(self, request):
        if request.user.is_authenticated:
            profile = UserProfile.objects.get(user_id=request.user.id)
            photos = Photo.objects.filter(user__in=profile.subscribes.all())
            return render(request, 'phototape/main.html', context={'photos': photos})
        return render(request, 'phototape/main.html')


class UserFormView(View):
    """
    Отображение информации по профилю зарегестрированного пользователя
    """
    def get(self, request):
        if request.user.is_authenticated:
            try:
                return render(request, 'phototape/profile.html')
            except:
                UserProfile.objects.create(user_id=request.user.id)
                return render(request, 'phototape/profile.html')


class UserProfileEditFormView(View):
    """
    Редактирование профиля зарегестрированного пользователя
    """
    def get(self, request):
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            user_form = UserForm(instance=user)
            user_form.fields['username'].widget = HiddenInput()
            try:
                profile = UserProfile.objects.get(user_id=request.user.id)
            except:
                profile = None
            profile_form = ProfileForm(instance=profile)
            return render(request, 'phototape/profile_edit.html', context={'user_form': user_form,
                                                                           'profile_form': profile_form})
        return render(request, 'phototape/profile_edit.html')

    def post(self, request):
        user = User.objects.get(id=request.user.id)
        user_form = UserForm(request.POST, instance=user)
        user_form.fields['username'].widget = HiddenInput()
        try:
            profile = UserProfile.objects.get(user_id=request.user.id)
        except:
            profile = None
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user.save()
            if profile is not None:
                profile.save()
            else:
                UserProfile.objects.create(**profile_form.cleaned_data, user_id=request.user.id)
        return render(request, 'phototape/profile_edit.html', context={'user_form': user_form,
                                                                       'profile_form': profile_form,
                                                                       })


class UploadPhotoFormView(View):
    """
    Загрузка фоторграфии
    """
    def get(self, request):
        upload_photo_form = UploadRecordsFrom()
        return render(request, 'phototape/upload_photo.html', context={'upload_photo_form': upload_photo_form})

    def post(self, request):
        upload_photo_form = UploadRecordsFrom(request.POST, request.FILES)
        if upload_photo_form.is_valid():
            Photo.objects.create(**upload_photo_form.cleaned_data, user_id=request.user.id)
        return HttpResponseRedirect('profile/')


class UserPhotosView(View):
    """
    Просмотр фотографий определенного пользователя
    """
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username=self.kwargs['username'])
        photos = Photo.objects.filter(user=user)
        req_user = UserProfile.objects.get(user_id=request.user.id)
        subscribe = False
        for sub in req_user.subscribes.all():
            if sub == user:
                subscribe = True
                break
        return render(request, 'phototape/user_photo_view.html', context={'photos': photos,
                                                                          'username': self.kwargs['username'],
                                                                          'subscribe': subscribe})


class AddLike(LoginRequiredMixin, View):
    """
    Добавление лайка
    """
    def post(self, request, pk, *args, **kwargs):
        photo = Photo.objects.get(pk=pk)
        is_dislike = False
        for dislike in photo.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if is_dislike:
            photo.dislikes.remove(request.user)
        is_like = False
        for like in photo.likes.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:
            photo.likes.add(request.user)
        if is_like:
            photo.likes.remove(request.user)
        return HttpResponseRedirect(f"/{request.POST['username']}")


class AddDislike(LoginRequiredMixin, View):
    """
    Добавление дизлайка
    """
    def post(self, request, pk, *args, **kwargs):
        photo = Photo.objects.get(pk=pk)
        is_like = False
        for like in photo.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            photo.likes.remove(request.user)
        is_dislike = False
        for dislike in photo.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            photo.dislikes.add(request.user)
        if is_dislike:
            photo.dislikes.remove(request.user)
        return HttpResponseRedirect(f"/{request.POST['username']}")


class PhotoDeatidView(generic.DetailView):
    """
    Просмотр фотографии с комментариями
    """
    model = Photo

    def get(self, request, *args, **kwargs):
        comment_form = CommentForm()
        if request.user.is_authenticated:
            comment_form.fields['name'].widget = HiddenInput()
        photo = Photo.objects.get(id=self.kwargs['pk'])
        comments = PhotoComment.objects.filter(photo=self.kwargs['pk'])
        username = photo.user.username
        return render(request, 'phototape/photo_detail_view.html', context={'photo': photo,
                                                                            'comments': comments,
                                                                            'comment_form': comment_form,
                                                                            'username': username})

    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.cleaned_data['name'] = request.user.username
        photo = Photo.objects.get(id=self.kwargs['pk'])
        PhotoComment.objects.create(**comment_form.cleaned_data, photo=photo)
        return HttpResponseRedirect(f"/{self.kwargs['pk']}/photo")


class SubscribeToUser(LoginRequiredMixin, View):
    """
    Подписка на пользователя
    """
    def post(self, request, *args, **kwargs):
        userprofile = UserProfile.objects.get(user_id=request.user.id)
        user = User.objects.get(username=request.POST['username'])
        is_subscribe = False
        for sub in userprofile.subscribes.all():
            if sub == user:
                is_subscribe = True
                break
        if not is_subscribe:
            userprofile.subscribes.add(user)
        if is_subscribe:
            userprofile.subscribes.remove(user)
        return HttpResponseRedirect(f"/{request.POST['username']}")


class FindResultView(generic.ListView):
    """
    Поиск пользователя по username
    """
    model = User
    template_name = 'phototape/find_result.html'

    def get_queryset(self):
        query = self.request.GET.get('text')
        object_list = User.objects.filter(
            Q(username__contains=query))
        return object_list
