"""
URL configuration for viksit_47 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from django.conf import settings


urlpatterns = [
    path('', views.home, name='home'),
    path('exams/', views.exams, name='exams'),
     path('mock/', views.mock, name='mock'),
    path('blogs/', views.blogs, name='blogs'),
    path('contact/', views.contact, name='contact'),
     path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('mock/', views.mock_redirect, name='mock_redirect'), 
    path("submit-mock/", views.submit_mock, name="submit_mock"),
     path("mock/<int:mock_id>/", views.mock, name="mock"),
    path('mock/', views.mock_redirect, name='mock_redirect'),
      path('mock/<int:mock_id>/submit/', views.submit_mock, name='submit_mock'),
     path("equipments/", views.equipments_view, name="equipments"),
]

