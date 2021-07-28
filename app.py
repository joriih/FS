from flask import Flask, render_template, request, g, session, redirect, url_for, jsonify
from flask.helpers import url_for
from flask_cors import CORS
from sqlalchemy import create_engine
from werkzeug.utils import redirect
from ldap import *
from employee import *
import pymysql
import sqlite3
import pandas as pd
import excel
import datetime
import flask


pd.options.display.float_format = '{:.0f}'.format
app = Flask(__name__)
app.secret_key = '1a2b3c4d5e'
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config.from_pyfile('config.py')

database = create_engine(app.config['DB_URL'], encoding = 'utf-8')
app.database = database


@app.route("/", methods = ['GET'])
def index():
    if 'loggedin' in session:
        return render_template('index.html', username = session['username'])
    return redirect(url_for('login'))


# 로그인 페이지 출력
@app.route('/login', methods = ['GET'])
def login():
    session.pop('username',None)
    session.pop('loggedin', None)
    return render_template(
        'login.html'
    )


# captchaKey, image return
@app.route('/captcha', methods = ['GET'])
def captcha():
    if request.method == 'GET':

        response = getcaptcha()
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# captcha 로그인 시도 및 토큰 발행
@app.route('/signin2', methods = ['POST'])
def signin2():
    if request.method == 'POST':

        response = signinwithcaptcha(request.get_json())
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# LDAP 로그인 시도
@app.route('/signin', methods = ['POST'])
def signin():
    if request.method == 'POST':
        # json.dumps(dict): dict('') -> json("")
        # json.loads(json): json("") -> dict('')
        
        # request.get_json(): dict object
        response = signinwithotp(request.get_json())
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# OTP 확인 및 토큰 발행
@app.route('/verify', methods = ['POST'])
def verify():
    if request.method == 'POST':
        response = verifywithotp(request.get_json())
        if (response['returnCode']) == "OK":
            session['loggedin'] = True
            session['username'] = response['username']
            redirect(url_for("index"))
        else:
            redirect(url_for("login"))
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# 토큰 연장
@app.route('/generateNewToken', methods = ['POST'])
def genNewToken():
    if request.method == 'POST':
        
        response = generateNewToken()
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# 토큰 연장
@app.route('/generateNewToken2', methods = ['POST'])
def genNewToken2():
    if request.method == 'POST':
        
        response = generateNewToken2(request)
        return response


