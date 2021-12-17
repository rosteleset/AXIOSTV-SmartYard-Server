Серверная часть, которая позволяет использовать SmartYard приложения для умных домофонов и видеонаблюдения

Это первый коммит, фактически скелет программы. Содержаться все используемые в API вызовы, но пока только начальная поддержка базы данных, большинство ответов захардкодены. Работа будет продолжаться.

Инсталяцию предлагаем делать на CentOS 7. Предполагается, что репозиторий epel подключен. 
Сразу отвечу адептам Debian/Ubuntu и других популярных дистрибутивов. 
Вы настолько круты, что самостоятельно адаптируете эту инструкцию под Ваши нужды. 
Компания, в которой я работаю, CentOS очень давно является корпоративным стандартом. Имеется свой репозиторий, который решает вопрос
с необходимыми версиями ПО, так как CentOS настолько стабилизирован, что местами это окаменелые ф-лии мамонта.
Приступим. Необходимо выполнить следующие команды в терминале под рутом:

yum install -y python36-virtualenv postgresql-server

cd /opt

mkdir smartyard

virtualenv-3.6 smartyard

smartyard/bin/pip install flask

smartyard/bin/pip install psycopg2-binary

smartyard/bin/pip install smartyard/bin/pip install

smartyard/bin/pip install Flask-Migrate

cd smartyard

su - postgres

psql

CREATE DATABASE smartyard WITH OWNER "smartyard" ENCODING 'UTF8';

postgres=# DROP DATABASE smartyard;

postgres=# GRANT ALL PRIVILEGES ON DATABASE smartyard TO smartyard;

\q

exit

export FLASK_APP=app.py

bin/flask db init

bin/flask db migrate

bin/flask db upgrade

./app.py

Далее необходимо настроить nginx, добовив в конфиг следующие строчки:
 
 location /api {
 
    proxy_pass      http://127.0.0.1:5000;
    
    proxy_set_header HOST $host;
    
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_set_header X-Real-IP $remote_addr;
    
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
    proxy_set_header X-Forwarded-Proto $scheme;
    
    proxy_set_header X-Request-Id $request_id;
    
  }



Лицензия и условия использования

Авторские права на используемое API принаддежат ЛанТа, код АКСИОСТВ

Данный проект опубликован под стандартной общественной лицензией GNU GPLv3. Вы можете модифицировать и использовать наши наработки в своих проектах, в т.ч. коммерческих, при обязательном условии публикации их исходного кода. Также мы готовы рассмотреть ваши Pull requests, если вы хотите чтобы наш проект развивался с учётом ваших модификаций и доработок.
