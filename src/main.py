import tornado.ioloop
import tornado.web
import sqlite3
import os

# データベース接続を設定
def get_db():
    db = sqlite3.connect('bbs.db')
    db.row_factory = sqlite3.Row  # Rowオブジェクトで結果を扱うようにする
    return db

# データベースの初期化
def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS threads (
                thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(thread_id) REFERENCES threads(thread_id)
            )
        ''')

# アプリケーションのルート
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        db = get_db()
        cursor = db.execute('SELECT * FROM threads ORDER BY created_at DESC')
        threads = cursor.fetchall()
        self.render("index.html", threads=threads)

# スレッドの投稿表示
class ThreadHandler(tornado.web.RequestHandler):
    def get(self, thread_id):
        db = get_db()
        thread = db.execute('SELECT * FROM threads WHERE thread_id = ?', (thread_id,)).fetchone()
        posts = db.execute('SELECT * FROM posts WHERE thread_id = ? ORDER BY created_at', (thread_id,)).fetchall()
        self.render("thread.html", thread=thread, posts=posts)

    def post(self, thread_id):
        message = self.get_argument("message")
        db = get_db()
        db.execute('INSERT INTO posts (thread_id, message) VALUES (?, ?)', (thread_id, message))
        db.commit()
        self.redirect(f"/thread/{thread_id}")

# スレッドの作成
class CreateThreadHandler(tornado.web.RequestHandler):
    def post(self):
        title = self.get_argument("title")
        db = get_db()
        db.execute('INSERT INTO threads (title) VALUES (?)', (title,))
        db.commit()
        self.redirect("/")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/thread/([0-9]+)", ThreadHandler),
        (r"/create", CreateThreadHandler),
    ], debug=True, template_path="templates")

if __name__ == "__main__":
    if not os.path.exists('bbs.db'):
        init_db()
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
