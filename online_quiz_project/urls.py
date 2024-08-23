"""
URL configuration for online_quiz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Routes the '/admin/results/' URL to the URLs defined in the 'quiz' app
    path('admin/results/', include('quiz.urls')), 
    
    # Admin site URL
    path('admin/', admin.site.urls),
    
    # Includes default authentication URLs (login, logout, password change/reset) provided by Django
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Includes the URLs defined in the 'quiz' app for the root of the site
    path('', include('quiz.urls')),
]
