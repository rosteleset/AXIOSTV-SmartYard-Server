Серверная часть, которая позволяет создать коммерческую систему для умных домофонов и видеонаблюдения. Данная версия развивается для кастомного варианта, который значительно переписан и не имеет обратной совместимости с Теледом.

В новой версии:
1. Переход на асинхронный режим, что позволяет значительно повысить произовдительносить. 
2. Залиты все самые последние новинки, среди них улучшеная подсистема отправки пушей, включая события на открытие ключем и пропущенные вызовы, подсистема детализации наработки и выставления счетов и актов. 
3. Значительно переработан механизм индивидуального выставления прав на девайсы, что позволяет не только давать разные права на объекты, отображаемые в приложении, но и разные права на девайсы внутри одного договора, например можно разрешить открывать домофон, но запретить просматривать камеры с него, или установить на это разыне тарифы и при неоплате отдельно отключать.

Описаны все используемые в API вызовы, и прктически все полностью реализованы. Очень малая часть ответов захардкодена и втекущей версии не используется. 
Реализована поддержка проверки МП перед публикацией в App Store и Google Play для чего необходимо выставить нужные значения в TEST_USER и TEST_PASS, которые в свою очередь написать в маркетах для проверки приложения перед пуюликацией. 

В полном объеме реализована регистрация по телефонному номеру, с проверкой с помощью СМС.

Реализован прием платежей через Юкасса, Центральная касса, ApplePay, GooglePay и SberPay через Сбербанк с использованием колбэка с ассимитричным шифрованием. Это позволяет принимать платежи в реальном времени. Сумма, рекомендованная к платежу вычисляется из стоймости пробления тарифа с учетом текущего баланса. Принятый платеж сразу отображается в балансе. 

Реализован backend авторизации для медиасервера Флюссоник. Он доступен по адресу server.ru/api/accessfl Также есть возможность совмещения с иной системой видеонаблюдения на одном медиасервере. Для этого есть режим проксирования. В первую очередь проверяютя права у МП. Во вторую очередь идет запрос на другой бэкенд и его ответ проксируется. Для включения этого режима заполните в конфиге PROXYFL='https://АДРЕС.ru/flussonic_auth/'

При каждом запросе списка камер каждому пользователю генерируется индивидуальный токен. Он действует только для этих камер, Время действия задается в конфиге в минутах, например EXPIRE=360 (6 часов).

Обращаем внимание, что для полноценной работы требуется интеграция с биллинговой системой, либо создаение отдельной базы пользователей. Привязка идет через номер телефона. Это оказалось очень удобным в случае, если Вы подключаете допуслуги (с мобильным приложением) действующим клиентам, у которых уже есть запись в биллинге с указанным там номером мобильного телефона. В случае, если есть возможность хранения нескольких номеров у каждого договора и один и тот же номер может быть указан в нескольких договорах, то мобильные приложения показывают каждый договор и услуги по нему.

Компанией АКСИОСТВ реализованы коннекторы к биллингам Abills, LanBiling и др. По вопросам внедрения обращайтесь admin@axiostv.ru
Для самостоятельной интеграции внимательно изучите файл Integration_read_me.txt

Инсталяцию можно делать на CentOS 9 (используется у нас), так и на Dabian/Ubuntu. Предполагается, что репозиторий epel подключен (на CentOS), kannel для отправки смс-сообщений на шлюз по протоколу smpp установлен и настроен. Информации по этой теие в сети достаточно. 

Приступим. Необходимо выполнить следующие команды в терминале под рутом:
cd /opt

mkdir smartyard


#CentOS:

yum install -y python3-virtualenv postgresql-server nginx supervisor asterisk redis clickhouse-server

#Проверяем. В итоге должны установиться пакеты:

rpm -qa | grep python3

python3-libs-3.10.10-17.el9.x86_64
python3-pip-wheel-22.3.1-2.el9.noarch
python3-virtualenv-20.13.4-500.el9.noarch
python3-devel-3.10.10-17.el9.x86_64
python3-setuptools-67.6.0-3.el9.noarch
python3-3.10.10-17.el9.x86_64
python3-pip-22.3.1-2.el9.noarch
python3-setuptools-wheel-67.6.0-3.el9.noarch


#Dabian/Ubuntu:

apt-get install python3-venv postgresql nginx supervisor libcurl4-openssl-dev libssl-dev gcc python3-dev asterisk redis clickhouse-server

#Переносим файл smartyard.ini в /etc/supervisord.d 

#Добавляем автозапуск postgresql-server nginx supervisor

#Стартуем postgresql-server nginx


#CentOS:

virtualenv smartyard


#Dabian/Ubuntu:

python3 -m venv smartyard


#Дале в терминале:

/opt/smartyard/bin/pip install requests flask psycopg2-binary firebase-admin Flask-Migrate python-dotenv geopandas pytz clickhouse-connect pycryptodomex pymysql redis Flask-HTTPAuth tzlocal reportlab num2words pydantic asyncpg flask[async] geopy

export PYCURL_SSL_LIBRARY=openssl

/opt/smartyard/bin/pip install pycurl --no-cache-dir
 

cd smartyard

mv example.env .env

cp dump.sql /tmp/dump.sql

su - postgres

psql

CREATE USER smartyard WITH PASSWORD 'smartyardpass';

CREATE DATABASE smartyard WITH OWNER "smartyard" ENCODING 'UTF8';

GRANT ALL PRIVILEGES ON DATABASE smartyard TO smartyard;

\q

psql < /tmp/dump.sql

exit

#Стартуем сервисы:

systemctl start redis

systemctl start clickhouse-server

systemctl start supervisord

systemctl start asterisk

Далее:

./smartyard.py

Смотрим и устраняем все ошибки.

Основные настройки, в т.ч. подключение к базе данных (PG_...) и серверу kannel (KANNEL_), а также имя отправителя смс (поддерживается не всеми смс-агрегаторами) и текстовая строка перед 4-х значным кодом подтверждения (текст смс) находятся в файле .env и интуитвно понятны. 

Создаем файл /etc/supervisord.d/smartyard.ini

[program:smartyard]

#user=smartyard

directory = /opt/smartyard

command = /opt/smartyard/smartyard.py

autostart = true

autorestart = true

stdout_logfile = /var/log/smartyard_out.log

stderr_logfile = /var/log/smartyard_err.log

stopsignal = INT


Далее необходимо настроить nginx, добавив в конфиг следующие строчки:
 
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

Авторские права на код принаддежат АКСИОСТВ.

Данный проект опубликован под стандартной общественной лицензией GNU GPLv3. Вы можете модифицировать и использовать наши наработки в своих проектах, в т.ч. коммерческих, при обязательном условии публикации их исходного кода. Также мы готовы рассмотреть ваши Pull requests, если вы хотите чтобы наш проект развивался с учётом ваших модификаций и доработок.
