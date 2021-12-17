Инсталяцию будем делать на CentOS 7. Сразу отвечу адептам Debian/Ubuntu и других популярных дистрибутивов. 
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
