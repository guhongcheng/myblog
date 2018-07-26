# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, \
    EventMessage
from myblog.settings import WECHAT_TOKEN, WEIXIN_APPID, WEIXIN_APPSECRET
from scrapy import views as scrapy_view
from urllib.parse import urlencode
wechat_instance = WechatBasic(
    token=WECHAT_TOKEN,
    appid=WEIXIN_APPID,
    appsecret=WEIXIN_APPSECRET
)


@csrf_exempt
def wechat(request):
    if request.method == 'GET':
        # 检验合法性
        # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        if not wechat_instance.check_signature(
                signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest('Verify Failed')

        return HttpResponse(
            request.GET.get('echostr', ''), content_type="text/plain")

    # 解析本次请求的 XML 数据
    try:
        wechat_instance.parse_data(data=request.body)
    except ParseError:
        return HttpResponseBadRequest('Invalid XML Data')
    # 获取解析好的微信请求信息
    message = wechat_instance.get_message()
    if isinstance(message, TextMessage):
        # 当前会话内容
        content = message.content.strip()
        if content == '功能':
            reply_text = (
                '欢迎关注南通本地公众号,在这里你可以查询"天气"、"电影"、"楼盘"、"旅游"相关信息\n' +
                '更多功能，敬请期待'
            )
            response = wechat_instance.response_text(content=reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '爬取天气':
            reply_text = scrapy_view.scrapy_weather()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '查询天气':
            reply_text = (
                '请问您想查看哪个城市的天气信息'
            )
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '删除天气':
            reply_text = scrapy_view.delete_weather()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '爬取电影':
            reply_text = scrapy_view.scrapy_movie()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '查询热映电影' or content == '查询电影':
            movie_list = scrapy_view.current_movie()
            reply_text = []
            for movie in movie_list:
                movie_info = {
                    'title': movie[0],
                    'picurl': movie[1],
                    'url': movie[2]
                }
                reply_text.append(movie_info)
            response = wechat_instance.response_news(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '删除电影':
            reply_text = scrapy_view.delete_movie()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '爬取美食':
            reply_text = scrapy_view.scrapy_shop()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if '查询美食' in content:
            page = 1
            if len(content) > 4:
                page = int(content[4])
            shop_list = scrapy_view.current_shop(page)
            reply_text = []
            for shop in shop_list:
                shop_info = {
                    'title': shop[0],
                    'picurl': shop[1],
                    'url': shop[2]
                }
                reply_text.append(shop_info)
            response = wechat_instance.response_news(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '删除美食':
            reply_text = scrapy_view.delete_shop()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '爬取楼盘':
            reply_text = scrapy_view.scrapy_loupan()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if '最新楼盘' in content or '查询楼盘' in content:
            loupan_list = scrapy_view.current_loupan()
            reply_text = []
            for loupan in loupan_list:
                loupan_info = {
                    'title': loupan[0],
                    'picurl': loupan[1],
                    'url': loupan[2]
                }
                reply_text.append(loupan_info)
            response = wechat_instance.response_news(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content == '删除楼盘':
            reply_text = scrapy_view.delete_loupan()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content in ['爬取旅游', '爬取蜜月']:
            reply_text = scrapy_view.scrapy_point()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content in ['删除旅游', '删除蜜月']:
            reply_text = scrapy_view.delete_point()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content in ['查询蜜月', '查询旅游']:
            point_list = scrapy_view.query_point()
            reply_text = []
            for point in point_list:
                point_info = {
                    'title': point[0],
                    'picurl': point[1],
                    'url': point[2]
                }
                reply_text.append(point_info)
            response = wechat_instance.response_news(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if content in ['爬取机票']:
            reply_text = scrapy_view.scrapy_flight()
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
        if '点歌' in content:
            if content == '点歌':
                reply_text = '请按正确格式进行点歌 点歌+歌名'
                response = wechat_instance.response_text(reply_text)
                return HttpResponse(response, content_type="application/xml")
            else:
                song_name = content[2:]
                song_name = urlencode({
                    "w": song_name
                })
                music_url = "https://y.qq.com/portal/search.html#page=1&searchid=1&remoteplace=txt.yqq.top&t=song&" + song_name
                response = wechat_instance.response_text(music_url)
                return HttpResponse(response, content_type="application/xml")
        else:
            reply_text = '功能还没有实现'
            weather_info = scrapy_view.search_weather(content)
            if weather_info != None:
                reply_text = weather_info[1] + ' ' + weather_info[2] + ' ' + weather_info[3] + ' 最高气温' + \
                             weather_info[4]
            response = wechat_instance.response_text(reply_text)
            return HttpResponse(response, content_type="application/xml")
    elif isinstance(message, VoiceMessage):
        reply_text = '语音信息我听不懂/:P-(/:P-(/:P-('
    elif isinstance(message, ImageMessage):
        reply_text = '图片信息我也看不懂/:P-(/:P-(/:P-('
    elif isinstance(message, VideoMessage):
        reply_text = '视频我不会看/:P-('
    elif isinstance(message, LinkMessage):
        reply_text = '链接信息'
    elif isinstance(message, LocationMessage):
        reply_text = '地理位置信息'
    elif isinstance(message, EventMessage):
        if message.type == 'subscribe':
            reply_text = '感谢您的到来!回复“功能”返回使用指南'
            # if message.key and message.ticket:
            #     reply_text += '\n来源：二维码扫描'
            # else:
            #     reply_text += '\n来源：搜索公众号名称'
        elif message.type == 'unsubscribe':
            reply_text = '取消关注事件'
        elif message.type == 'scan':
            reply_text = '已关注用户扫描二维码！'
        elif message.type == 'location':
            reply_text = '上报地理位置'
        elif message.type == 'click':
            if "楼盘" in message.key:
                loupan_list = scrapy_view.current_loupan()
                reply_text = []
                for loupan in loupan_list:
                    loupan_info = {
                        'title': loupan[0],
                        'picurl': loupan[1],
                        'url': loupan[2]
                    }
                    reply_text.append(loupan_info)
                response = wechat_instance.response_news(reply_text)
                return HttpResponse(response, content_type="application/xml")
            if "旅游" in message.key:
                point_list = scrapy_view.query_point()
                reply_text = []
                for point in point_list:
                    point_info = {
                        'title': point[0],
                        'picurl': point[1],
                        'url': point[2]
                    }
                    reply_text.append(point_info)
                response = wechat_instance.response_news(reply_text)
                return HttpResponse(response, content_type="application/xml")
            if "美食" in message.key:
                page = 1
                content = message.key
                if len(content) > 4:
                    page = int(content[4])
                shop_list = scrapy_view.current_shop(page)
                reply_text = []
                for shop in shop_list:
                    shop_info = {
                        'title': shop[0],
                        'picurl': shop[1],
                        'url': shop[2]
                    }
                    reply_text.append(shop_info)
                response = wechat_instance.response_news(reply_text)
                return HttpResponse(response, content_type="application/xml")
            else:
                reply_text = scrapy_view.search_weather(message.key)
                response = wechat_instance.response_text(content=reply_text)
                return HttpResponse(response, content_type="application/xml")
        elif message.type == 'view':
            reply_text = '自定义菜单跳转链接'
        elif message.type == 'templatesendjobfinish':
            reply_text = '模板消息'
    else:
        reply_text = '功能还没有实现'
    response = wechat_instance.response_text(content=reply_text)
    return HttpResponse(response, content_type="application/xml")
