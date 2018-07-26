from django.shortcuts import render
import pymysql
from bs4 import BeautifulSoup
from urllib.request import urlopen
import datetime
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time



def scrapy_weather():
    ## 打开数据库连接,connection里charset=utf8是为了把所有的数据都编译成utf8编码格式发送到数据库
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.weather')
    # urls = ['hb', 'db', 'hd', 'hz', 'hn', 'xb', 'xn']
    urls = ['hd', 'hn']
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        "Accept": "*/*",
        "cookie": "f_city=%E5%8C%97%E4%BA%AC%7C101010100%7C%2C%E4%B8%8A%E6%B5%B7%7C101020100%7C%2C%E5%B9%BF%E5%B7%9E%7C101280101%7C; vjuids=22ee3f4b9.163a4a75e16.0.484471d023b63; Hm_lvt_080dabacb001ad3dc8b9b9049b36d43b=1527475822,1527647097; Wa_lvt_1=1527475822,1527647097; vjlast=1527647097.1528254196.11; Hm_lpvt_080dabacb001ad3dc8b9b9049b36d43b=1528254392; Wa_lpvt_1=1528254392"}
    for url in urls:
        link = 'http://www.weather.com.cn/textFC/' + url + '.shtml'
        req = session.get(link, headers=headers)
        req.encoding = 'utf-8'
        bsobj = BeautifulSoup(req.text, 'html.parser')
        tables = bsobj.findAll('div', {'class': 'conMidtab'})[0].findAll('table')
        for table in tables:
            province_global = ''
            trs = table.findAll('tr')
            i = 0
            for tr in trs[2:]:
                tds = tr.findAll('td')
                if i == 0:
                    province = tds[0].get_text()
                    city = tds[1].get_text()
                    weather_info = tds[2].get_text()
                    wind_info = tds[3].get_text()
                    highest_temp = tds[4].get_text()
                    province_global = province
                else:
                    province = province_global
                    city = tds[0].get_text()
                    weather_info = tds[1].get_text()
                    wind_info = tds[2].get_text()
                    highest_temp = tds[3].get_text()
                province = province.replace('\n', '')
                city = city.replace('\n', '')
                weather_info = weather_info.replace('\n', '')
                wind_info = wind_info.replace('\n', '')
                highest_temp = highest_temp.replace('\n', '')
                scrapy_date = datetime.datetime.now().strftime('%Y-%m-%d')
                cur.execute(
                    'insert into scrapy.weather(province, city, weather_info, wind_info, highest_temp, scrapy_date) values(''%s'', ''%s'', ''%s'',''%s'',''%s'', ''%s'')',
                    (province, city, weather_info, wind_info, highest_temp, scrapy_date))
                cur.connection.commit()
                i = i + 1
    cur.close()
    conn.close()
    result = '爬取成功'
    return result


def search_weather(city):
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('select province,city,weather_info,wind_info,highest_temp from scrapy.weather where city = ''%s''',
                (city,))
    weather_info = cur.fetchone()
    cur.close()
    conn.close()
    return weather_info


def search_existweather(searchdate):
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('select id from scrapy.weather where scrapy_date = ''%s'' limit 1', (searchdate,))
    weather_info = cur.fetchone()
    cur.close()
    conn.close()
    return weather_info


def delete_weather():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.weather')
    result = '删除成功'
    cur.close()
    conn.close()
    return result


def scrapy_movie():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)AppleWebKit 537.36(KHTML, like Gecko) Chrome",
        "Accept": "*/*",
        "cookie": "ci=82"}
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.maoyan_movie')
    init_url = 'https://maoyan.com'
    cinema_init_url = init_url + '/cinemas?movieId='
    movies_url = init_url + '/films'
    req = session.get(movies_url, headers=headers)
    bsobj = BeautifulSoup(req.text, 'html.parser')
    movies = bsobj.find('dl', {'class': 'movie-list'}).findAll('dd')
    for movie in movies:
        title = movie.find('div', {'class': 'movie-item-title'}).attrs['title']
        inner_url = str(movie.find('a', {'data-act': 'movie-click'}).attrs['href'])
        movie_url = init_url + inner_url
        img_url = movie.findAll('img')[1].attrs['data-src']
        movie_id = str(inner_url.split('/')[2])
        cinema_url = cinema_init_url + movie_id
        cur.execute(
            'insert into scrapy.maoyan_movie(title,img_url,movie_url,cinema_url) values(''%s'', ''%s'', ''%s'',''%s'')',
            (title, img_url, movie_url, cinema_url))
        cur.connection.commit()
        cinema_req = session.get(cinema_url, headers=headers)
        cinema_bsobj = BeautifulSoup(cinema_req.text, 'html.parser')
        cinemas = cinema_bsobj.find('div', {'class': 'cinemas-list'}).findAll('div', {'class': 'cinema-cell'})
        for cinema in cinemas:
            name = cinema.find('a', {'class': 'cinema-name'}).get_text()
            district = cinema.find('p', {'class': 'cinema-address'}).get_text()
            price = cinema.find('span', {'class': 'stonefont'}).get_text()
            cur.execute(
                'insert into scrapy.maoyan_cinema(name,district,price,movie_name) values(''%s'', ''%s'', ''%s'', ''%s'')',
                (name, district, price, title))
            cur.connection.commit()
    cur.close()
    conn.close()
    result = '爬取成功'
    return result


