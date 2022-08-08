from django.urls import path
from django.contrib import admin
from PHR import views
#from . import views

"""urlpatterns = [
    path('', views.IndexView.as_view(), name= 'index'),
]"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index),
    path('edit/', views.phr),
    path('edit_Basic/', views.BasicChange),
    path('edit_Disease/', views.DiseaseChange),
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('graph/', views.graph),
]