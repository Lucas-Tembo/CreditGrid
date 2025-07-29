from django.urls import path
from . import views
from django.urls import path, include


urlpatterns = [
    path('signup', views.signup, name = 'signup'),
    path('login', views.login_view, name = 'login'),
    path('logout',views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

]