from django.urls import path
from .views import RegisterUserView,LoginUserView,ProfileUserView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register-user'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('profile/', ProfileUserView.as_view(), name='profile'),
]
