# INTRODUCTION




![homepage screenshot](http://github.com/wandonye/vshare/raw/master/screenshots/vshare_screenshot.png)

## FEATURES

### Frontend Framework

- [HTML5 Boilerplate](https://github.com/h5bp/html5-boilerplate).
- [jQuery](http://jquery.com/). 
- [Twitter Bootstrap](https://github.com/twitter/bootstrap).

### Flask Extensions

- Handle **orm** with [SQLAlchemy](http://www.sqlalchemy.org).
- Handle **web forms** with [WTForms](http://wtforms.simplecodes.com/).
- Implement **user session management (signin/signout/rememberme)** with [Flask-Login](https://github.com/maxcountryman/flask-login).
- Implement **reset password via email** with [Flask-Mail](http://packages.python.org/Flask-Mail/).
- Implement **unit testing** with [Flask-Testing](http://packages.python.org/Flask-Testing/).
- Implement **external script (initdb/testing/etc)** with [Flask-Script](http://flask-script.readthedocs.org/en/latest/).
- Handle **i18n** with [Flask-Babel](http://packages.python.org/Flask-Babel/).

### Others

- Well designed structure for **large project**.
- Quickly Deploy via [mod\_wsgi](http://flask.pocoo.org/docs/deploying/mod_wsgi/) and [fabric](http://flask.pocoo.org/docs/patterns/fabric/).
- Admin interface.
- Home-bake logger.

## USAGE

Pre-required:

- Ubuntu (should be fine in other linux distro)
- git
- pip
- postgresql
- virtualenv or conda
- apache + mod\_wsgi

Clone.

    git clone https://github.com/wandonye/vshare.git vshare


Reset local debug env:

- rm -rf /tmp/instance

- mkdir /tmp/instance

- python manage.py initdb

To setup:

- source activate vshare
- python setup.py install

To run:

- python manage.py run


Translation:

-python setup.py compile_catalog --directory `find -name translations` --locale zh -f"

Open `http://127.0.0.1:5000`, done!

## Deploy with WSGI

Clone.

    cd /var/www
    git clone https://github.com/imwilsonxu/vshare.git vshare
    sudo chown `whoami` -R vshare

vhost.

    WSGIDaemonProcess vshare user=wilson group=wilson threads=5
    WSGIScriptAlias /vshare /var/www/vshare/app.wsgi

    <Directory /var/www/vshare/>
        WSGIScriptReloading On
        WSGIProcessGroup vshare
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>


**IMPORTANT**:

- Change `INSTANCE_FOLDER_PATH` in `vshare/utils.py` to suit yourself.
- Put `production.cfg` under `INSTANCE_FOLDER_PATH`.

## STRUCTURE

    ├── app.wsgi                (mod_wsgi wsgi config)
    ├── CHANGES
    ├── vshare                   (main app)
    │   ├── api                 (api module)
    │   ├── app.py              (create flask app)
    │   ├── config.py           (config module)
    │   ├── decorators.py
    │   ├── extensions.py       (init flask extensions)
    │   ├── frontend            (frontend module)
    │   ├── __init__.py
    │   ├── settings            (settings module)
    │   ├── static
    │   │   ├── css
    │   │   ├── favicon.png
    │   │   ├── humans.txt
    │   │   ├── img
    │   │   ├── js
    │   │   └── robots.txt
    │   ├── templates
    │   │   ├── errors
    │   │   ├── frontend
    │   │   ├── index.html
    │   │   ├── layouts 
    │   │   ├── macros
    │   │   ├── settings
    │   │   └── user
    │   ├── translations        (i18n)
    │   ├── chat                (chat module)
    │   │   ├── models.py
    │   ├── admin                (admin module)
    │   │   ├── constants.py
    │   │   ├── forms.py        (wtforms)
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   ├── post                (post module)
    │   │   ├── constants.py
    │   │   ├── forms.py        (wtforms)
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   ├── user                (user module)
    │   │   ├── constants.py
    │   │   ├── forms.py        (wtforms)
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── views.py
    │   ├── utils.py
    ├── LICENSE
    ├── manage.py               (manage via flask-script)
    ├── MANIFEST.in
    ├── README.markdown
    ├── screenshots
    ├── setup.py
    └── tests                   (unit tests, run via `nosetest`)

## LICENSE

[MIT LICENSE](http://www.tldrlegal.com/license/mit-license)

## ACKNOWLEDGEMENTS

Thanks to Python, Flask, its [extensions](http://flask.pocoo.org/extensions/), and other goodies.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/imwilsonxu/vshare/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

