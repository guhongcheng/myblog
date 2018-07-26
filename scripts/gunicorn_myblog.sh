# description: restart gunicorn
cd /home/charlie/sites/myblog/myblog && exec ../env/bin/gunicorn  myblog.wsgi:application -b 127.0.0.1:8000

