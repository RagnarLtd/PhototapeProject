from django.conf.urls.static import static
from django.urls import path
from django.conf import settings

from phototape.views import UserRegisterFormView, MyLoginView, MyLogoutView, UserProfileEditFormView, UserFormView, \
    UploadPhotoFormView, UserPhotosView, AddLike, AddDislike, PhotoDeatidView, MainPageView, SubscribeToUser, \
    FindResultView

urlpatterns = [
    path('register', UserRegisterFormView.as_view(), name='register'),
    path('login', MyLoginView.as_view(), name='login'),
    path('logout', MyLogoutView.as_view(), name='logout'),
    path('profile_edit', UserProfileEditFormView.as_view(), name='profile_edit'),
    path('profile', UserFormView.as_view(), name='profile'),
    path('upload_photo', UploadPhotoFormView.as_view(), name='upload_photo'),
    path('<str:username>/', UserPhotosView.as_view(), name='user_photos'),
    path('<int:pk>/like/', AddLike.as_view(), name='like'),
    path('<int:pk>/dislike/', AddDislike.as_view(), name='dislike'),
    path('<int:pk>/photo/', PhotoDeatidView.as_view(), name='photo_detail'),
    path('', MainPageView.as_view(), name='main'),
    path('subscribe/', SubscribeToUser.as_view(), name='subscribe'),
    path('find', FindResultView.as_view(), name='find_result'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
