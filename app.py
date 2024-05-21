from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to initialize the database
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                expiration_date TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize the database on app startup
init_db()

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Admin setup
@app.route('/setup_admin', methods=['GET', 'POST'])
def setup_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('setup_admin.html')

# Admin login
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM admin WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
        if user:
            return redirect(url_for('admin_dashboard'))
    return render_template('admin.html')

# Admin dashboard
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'delete':
            user_id = request.form['user_id']
            # Delete user logic here
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                conn.commit()
            return redirect(url_for('admin_dashboard'))

    # Fetch users from the database (replace this with actual database integration)
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()

    return render_template('admin_dashboard.html', users=users)

# Create user route
@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        expiration_date = request.form['expiration_date']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (username, password, expiration_date) VALUES (?, ?, ?)',
                           (username, password, expiration_date))
            conn.commit()

        return redirect(url_for('admin_dashboard'))

    return redirect(url_for('admin_dashboard'))

# Delete user route
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
    return redirect(url_for('admin_dashboard'))

# Edit user route
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Fetch user details from the database based on user_id
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()

    if request.method == 'POST':
        # Update user details in the database
        username = request.form['username']
        password = request.form['password']
        expiration_date = request.form['expiration_date']

        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET username = ?, password = ?, expiration_date = ? WHERE id = ?',
                           (username, password, expiration_date, user_id))
            conn.commit()

        return redirect(url_for('admin_dashboard'))

    return render_template('edit_user.html', user=user)

# Client login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
        if user:
            return redirect(url_for('client_dashboard'))
    return render_template('login.html')

# Client dashboard
@app.route('/client_dashboard')
def client_dashboard():
    return render_template('client_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
