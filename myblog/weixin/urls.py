from django.conf.urls import url
from . import views

app_name = 'weixin'

urlpatterns = [
    url(r'^weixin', views.wechat, name='weixin')
]