# CRUD - Read
@app.route('/employee/getEmployees', methods = ['GET', 'POST'])
def getEmployees():
    if request.method in ['GET', 'POST']:
        
        response = userlist(app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# CRUD - Create
@app.route('/employee/addNewEmployee', methods = ['POST'])
def addNewEmployee():
    if request.method == 'POST':
        
        response = add_user(request.get_json(), app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# CRUD - Update
@app.route('/employee/updateEmployeeInfo', methods = ['POST'])
def updateEmployeeInfo():
    if request.method == 'POST':
        
        response = update_user(request.get_json(), app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)


# CRUD - Delete
@app.route('/employee/deleteEmployee', methods = ['POST'])
def deleteEmployee():
    if request.method == 'POST':
        
        response = delete_user(request.get_json(), app)
        return response

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)

# AppDu health_check 함수 절대 지우지 말것 
# health_check
@app.route('/health_check', methods = ['GET'])
def health_check():
    if request.method == 'GET':

        return json.dumps({'returnCode': 'OK'})

    else:
        return json.dumps({'returnCode': 'NG', 'message': 'Method ' + request.method + ' not allowed.'}, status=405)

@app.route('/hy_pass', methods=['POST'])
def hy_pass_():
    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    pass_ = "업셀링"
    if not True in [badchar in id or badchar in date_ or badchar in num for badchar in "\n'\""]:
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO pass_shooting (id, date_, num, pass_shooting) VALUES ('{}','{}','{}','{}')".format(id, date_, num, pass_)
        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT * FROM pass_shooting WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND pass_shooting = '{}'".format(id, date_, num, pass_)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/hy_shooting', methods=['POST'])
def hy_shooting():
    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    if not True in [badchar in id or badchar in date_ or badchar in num for badchar in "\n'\""]:
        shooting = "해지징후"
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO pass_shooting (id, date_, num, pass_shooting) " \
            "VALUES ('{}','{}','{}','{}')".format(id, date_, num, shooting)
        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT * FROM pass_shooting WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND pass_shooting = '{}'".format(id, date_, num, shooting)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/re_pass', methods=['POST'])
def re_pass_():
    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    
    if not True in [badchar in id or badchar in date_ or badchar in num for badchar in "\n'\""]:
        pass_ = "업셀링"

        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO pass_shooting (id, date_, num, pass_shooting) VALUES ('{}','{}','{}','{}')".format(id, date_, num, pass_)
        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT * FROM pass_shooting WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND pass_shooting = '{}'".format(id, date_, num, pass_)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/re_shooting', methods=['POST'])
def re_shooting():
    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    
    if not True in [badchar in id or badchar in date_ or badchar in num for badchar in "\n'\""]:
        shooting = "해지징후"
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO pass_shooting (id, date_, num, pass_shooting) " \
            "VALUES ('{}','{}','{}','{}')".format(id, date_, num, shooting)
        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT * FROM pass_shooting WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND pass_shooting = '{}'".format(id, date_, num, shooting)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/no_shooting', methods=['POST'])
def no_shooting():
    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    
    if not True in [badchar in id or badchar in date_ or badchar in num for badchar in "\n'\""]:
        shooting = "해지징후"
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO pass_shooting (id, date_, num, pass_shooting) " \
            "VALUES ('{}','{}','{}','{}')".format(id, date_, num, shooting)
        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT * FROM pass_shooting WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND pass_shooting = '{}'".format(id, date_, num, shooting)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/no_care', methods=['POST'])
def no_care():

    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    care = request.form['care']
    
    if not True in [badchar in id or badchar in date_ or badchar in num or badchar in care for badchar in "\n'\""]:
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO care (id, date_, num, care) " \
            "VALUES ('{}','{}','{}','{}')".format(id, date_, num, care)
        curs.execute(sql)
        conn.commit()
        sql2 = "SELECT * FROM care WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND care = '{}'".format(id, date_, num, care)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/no_pass', methods=['POST'])
def no_pass():
    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    if not True in [badchar in id or badchar in date_ or badchar in num for badchar in "\n'\""]:
        pass_ = "업셀링"

        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO pass_shooting (id, date_, num, pass_shooting) VALUES ('{}','{}','{}','{}')".format(id, date_,
                                                                                                            num, pass_)
        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT * FROM pass_shooting WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND pass_shooting = '{}'".format(
            id, date_, num, pass_)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/re_care', methods=['POST'])
def re_care():
    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    care = request.form['care']
    if not True in [badchar in id or badchar in date_ or badchar in num or badchar in care for badchar in "\n'\""]:

        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO care (id, date_, num, care) " \
            "VALUES ('{}','{}','{}','{}')".format(id, date_, num, care)
        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT * FROM care WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND care = '{}'".format(id, date_, num, care)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)

@app.route('/hy_care', methods=['POST'])
def hy_care():

    id = request.form['username']
    date_ = request.form['id'].split(",")[0]
    num = request.form['id'].split(",")[1]
    care = request.form['care']
    if not True in [badchar in id or badchar in date_ or badchar in num or badchar in care for badchar in "\n'\""]:
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO care (id, date_, num, care) " \
            "VALUES ('{}','{}','{}','{}')".format(id, date_, num, care)
        curs.execute(sql)
        conn.commit()
        sql2 = "SELECT * FROM care WHERE id = '{}' AND date_ = '{}' AND num = '{}' AND care = '{}'".format(id, date_, num, care)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)


@app.route('/request_history', methods=['POST'])
def request_history():
    id = request.form['username']
    sa_type = request.form['sa_type']
    num = request.form['num']
    service_type = request.form['service_type']
    region = request.form['region']
    if not True in [badchar in id or badchar in sa_type or badchar in num or badchar in service_type or badchar in region for badchar in "\n'\""]:

        now = time.localtime()
        now_time = "%02d/%02d %02d:%02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)

        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql = "INSERT INTO driq_request (id, date_, request_type, num, service_type, region, rpa_check) " \
            "VALUES ('{}','{}','{}','{}', '{}', '{}', '{}')".format(id, now_time , sa_type, num, service_type, region, "N")

        curs.execute(sql)
        conn.commit()

        sql2 = "SELECT  count(*) FROM `driq_request` WHERE date_ <= '{}' AND rpa_check = 'N' ORDER BY date_".format(now_time)
        curs.execute(sql2)
        rows = curs.fetchall()

        sql2 = "SELECT date_, num, service_type, region FROM driq_request WHERE id = '{}' AND rpa_check = 'Y' ORDER BY date_ LIMIT 10".format(id)
        curs.execute(sql2)
        rows2 = curs.fetchall()
        return jsonify(rows)

