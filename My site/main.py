# -*- coding: utf-8 -*-

import hashlib
import os
import time

import tornado.ioloop
import tornado.web
from PIL import Image
from tornado import escape
import connections

settings = {
    "cookie_secret": "SECRETCODE",
    "login_url": "/login",
}


def get_user_info(name):
    connect = connections.getConnection()
    cursor = connect.cursor()
    cursor.execute("select * from users where login = %s", name)
    user_info = cursor.fetchone()
    connect.commit()
    cursor.close()
    connect.close()
    return user_info


def scale_image(input_image_path,
                output_image_path,
                width=None,
                height=None
                ):
    original_image = Image.open(input_image_path)
    w, h = original_image.size

    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        # No width or height specified
        raise RuntimeError('Width or height required!')

    original_image.thumbnail(max_size, Image.ANTIALIAS)
    original_image.save(output_image_path)

    scaled_image = Image.open(output_image_path)
    width, height = scaled_image.size


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        connect = connections.getConnection()
        cursor = connect.cursor()
        cursor.execute("select * from users")
        users = cursor.fetchall()
        connect.commit()
        cursor.close()
        connect.close()
        if self.get_secure_cookie("login") is not None:
            cookier = self.get_secure_cookie("login").decode('utf-8')
            for user in users:
                if user['login'] == cookier:
                    return self.get_secure_cookie("login")
        return None


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        connect = connections.getConnection()
        cursor = connect.cursor()
        cursor.execute("select * from posts order by post_id desc limit 50")
        posts = cursor.fetchall()
        connect.commit()
        cursor.close()
        connect.close()
        self.render('templates/content.html', first_posts=posts, user_info=get_user_info(name))


class LoginHandler(BaseHandler):
    def get(self):
        self.render('templates/login.html')

    def post(self):
        login = self.get_argument("login")
        password = self.get_argument("password")
        connect = connections.getConnection()
        cursor = connect.cursor()
        cursor.execute("select * from users")
        users = cursor.fetchall()
        connect.commit()
        cursor.close()
        connect.close()
        for user in users:
            if user['login'] == login and user['password'] == password:
                self.set_secure_cookie("login", user['login'], expires_days=1)
                connect = connections.getConnection()
                cursor = connect.cursor()
                cursor.execute("update users set last_cookie = %s where login = %s", (user['login'], user['login']))
                connect.commit()
                cursor.close()
                connect.close()
                self.redirect("/")
                break
        else:
            self.clear_all_cookies(path="/")
            self.redirect("/login")


class AdminPanelHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        gusi = get_user_info(name)
        if gusi is not None and gusi['isadmin'] > 0:
            self.render('templates/adminpanel.html', user_info=gusi)
        else:
            self.redirect('/')


class AddPostAdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        gusi = get_user_info(name)
        if gusi is not None and gusi['isadmin'] > 0:
           self.render('templates/addpost.html', user_info=gusi)
        else:
           self.redirect('/')

    def post(self):
        poster_name = tornado.escape.xhtml_escape(self.current_user)
        post_name = self.get_argument("post_name")
        short_info = self.get_argument("short_info")
        long_info = self.get_argument("long_info")
        tags = self.get_argument("tags")

        file1 = self.request.files['main_image'][0]
        original_fname = 'static/post_imgs/' + str(
            hashlib.md5((str(time.time()) + file1['filename']).encode()).hexdigest()) + '.png'
        output_file = open(original_fname, 'wb')

        output_file.write(file1['body'])
        scale_image(input_image_path=original_fname,
                    output_image_path=original_fname,
                    height=360)
        main_image = '/' + original_fname
        post_time = time.strftime('%Y-%m-%d %H-%M-%S')
        connect = connections.getConnection()
        cursor = connect.cursor()
        cursor.execute("insert into posts values(0, %s, %s, %s, %s, %s, %s, %s)",
                       (post_name, short_info, long_info, main_image, tags, poster_name, post_time))
        connect.commit()
        cursor.execute("update users set count_posts=count_posts+1 where login = %s", poster_name)
        connect.commit()
        cursor.close()
        connect.close()

        self.redirect('/adminpanel')


class ViewPostHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, post_id):
        name = tornado.escape.xhtml_escape(self.current_user)
        connect = connections.getConnection()
        cursorp = connect.cursor()
        existp = cursorp.execute("select * from posts where post_id =%s", post_id)
        posts = cursorp.fetchall()
        cursorp.close()
        cursorc = connect.cursor()
        existc = cursorc.execute("select * from comments join users where comments.author = users.login and post_id =%s ", post_id)
        comments = cursorc.fetchall()
        cursorc.close()
        connect.close()
        if existp == 0:
            self.redirect("/")
        else:
            self.render('templates/post_base.html', first_posts=posts, comments=comments, user_info=get_user_info(name))

    def post(self, post_id):
        name = tornado.escape.xhtml_escape(self.current_user)
        try:
            comment = self.get_argument('comment_text')
        except Exception as e:
            # post_id = self.request.uri.split('/')[2]
            connect = connections.getConnection()
            cursor = connect.cursor()
            cursor.execute("delete from posts where post_id =%s", post_id)
            connect.commit()
            cursor.close()
            connect.close()
            self.redirect("/")
        else:
            if comment is not None:
                connect = connections.getConnection()
                cursora = connect.cursor()
                cursora.execute("insert into comments values(0, %s, %s, %s, %s)",
                                (comment, post_id, name, time.strftime('%Y-%m-%d %H-%M-%S')))
                connect.commit()
                cursora.close()
                connect.close()
                self.redirect(self.request.uri)
            else:
                self.redirect(self.request.uri)


class testHandler(BaseHandler):
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        print(self.request.uri)
        self.render('templates/test.html')


class deauthHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies(path="/")
        self.redirect("/login")


class profileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.render('templates/profile.html', user_info=get_user_info(name))

    def post(self):
        user_change = tornado.escape.xhtml_escape(self.current_user)
        user_name = self.get_argument("user_name")
        user_mail = self.get_argument("user_mail")
        user_password = self.get_argument("user_password")

        file1 = self.request.files['user_image_url'][0]
        hash_sum = str(
            hashlib.md5((str(time.time()) + file1['filename']).encode()).hexdigest()) + '.png'
        original_fname = 'static/user_image/' + hash_sum
        output_file = open(original_fname, 'wb')

        output_file.write(file1['body'])
        out_fname = 'static/user_image/thumbnail/' + hash_sum
        scale_image(input_image_path=original_fname,
                    output_image_path=out_fname,
                    height=32)

        connect = connections.getConnection()
        cursor = connect.cursor()
        cursor.execute(
            "update users set user_name=%s, mail=%s, password=%s, user_image_url=%s, user_image_thumbnail_url=%s where login = %s",
            (user_name, user_mail, user_password, original_fname, out_fname, user_change))
        connect.commit()
        cursor.close()
        connect.close()

        self.redirect("/profile")


class findHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.redirect("/")

    def post(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        search_line = self.get_argument("search_line")
        if search_line is not None:
            user_info = get_user_info(name)
            connect = connections.getConnection()
            cursora = connect.cursor()
            cursorpn = connect.cursor()
            result_author = cursora.execute("select * from posts where author like '" + str(search_line) + "%'")
            result_post_name = cursorpn.execute("select * from posts where post_name like '" + str(search_line) + "%'")
            if result_author > 0:
                find_postsa = cursora.fetchall()
                self.render('templates/find.html', first_posts=find_postsa, user_info=user_info)
            elif result_post_name > 0:
                find_postspn = cursorpn.fetchall()
                self.render('templates/find.html', first_posts=find_postspn, user_info=user_info)
            else:
                find_postsa = cursora.fetchall()
                self.render('templates/find.html', first_posts=find_postsa, user_info=user_info)
            cursora.close()
            cursorpn.close()
            connect.close()


class registerHandler(BaseHandler):
    def get(self):
        bad = False
        self.render('templates/register.html', bad=bad)

    def post(self):
        new_login = self.get_argument('new_login')
        new_username = self.get_argument('new_username')
        new_mail = self.get_argument('new_mail')
        new_password = self.get_argument('new_password')
        new_user_image = 'static/user_image/default.png'
        new_user_thumbnail_image = 'static/user_image/thumbnail/default.png'
        connect = connections.getConnection()
        cursorf = connect.cursor()
        ifexist = cursorf.execute("select * from users where login = '" + str(new_login) + "' or mail = '" + str(new_mail) + "'")
        cursorf.close()
        if ifexist == 0:
            cursor = connect.cursor()
            cursor.execute(
                "insert into users values(0, %s, %s, %s, NULL, 0, %s, %s, %s, 0)",
                (new_login, new_password, new_mail, new_username, new_user_image, new_user_thumbnail_image))
            connect.commit()
            cursor.close()
            connect.close()
            self.redirect('/login')
        else:
            bad = True
            connect.close()
            self.render('templates/register.html', bad=bad)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/login", LoginHandler),
        (r"/adminpanel", AdminPanelHandler),
        (r"/addpost", AddPostAdminHandler),
        (r"/post/([0-9]+)", ViewPostHandler),
        (r"/deauth", deauthHandler),
        (r"/profile", profileHandler),
        (r"/find", findHandler),
        (r"/register", registerHandler),
    ], **settings,
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"))


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
