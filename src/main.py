import tornado.ioloop
import tornado.web
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('db/todos.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL
        );
    ''')
    conn.commit()
    return conn

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM todos')
        todos = c.fetchall()
        conn.close()
        self.render("index.html", title="ToDo List", todos=[{'id': row[0], 'title': row[1]} for row in todos])

class NewTodoHandler(tornado.web.RequestHandler):
    def post(self):
        title = self.get_argument("title", None)
        if title:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('INSERT INTO todos (title) VALUES (?)', (title,))
            conn.commit()
            conn.close()
        self.redirect("/")

class DeleteTodoHandler(tornado.web.RequestHandler):
    def post(self):
        todo_id = self.get_argument("id", None)

        if todo_id:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
            conn.commit()
            conn.close()
        self.redirect("/")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/new", NewTodoHandler),
        (r"/delete", DeleteTodoHandler),
    ], debug=True, template_path="templates")

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Server running on http://localhost:8888/")
    tornado.ioloop.IOLoop.current().start()