@app.route('/only_history', methods=['POST'])
def only_history():
    id = request.form['id']
    if not True in [badchar in id for badchar in "\n'\""]:

        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        sql2 = "SELECT date_, num, service_type, region FROM driq_request WHERE id = '{}' AND rpa_check = 'YY' ORDER BY date_ DESC".format(id)
        curs.execute(sql2)
        rows = curs.fetchall()
        return jsonify(rows)


@app.route('/all_history', methods=['POST'])
def all_history():
    id = ""
    conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
    curs = conn.cursor()
    sql2 = "SELECT id, date_, num, service_type, region FROM driq_request WHERE rpa_check = 'YY' ORDER BY date_ DESC".format(id)
    curs.execute(sql2)
    rows = curs.fetchall()
    return jsonify(rows)

@app.route('/request_result', methods=['POST'])
def request_result():
    id = request.form['username']
    clicked_id = request.form['clicked_id']
    
    if not True in [badchar in id or badchar in clicked_id for badchar in "\n'\""]:
        date_ = clicked_id.split(",")[0]
        num = clicked_id.split(",")[1]

        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        # sql2 = "SELECT real_hybrid, date_, num FROM driq_result WHERE id = '{}' AND date_ = '{}' AND num = '{}'".format(id, date_, num)
        sql2 = "SELECT real_hybrid, date_, num FROM driq_result WHERE date_ = '{}' AND num = '{}'".format(date_,num)
        curs.execute(sql2)
        rows = curs.fetchall()
        if rows[0][0] == "Real":
            # sql3 = "SELECT * FROM driq_result_app_real WHERE id = '{}' AND date_ = '{}' AND num = '{}'".format(id, date_, num)
            sql3 = "SELECT * FROM driq_result_app_real WHERE date_ = '{}' AND num = '{}'".format(date_,num)
            curs.execute(sql3)
            rows2 = curs.fetchall()

            conn2 = sqlite3.connect('trest.db')
            curs2 = conn2.cursor()
            sql4 = "SELECT * FROM trest WHERE num like '{}%' ".format(num[:8])
            curs2.execute(sql4)
            rows3 = curs2.fetchall()


            if rows3 == []:
                rows3 = ["nothing", "nothing", "nothing","nothing", "nothing", "nothing","nothing", "nothing", "nothing","nothing", "nothing"]
            return jsonify((rows2, rows3))

        elif rows[0][0] == "Hybrid":
            # sql3 = "SELECT * FROM driq_result_app_hybrid WHERE id = '{}' AND date_ = '{}' AND num = '{}'".format(id, date_,num)
            sql3 = "SELECT * FROM driq_result_app_hybrid WHERE date_ = '{}' AND num = '{}'".format(date_,num)
            curs.execute(sql3)
            rows2 = curs.fetchall()
            conn2 = sqlite3.connect('trest.db')
            curs2 = conn2.cursor()
            sql4 = "SELECT * FROM trest WHERE num like '{}%' ".format(num[:8])
            curs2.execute(sql4)
            rows3 = curs2.fetchall()
            if rows3 == []:
                rows3 = ["nothing", "nothing", "nothing","nothing", "nothing", "nothing","nothing", "nothing", "nothing","nothing", "nothing"]
            return jsonify((rows2, rows3))

        elif rows[0][0] == "no":
            rows2 = ["nothing"]
            conn2 = sqlite3.connect('trest.db')
            curs2 = conn2.cursor()
            sql4 = "SELECT * FROM trest WHERE num like '{}%' ".format(num[:8])
            curs2.execute(sql4)
            rows3 = curs2.fetchall()
            if rows3 == []:
                rows3 = ["nothing", "nothing", "nothing","nothing", "nothing", "nothing","nothing", "nothing", "nothing","nothing", "nothing"]
            return jsonify((rows2, rows3))
        else :
            return jsonify("nothing")

