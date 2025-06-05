from datetime import datetime
from datetime import timedelta
import sqlite3
import csv
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from flask_session import Session
from flask_bcrypt import Bcrypt


#Database set up
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)

#Set up secret key for bcrypt
app.secret_key = '0i^[P[A*#N*F"->RLrk7LPgXsdP?K9VaV>z7]Ke<:=80jh=pPVp5%XcbtX(S[{/'
bcrypt = Bcrypt(app)

#Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)#Initialize session


#Default endpoint
@app.route("/")
def index():
    return render_template(
        'index.html',
        isNewUser = session.get('new_user', False),
        message=session.pop('message', None)
    )

#Scan in
@app.route("/scan-badge", methods = ['POST'])
def scan_badge():
    badge_num = request.form['badge-num']

    #Find user by comparing hashes
    user_id = checkUser(badge_num)

    if user_id:
        #User exists
        checkin_id = is_clocked_in(user_id)
        if checkin_id:
            clock_user_out(checkin_id)
            flash('Clocked out successfully', 'success')
        else:
            session['user_id'] = user_id
            return redirect(url_for('select_documents'))
    else:
        #New user
        session['new_user'] = True
        session['raw_badge'] = badge_num
        flash('New user detected', 'info')
    
    return redirect(url_for('index'))

        
        

#New user
@app.route("/new-user", methods = ['POST'])
def new_user():
    if 'raw_badge' not in session:
        return redirect(url_for('index'))

    #Hash badge ID
    hashed_badge = bcrypt.generate_password_hash(session['raw_badge']).decode('utf-8')

    department = request.form['department']

    with get_db() as con:
        try:
            cursor = con.execute('INSERT INTO users (hashed_badge, full_name, department) VALUES (?, ?, ?)',
                        (hashed_badge, request.form['full-name'], department))
            con.commit()

            user_id = cursor.lastrowid

            session['user_id'] = user_id 
            session.pop('raw_badge')
            session.pop('new_user')
            return redirect(url_for("select_documents"))
        except sqlite3.IntegrityError:
            flash('Badge already registered', 'error')


    return redirect(url_for("index"))



#Select documents
@app.route("/select-documents", methods=['GET', 'POST'])
def select_documents():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        documents = request.form.getlist('documents')
        user_details = getNameAndDepartment(session['user_id'])
        clock_user_in(session['user_id'], user_details['full_name'], documents)
        flash('Clocked in successfully', 'success')
        return redirect(url_for('index'))
    
    #Get request, show documents
    user_details = getNameAndDepartment(session['user_id'])

    department = user_details['department']

    documents = get_documents(department)

    return render_template('checkin.html', full_name=user_details['full_name'], department = department, document_list = documents)





#Check if user is clocked in
def is_clocked_in(user_id):
    with get_db() as con:
        result = con.execute('SELECT id FROM checkins WHERE user_id = ? AND outtime IS NULL', (user_id,)).fetchone()
        return result['id'] if result else None


#Clock user in
def clock_user_in(badge_id, name, documents):
    with get_db() as con:
        documents_str = ','.join(documents)
        con.execute("INSERT INTO checkins (user_id, name, intime, documents_accessed) VALUES (?, ?, datetime('now', 'localtime'), ?)", (badge_id, name, documents_str, ))
        con.commit()
        session["tag"] = None
        session["message"] = "Clocked In"

#Clock user out
def clock_user_out(check_in_id):
    with get_db() as con:
        con.execute("UPDATE checkins SET outtime = datetime('now', 'localtime') WHERE id = ?", (check_in_id,))
        con.commit()
        session["tag"] = None
        session["message"] = "Clocked Out"


#Check if user exists
def checkUser(badge_id):
    with get_db() as con:
        #Get ID of saved tag
        users = con.execute('SELECT id, hashed_badge FROM users').fetchall()
        for user in users:
            if bcrypt.check_password_hash(user['hashed_badge'], badge_id):
                return user['id']
    return None


#Get all documents to be accessed by department
def get_documents(department):
    with get_db() as con:
        documents = con.execute("SELECT document_name FROM documents WHERE department_name = ?", (department,)).fetchall()
        return [dict(row) for row in documents] if documents else []


#Get the users full name
def getNameAndDepartment(user_id):
    with get_db() as con:
        return con.execute('SELECT full_name, department FROM users WHERE id = ?', (user_id,)).fetchone()

def get_user_name(user_id):
    with get_db() as con:
        return con.execute("SELECT full_name FROM users WHERE id = ?", (user_id,)).fetchone()



#Write to excel
@app.route('/export/<table>', methods=['POST'])
def export(table):

    #Get date range and convert to SQLite format
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    #Convert to SQLite format
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    start_date = start_date - timedelta(days=1)
    
    #Get file path
    file_path = f"{table}.csv"

    with get_db() as con:
    #Get all records for table
        savedData = con.execute('SELECT name, intime, outtime, documents_accessed FROM checkins WHERE date(intime) BETWEEN ? AND ? ORDER BY intime', (start_date, end_date))
        headers = [description[0] for description in savedData.description]

    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(savedData.fetchall())


    return send_file(file_path, as_attachment=True)


