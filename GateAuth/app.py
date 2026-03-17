from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "gatepass_secret"

def get_db():
    return sqlite3.connect("database.db")

# Home page route
@app.route('/')
def home():
    return render_template("home.html")

# New account page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        role = request.form['role']
        password = request.form['password']

        db = get_db()
        db.execute(
            "INSERT INTO users(name,email,contact,role,password) VALUES (?,?,?,?,?)",
            (name, email, contact, role, password)
        )
        db.commit()
        return redirect('/')
    return render_template("register.html")

# Login page route 
@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=? AND password=? AND role=?",
            (email, password, role)
        ).fetchone()

        if user:
            session['user_id'] = user[0]
            session['role'] = role
            return redirect(f'/{role}_dashboard')

    return render_template(f"{role}_login.html")

# Student dashboard page route
@app.route('/student_dashboard', methods=['GET', 'POST'])
def student_dashboard():
    if request.method == 'POST':
        reason = request.form['reason']
        out_date = request.form['out_date']
        in_date = request.form['in_date']

        db = get_db()
        db.execute(
            "INSERT INTO gate_pass(student_id,reason,out_date,in_date) VALUES (?,?,?,?)",
            (session['user_id'], reason, out_date, in_date)
        )
        db.commit()

    passes = get_db().execute(
        "SELECT * FROM gate_pass WHERE student_id=?",
        (session['user_id'],)
    ).fetchall()

    return render_template("student_dashboard.html", passes=passes)

# Parent dashboard page route
@app.route('/parent_dashboard')
def parent_dashboard():
    passes = get_db().execute("SELECT * FROM gate_pass").fetchall()
    return render_template("parent_dashboard.html", passes=passes)

@app.route('/parent_approve/<int:pid>')
def parent_approve(pid):
    db = get_db()
    db.execute(
        "UPDATE gate_pass SET parent_permission='APPROVED' WHERE pass_id=?",
        (pid,)
    )
    db.commit()
    return redirect('/parent_dashboard')

# Warden dashboard page route
@app.route('/warden_dashboard')
def warden_dashboard():
    passes = get_db().execute(
        "SELECT * FROM gate_pass WHERE parent_permission='APPROVED'"
    ).fetchall()
    return render_template("warden_dashboard.html", passes=passes)

@app.route('/warden_approve/<int:pid>')
def warden_approve(pid):
    db = get_db()
    db.execute(
        "UPDATE gate_pass SET warden_status='APPROVED' WHERE pass_id=?",
        (pid,)
    )
    db.commit()
    return redirect('/warden_dashboard')

# Admin dashboard page route
@app.route('/admin_dashboard')
def admin_dashboard():
    passes = get_db().execute("SELECT * FROM gate_pass").fetchall()
    return render_template("admin_dashboard.html", passes=passes)


if __name__ == "__main__":
    app.run(debug=True)
