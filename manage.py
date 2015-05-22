# -*- coding: utf-8 -*-

from flask.ext.script import Manager
from datetime import datetime

from vshare import create_app
from vshare.extensions import db
from vshare.user import User, UserDetail, ADMIN, USER, ACTIVE
from vshare.utils import MALE, FEMALE
from vshare.post import Post, Tag


app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""

    app.run()

@manager.command
def test():
    """Run the tests."""
    os.system('py.test --tb=short -s tests/')


@manager.command
def initdb():
    """Init/reset database."""

    db.drop_all()
    db.create_all()
    admin = User(
            name=u'admin',
            email=u'admin@example.com',
            password=u'123456',
            first_name='first_name',
            last_name='last_name',
            role_code=ADMIN,
            confirmed_at=datetime.now(),
            status_code=ACTIVE,
            user_detail=UserDetail(
                sex_code=MALE,
                birth_day=datetime(1982, 11, 11),
                phone='0102831089',
                url=u'http://admin.example.com',
                deposit=100.00,
                location=u'Hangzhou',
                bio=u'admin Guy is ... hmm ... just a admin guy.'))
#    admin.followers.add(4)
    db.session.add(admin)
    db.session.commit()

    admin = User.query.get(1)
    for usr in ['foooo1','foooo2']:
        user = User(
                name=usr,
                email=usr+'@example.com',
                password='Pw'+usr,
                first_name='DT'+usr,
                last_name='Wang',
                role_code=USER,
                confirmed_at=datetime.now(),
                user_detail=UserDetail(
                    sex_code=FEMALE,
                    birth_day=datetime(1982, 11, 11),
                    phone='0102831089',
                    deposit=100.00,
                    location='Hangzhou',
                    bio='a great user!.'))
        db.session.add(user)
        db.session.commit()

    user = User(
            name='danny',
            email='wandonye@qq.com',
            password=u'Test123',
            first_name='Dongning',
            last_name='Wang',
            confirmed_at=datetime.now(),
            user_detail=UserDetail(
                birth_day=datetime(1982, 11, 11),
                phone='0102831089',
                location='Madison',
                bio='a great user!.'))
    db.session.add(user)
    db.session.commit()
    user = User.query.get(4)
    user.follow(admin)
    db.session.add(user)
    db.session.commit()


    post = Post(text='form.text.data', tags=[Tag(tag='food')], 
                    effective_on=datetime(2014, 11, 11), 
                    user_id=1)
    db.session.add(post)
    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
