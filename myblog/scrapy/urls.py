from django.conf.urls import url
from . import views

app_name = 'scrapy'
urlpatterns = [
     url(r'^scrapy', views.scrapy_weather, name='scrapy_weather'),

]