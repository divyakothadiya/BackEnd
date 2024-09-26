from django.urls import path
from .views import RegisterUserView,LoginUserView,ProfileUserView,ProfileUserUpdateView,DeleteUserView,VerifyOTP

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/', ProfileUserView.as_view(), name='profile'),
    path('update-profile/', ProfileUserUpdateView.as_view(), name='update-profile'),
    path('delete/', DeleteUserView.as_view(), name='delete-user'),
    path('verify/', VerifyOTP.as_view(), name = 'verify'),
]
