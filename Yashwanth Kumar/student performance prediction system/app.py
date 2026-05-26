from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "student_secret_key"


# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        study REAL,
        attendance REAL,
        previous_score REAL,
        sleep REAL,
        papers REAL,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# HOME
# =========================
@app.route('/')
def home():
    return redirect(url_for('login'))


# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == "" or password == "":
            return render_template(
                "register.html",
                msg="Please enter username and password"
            )

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                msg="Username already exists"
            )

    return render_template("register.html")


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == "" or password == "":
            return render_template(
                "login.html",
                msg="Please enter username and password"
            )

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('dashboard'))

        return render_template(
            "login.html",
            msg="Invalid Username or Password"
        )

    return render_template("login.html")


# =========================
# DASHBOARD
# =========================
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM history WHERE username=?",
        (username,)
    )
    total = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM history WHERE username=? AND result='Pass'",
        (username,)
    )
    passed = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM history WHERE username=? AND result='Fail'",
        (username,)
    )
    failed = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total=total,
        passed=passed,
        failed=failed
    )


# =========================
# PREDICT
# =========================
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        try:
            study = float(request.form.get("study", 0) or 0)
            attendance = float(request.form.get("attendance", 0) or 0)
            previous_score = float(request.form.get("previous_score", 0) or 0)
            sleep = float(request.form.get("sleep", 0) or 0)
            papers = float(request.form.get("papers", 0) or 0)

            score = (
                (study * 5) +
                (attendance * 0.3) +
                (previous_score * 0.4) +
                (sleep * 2) +
                (papers * 1.5)
            )

            if attendance >= 75 and previous_score >= 40 and score >= 80:
                result = "Pass"
            else:
                result = "Fail"

            conn = sqlite3.connect("database.db")
            cur = conn.cursor()

            cur.execute("""
            INSERT INTO history(
                username,
                study,
                attendance,
                previous_score,
                sleep,
                papers,
                result
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session['username'],
                study,
                attendance,
                previous_score,
                sleep,
                papers,
                result
            ))

            conn.commit()
            conn.close()

            return render_template(
                "predict.html",
                prediction_text=result
            )

        except Exception as e:
            return render_template(
                "predict.html",
                prediction_text=str(e)
            )

    return render_template("predict.html")


# =========================
# HISTORY
# =========================
@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM history
        WHERE username=?
        ORDER BY id DESC
    """, (session['username'],))

    rows = cur.fetchall()
    conn.close()

    return render_template("history.html", rows=rows)


# =========================
# DELETE SINGLE HISTORY
# =========================
@app.route('/delete_history/<int:id>')
def delete_history(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM history WHERE id=? AND username=?",
        (id, session['username'])
    )

    conn.commit()
    conn.close()

    return redirect(url_for('history'))


# =========================
# EXCEL
# =========================
@app.route('/excel')
def excel():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect("database.db")

    df = pd.read_sql_query(
        """
        SELECT study,
               attendance,
               previous_score,
               sleep,
               papers,
               result
        FROM history
        WHERE username=?
        ORDER BY id DESC
        """,
        conn,
        params=(session['username'],)
    )

    conn.close()

    df.columns = [
        "Study Hours",
        "Attendance",
        "Previous Score",
        "Sleep Hours",
        "Papers",
        "Result"
    ]

    file_name = "Student_History.xlsx"
    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True,
        download_name="Student_History.xlsx"
    )


# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True)