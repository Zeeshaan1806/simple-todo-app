from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "mysecretkey123"  # VULNERABILITY 1: Hardcoded secret key

def init_db():
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS todos
                 (id INTEGER PRIMARY KEY, task TEXT, completed BOOLEAN)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    # Get all todos from database
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute("SELECT * FROM todos")
    todos = c.fetchall()
    conn.close()
    
    # VULNERABILITY 2: SQL Injection vulnerability in search
    search = request.args.get('search', '')
    if search:
        conn = sqlite3.connect('todos.db')
        c = conn.cursor()
        # Vulnerable SQL query - no parameterization
        query = f"SELECT * FROM todos WHERE task LIKE '%{search}%'"
        c.execute(query)
        todos = c.fetchall()
        conn.close()
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>To do list</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
                .task { margin-bottom: 10px; padding: 10px; border: 1px solid #ddd; }
                .completed { text-decoration: line-through; background-color: #f9f9f9; }
                form { margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <h1>Simple Todo App</h1>
            
            <form method="GET">
                <input type="text" name="search" placeholder="Search tasks" value="{{ search }}">
                <button type="submit">Search</button>
            </form>
            
            <form action="/add" method="POST">
                <input type="text" name="task" placeholder="Add a new task" required>
                <button type="submit">Add Task</button>
            </form>
            
            <h2>Tasks</h2>
            {% for todo in todos %}
                <div class="task {% if todo[2] %}completed{% endif %}">
                    <span>{{ todo[1] }}</span>
                    {% if not todo[2] %}
                        <a href="/complete/{{ todo[0] }}">Mark Complete</a>
                    {% endif %}
                </div>
            {% endfor %}
        </body>
        </html>
    ''', todos=todos, search=search)

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute("INSERT INTO todos (task, completed) VALUES (?, ?)", (task, False))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/complete/<int:id>')
def complete(id):
    conn = sqlite3.connect('todos.db')
    c = conn.cursor()
    c.execute("UPDATE todos SET completed = TRUE WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    # 
    app.run(debug=False, host='0.0.0.0', port=5000)