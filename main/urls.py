from django.urls import path , include
from . import views
from django.contrib.auth import views as auth_views




urlpatterns = [
    path('', views.base, name="base"),

    path('mybank/', views.mybank, name="mybank"),

    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name="logout"),
    path('verify-email/', views.verify_email, name='verify_email'),

    path('transfer/', views.transfer, name='transfer'),
    path("transfer/confirm/", views.confirm_transfer, name="confirm_transfer"),
    path("ajax/find-user/", views.find_user_ajax, name="find_user_ajax"),

    path('history/', views.history, name='history'),

]