def current_movie():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('SELECT title,img_url,movie_url FROM scrapy.maoyan_movie limit 6 ')
    movie_info = cur.fetchall()
    cur.close()
    conn.close()
    return movie_info


def delete_movie():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.maoyan_movie')
    result = '删除成功'
    cur.close()
    conn.close()
    return result


def scrapy_loupan():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.loupan')
    year_month = datetime.datetime.now().strftime('%Y%m')
    today = datetime.date.today()
    year = today.year
    month = today.month
    first = today.replace(day=1)
    lastYearMonth = first - datetime.timedelta(days=1)
    lastYearMonth = lastYearMonth.strftime('%Y%m')
    if month == 12:
        next_month = 1
        year = year + 1
    else:
        next_month = month + 1
    NextYearMonth = datetime.datetime(year, next_month, 1)
    NextYearMonth = NextYearMonth.strftime('%Y%m')
    scrapy_yearmonth = []
    scrapy_yearmonth.append(year_month)
    scrapy_yearmonth.append(str(lastYearMonth))
    scrapy_yearmonth.append(str(NextYearMonth))
    for ym in scrapy_yearmonth:
        session = requests.Session()
        url = 'http://newhouse.nt.fang.com/house/saledate/' + ym + '.htm'
        req = session.get(url)
        req.encoding = 'gb2312'
        bsobj = BeautifulSoup(req.text, 'html.parser')
        houses = bsobj.find('div', {'id': 'kplist'}).findAll('li')
        for house in houses:
            if house.find('div'):
                name = str(house.find('div', {'class': 'nlcd_name'}).find('a').get_text())
                district = house.find('div', {'class': 'address'}).find('a').attrs['title']
                price = house.find('div', {'class': 'nhouse_price'}).find('span').get_text()
                imgs = house.find('div', {'class': 'nlc_img'}).findAll('img')
                if len(imgs) == 3:
                    imgurl = imgs[1].attrs['src']
                else:
                    imgurl = imgs[0].attrs['src']
                detailurl = house.find('div', {'class': 'nlcd_name'}).find('a').attrs['href']
                cur.execute(
                    'insert into scrapy.loupan(name, district, price, imgurl, detailurl, scrapy_date) values(''%s'', ''%s'', ''%s'',''%s'', ''%s'',''%s'')',
                    (name, district, price, imgurl, detailurl, ym))
                cur.connection.commit()
    cur.close()
    conn.close()
    result = '爬取成功'
    return result


def current_loupan():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cur = conn.cursor()
    cur.execute(
        "select case when price='价格待定' then concat(name,'-',substring(district,1,3),'-',price) else concat(name, '-', substring(district, 1, 3), '-', price, '元/m²')end as info, imgurl, detailurl from scrapy.loupan limit 8")
    loupan_info = cur.fetchall()
    cur.close()
    conn.close()
    return loupan_info


def delete_loupan():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.loupan')
    result = '删除成功'
    cur.close()
    conn.close()
    return result


def scrapy_shop():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
        "Accept": "*/*",
        "cookie": "cy=94; cye=nantong;"}
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.shop')
    url = 'http://www.dianping.com/mylist/ajax/shoprank?rankId=e75efa4f2527ec212b56e143f87c878608e25c702ab1b810071e8e2c39502be1'
    req = session.get(url, headers=headers)
    data = json.loads(req.text)
    shops = data['shopBeans']
    shop_init_url = 'http://www.dianping.com/shop/'
    for shop in shops:
        name = shop['shopName']
        CategoryName = shop['mainCategoryName']
        RegionName = shop['mainRegionName']
        avgPrice = shop['avgPrice']
        # address = shop['address']
        imgurl = shop['defaultPic']
        shop_url = shop_init_url + str(shop['shopId'])
        cur.execute(
            'insert into scrapy.shop(name,CategoryName,RegionName,avgPrice,imgurl,shop_url) values(''%s'', ''%s'', ''%s'',''%s'', ''%s'',''%s'')',
            (name, CategoryName, RegionName, avgPrice, imgurl, shop_url))
        cur.connection.commit()
    cur.close()
    conn.close()
    result = '爬取成功'
    return result


def current_shop(page):
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    sql = "select concat(name,'-',CategoryName,'-',RegionName,'-', '人均￥', avgPrice)as info, imgurl,shop_url from scrapy.shop order by id limit " + str(
        (page - 1) * 6) + ",6"
    cur.execute(sql)
    shop_info = cur.fetchall()
    cur.close()
    conn.close()
    return shop_info


