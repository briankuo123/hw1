import re, sqlite3, hashlib 
from flask import Flask, render_template, url_for, request, redirect, make_response
app = Flask(__name__)

def hash(s):
    ret = hashlib.md5(s.encode())
    return ret.hexdigest()

def register_action():
    username = request.form.get('username', '')
    email = request.form.get('email', '')
    password1 = request.form.get('password1', '')
    password2 = request.form.get('password2', '')

    if not username:
        return '請輸入username'
    elif not email:
        return '請輸入email'
    elif not password1:
        return '請輸入password'
    elif not password2:
        return '請輸入password'
    elif len(password1)<4:
        return '密碼必須大於4碼'
    elif not password1==password2:
        return '兩次密碼必須相符'

    password1 = hash(password1)
    con = sqlite3.connect('mywebsite.db')
    cur = con.cursor()
    cur.execute(f'SELECT * FROM user WHERE `email`="{email}"')
    queryresult = cur.fetchall()
    if queryresult:
        return 'email重複，請使用另一個email'
    cur.execute(f'SELECT * FROM user WHERE `username`="{username}"')
    queryresult = cur.fetchall()
    if queryresult:
        return 'username重複，請使用另一個usernme'
    # Insert a row of data
    cur.execute(f"INSERT INTO user (`username`, `email`, `password`) VALUES ('{username}','{email}','{password1}')")
    # Save (commit) the changes
    con.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()
    return '註冊成功'

def do_login(email):
    con = sqlite3.connect('mywebsite.db')
    cur = con.cursor()
    querydata = cur.execute("SELECT username FROM user WHERE email='"+email+"'")
    con.close
    result=querydata.fetchone()
    resp=make_response(render_template('user.html', username = result[0], title = result[0]+"的登入畫面"))
    resp.set_cookie('login', 'ok')
    if result:
        return resp


def login_check(email,password):
    password=hash(password)
    con = sqlite3.connect('mywebsite.db')
    cur = con.cursor()
    querydata = cur.execute("SELECT * FROM user WHERE `email`='"+email+"'AND `password`='"+password+"'")
    results = cur.fetchall()
    con.close
    if results:
        return True
    else:
        return False
    


@app.route('/')
def index():
    return render_template('index.html', title = "我的作業")

@app.route('/user/<username>')
def show_user_profile(username):
    return render_template('user.html', username = username)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        # return request.form.get('username', '')+';'+request.form.get('email', '')
        return register_action()
    else:
        # username = request.args.get('username', '') if request.args.get('username', '') else ''
        username = request.args.get('username', '')
        email = request.args.get('email', '')
        return render_template('register.html', username=username, email=email, title = "我的作業")

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if login_check(request.form['mailbar'],request.form['pwbar']):
            return do_login(request.form['mailbar'])
        else:
            error = 'Invalid username/password'
            resp=make_response(render_template('login_fail.html', title = "我的作業"))
            resp.set_cookie('login','fail')
            return resp
    else:
        return render_template('login.html', title = "我的作業")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title = "我的作業"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html', title = "我的作業"), 500


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
