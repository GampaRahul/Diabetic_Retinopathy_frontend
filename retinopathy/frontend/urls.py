from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('predicting', views.predicting, name='predicting'),
    path('signIn', views.signIn, name='signIn'),
    path('signUp', views.signUp, name='signUp'),
    path('logout', views.logout, name='logout'),
    path('session', views.session, name='session'),
    path('history', views.history, name='history'),
    path('save', views.save, name='save'),
    path('getData', views.getData, name='getData'),
    path('getPic', views.getPic, name='getPic')
]