def delete_shop():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.shop')
    result = '删除成功'
    cur.close()
    conn.close()
    return result


def query_song(name):
    url = r'http://s.music.163.com/search/get/?type=1&s=' + name
    session = requests.Session()
    req = session.get(url)
    musics = json.loads(req.text)
    music = musics['result']['songs'][0]
    music_info = {
        'music_url': music['page'],
        'title': music['name']
    }
    return music_info



def scrapy_point():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.travel')
    session = requests.Session()
    link = 'http://www.tuniu.com/motif/d1318'
    req = session.get(link)
    req.encoding = 'utf-8'
    bsobj = BeautifulSoup(req.text, 'html.parser')
    points = bsobj.find('div', {'class': 'main-coat'}).findAll('div', {'class': 'board-point'})
    for point in points:
        name = point.find('h2', {'class': 'point-name'}).get_text()
        imgurl = point.find('a', {'class': 'pic'}).find('img').attrs['src']
        detailurl = point.find('a', {'class': 'go'}).attrs['href']
        travel_count = point.find('p', {'class': 'catelog'}).findAll('span')[0].get_text()
        recommand = point.find('span', {'class': 'recommand'}).get_text()[:50] + '...'
        cur.execute(
            'insert into scrapy.travel(name,imgurl,detail_url,travel_count,recommand) values(''%s'', ''%s'', ''%s'',''%s'', ''%s'')',
            (name, imgurl, detailurl, travel_count, recommand))
        cur.connection.commit()
    cur.close()
    conn.close()
    result = '爬取成功'
    return result


def delete_point():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    cur.execute('TRUNCATE TABLE scrapy.travel')
    result = '删除成功'
    cur.close()
    conn.close()
    return result


def query_point():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    sql = "select  concat(a.name,'-',a.recommand) as detail,a.imgurl,a.detail_url from scrapy.travel a where a.travel_count like '%万' order by cast(replace(a.travel_count,'万','') as decimal(5,1)) desc limit 8"
    cur.execute(sql)
    point_info = cur.fetchall()
    cur.close()
    conn.close()
    return point_info


def scrapy_flight():
    conn = pymysql.connect(host='localhost', user='root', passwd='Guhc@1990', charset='utf8')
    cur = conn.cursor()
    #cur.execute('TRUNCATE TABLE scrapy.flight')
    # driver = webdriver.PhantomJS(executable_path='c:/software/phantomjs/bin/phantomjs')
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    )
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    scrapy_date = "2018-06-30"
    time.sleep(2)
    driver.get("http://flights.ctrip.com/booking/NTG-CAN-day-1.html?DDate1=" + scrapy_date)
    with open('xiecheng.txt','w') as f:
        f.write(driver.page_source)
    driver.save_screenshot('s.png')
    # airline = driver.find_element_by_css_selector("#flight_ZH9966 strong.pubFlights_zh.flight_logo").text
    for i in range(0, 8):
        # flight_element = "//div[@data-classifyid='__classify_id__" + str(i) + "']"
        flight_element = "//div[contains(@id,'flight')][@data-classifyid='__classify_id__" + str(i) + "']"
        is_exists_flight = driver.find_elements_by_xpath(flight_element)
        if len(is_exists_flight) > 0:
            flight_no = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td/div[@class='clearfix J_flight_no']/span").text
            airline = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td/div[@class='clearfix J_flight_no']/strong").text
            plane_type = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td/div[@class='low_text']/span").text
            departure_time = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td[@class='right']/div/strong").text
            departure_ariport = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td[@class='right']/div[2]").text
            arrive_time = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td[@class='left']/div/strong").text
            arrive_ariport = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td[@class='left']/div[2]").text
            lowest_price = driver.find_element_by_xpath(
                flight_element + "/table/tbody/tr/td[@class='price ']/span[@class='J_base_price']/span[@class='base_price02']").text.replace(
                "¥", "")
            # record_exist = "SELECT 1 FROM scrapy.flight where flight_no='%s' and scrapy_date='%s' " % (flight_no, scrapy_date)
            # print(record_exist)
            # cur.execute(record_exist)
            # print(len(cur.fetchall()))
            # if(len(cur.fetchall())==0):
            #     print(111)
            #     cur.execute(
            #         'insert into scrapy.flight(flight_no,airline,plane_type,departure_time,departure_airport,arrive_time,arrive_airport,lowest_price,scrapy_date) values(''%s'', ''%s'', ''%s'',''%s'', ''%s'', ''%s'',''%s'', ''%s'', ''%s'')',
            #         (flight_no, airline, plane_type, departure_time, departure_ariport, arrive_time, arrive_ariport,
            #          lowest_price, scrapy_date))
            #     cur.connection.commit()

    driver.quit()
    cur.close()
    conn.close()
    result = '爬取成功'
    return result