@app.route('/rpa_sql', methods=['GET', 'POST'])
def rpa_sql():
    return render_template('rpa_sql.html')  #

@app.route('/rpa_select', methods=['GET', 'POST'])
def rpa_select():
    conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
    curs = conn.cursor()
    sql2 = "select * from driq_request where rpa_check='N'"
    curs.execute(sql2)
    rows = curs.fetchall()
    return render_template('rpa_select.html', rows=rows)  #

@app.route('/rpa_inup', methods=['POST'])
def rpa_inup():
    request_update = request.form['request_update']
    real_insert = request.form['real_insert']
    hybrid_insert = request.form['hybrid_insert']
    real_hybrid_result = request.form['real_hybrid_result']
    if not True in [badchar in request_update or badchar in real_insert or badchar in hybrid_insert or badchar in real_hybrid_result for badchar in "\n'\""]:
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        curs.execute(request_update)
        conn.commit()
        curs.execute(real_hybrid_result)
        conn.commit()

        if real_insert =="":
            curs.execute(hybrid_insert)
            conn.commit()
        elif hybrid_insert =="":
            curs.execute(real_insert)
            conn.commit()
        else:
            pass

        return jsonify("ghdlt")  #

@app.route('/toast', methods=['POST'])
def toast():
    id = request.form['username']
    if not True in [badchar in id for badchar in "\n'\""]:
        sql = "SELECT count(*) FROM driq_request WHERE rpa_check = 'Y' and id = '{}' order by date_ desc".format(id)

        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()
        curs.execute(sql)
        rows = curs.fetchone()

        sql2 = "UPDATE driq_request SET rpa_check = 'YY' WHERE id = '" + id +"' and rpa_check='Y'"
        curs.execute(sql2)
        conn.commit()

        return jsonify(rows, rows)

@app.route('/test333')
def test333():
    return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if 'loggedin' in session:
        if request.method == 'POST':
            f = request.files['file']
            if not True in [badchar in f for badchar in "\n'\""]:
                print(f.filename)
                f.save(f.filename)

                conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
                curs = conn.cursor()
                a = excel.excel(f.filename)
                for i in a:
                    now = time.localtime()
                    now_time = "%02d/%02d %02d:%02d" % (now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)

                    sql = "INSERT INTO driq_request (id, date_, request_type, num, service_type, region, rpa_check) " \
                        "VALUES ('{}','{}','{}','{}', '{}', '{}', '{}')".format(session['username'], now_time, i[0], str(int(i[1])), i[3], i[2], "E")
                    curs.execute(sql)
                    conn.commit()

                sql2 = "INSERT INTO excel (id, date_, cnt) VALUES ('{}', '{}', '{}')".format(session['username'], now_time, len(a))
                curs.execute(sql2)
                conn.commit()
                return render_template('confirm.html')
        else :
            return render_template('confirm.html')
    return redirect(url_for('login'))

@app.route('/uploader/progress', methods = ['GET', 'POST'])
def progress():
    id = session['username']
    
    if not True in [badchar in id for badchar in "\n'\""]:
        conn = pymysql.connect(host='10.217.166.215', user='gc', passwd='Driq1234', port=40273, db='gc')
        curs = conn.cursor()

        sql2 = "SELECT cnt, date_ FROM excel WHERE id = '{}' order by date_ desc".format(id)
        
        curs.execute(sql2)
        d = curs.fetchone()
        all = d[0]
        date_ = d[1]
        print(all, date_)

        sql = "SELECT count(*) FROM driq_request WHERE rpa_check = 'EY' and id = '{}' and date_ = '{}' order by date_ desc".format(id,date_)
        curs.execute(sql)
        dd = curs.fetchone()
        now = dd[0]
        
        percent = int(now) / int(all) * 100
        print(now, all, percent)

        sql3 = "SELECT request_type, num, service_type, region, rpa_check FROM driq_request WHERE id = '{}' and date_ = '{}' order by date_ desc".format(id,date_)
        curs.execute(sql3)
        rows = curs.fetchall()
        print(rows)
        return jsonify(now, all, percent, rows)

# Flask 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0')
    #app.run(host='0.0.0.0',port=8000,debug=True)
