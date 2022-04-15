from flask import render_template, request, Flask, url_for
import sqlite3

from werkzeug.utils import redirect

sql_insert_userinfo = 'insert into userinfo(id,username,depart,idnumber,sex) values(?,?,?,?,?)'
app = Flask(__name__)


# 到主页
@app.route('/home')
def home():
    return render_template('index.html')


# 到about.html
@app.route('/abouthtml')
def abouthtml():
    return render_template('about.html')


# 使用md5加密密码比对
def md5(string):
    # 创建md5对象
    c = string
    return c


"""用户的信息userinfo表的操作"""


# 添加学生啊
@app.route('/addUser')
def addUser():
    return render_template('addUser.html')


@app.route('/adduserrec', methods=['POST', 'GET'])
def adduserrec():
    msg = None
    if request.method == 'POST':
        try:
            id = request.form['id']
            username = request.form['username']
            depart = request.form['depart']
            idnumber = request.form['idnumber']
            sex = request.form['sex']
            # print(id, username, depart, idnumber, sex)
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                # print(id,username,depart,idnumber,sex)
                cur.execute(sql_insert_userinfo, (id, username, depart, idnumber, sex))
                cur.execute('insert into user(id,password,role) values(?,?,?)', (id, md5(str(id)), '学生'))
                con.commit()
                msg = "Record  " + id + "  successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)


# 查看全部学生信息
@app.route('/listuserinfo')
def listuserinfo():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from userinfo")
    rows = cur.fetchall()
    return render_template("listUserInfo.html", rows=rows)


# 查询学生的信息
@app.route('/getuserinfo/<int:id>')
def getuserinfo(id):
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # print(id,type(id))
    cur.execute("select * from userinfo where id=" + str(id))
    row = cur.fetchall()
    return render_template("listUserInfoWithId.html", row=row)


# 更新学生信息
@app.route('/updateuserinfo', methods=['POST', 'GET'])
def updateuserinfo():
    global msg
    try:
        id = request.form['id']
        username = request.form['username']
        depart = request.form['depart']
        idnumber = request.form['idnumber']
        sex = request.form['sex']
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            # print(id, username, depart, idnumber, sex)
            cur.execute("update userinfo set username=?, depart=?, idnumber=?, sex=? where id =?",
                        (username, depart, idnumber, sex, id))
            con.commit()
            msg = "Update  " + id + "  successfully"
    except:
        con.rollback()
        msg = "Update operation failed"

    finally:
        return render_template("result.html", msg=msg)


# 删除学生信息 相当于注销账号
@app.route('/deleteuserinfo/<int:id>')
def deleteuserinfo(id):
    global msg
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            # 删除信息
            n = cur.execute("delete from userinfo where id =?", (id,))
            # 删课程
            cur.execute("delete from course where id =?", (id,))
            # 删除密码
            cur.execute("delete from user where id =?", (id,))
            print(n.rowcount)
            con.commit()
            msg = "Delete  " + str(id) + "  successfully"
    except:
        con.rollback()
        msg = 'Delete failed'
    finally:
        return render_template("result.html", msg=msg)


"""密码表的操作"""


# 登录得到用户的身份，出错就显示密码错了
@app.route('/')
def loginpage():
    return render_template('login+.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    msg = None
    if request.method == 'POST':
        try:
            id = request.form['id']
            password = request.form['password']
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                role = cur.execute("select role from user where id=? and password=?", (id, md5(password))).fetchall()
                print(role)
                if role:
                    return redirect(url_for('home'))
                else:
                    msg = '帐号或密码错误！'
                    return render_template('login+.html', msg=msg)
        except:
            print('error happens when handling login')
        finally:
            con.close()


# 修改密码
@app.route('/updatepwdpage')
def updatepwdpage():
    return render_template('updatepwd.html')


@app.route('/updatepwd', methods=['POST', 'GET'])
def updatepwd():
    msg = None
    if request.method == 'POST':
        # 没有登录
        id = request.form['id']
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        newpassword1 = request.form['newpassword1']
        # 两次填写的新密码不一样
        if newpassword != newpassword1:
            return render_template('updatepwd.html', msg='The passwords filled in twice are inconsistent')
        try:
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                result = cur.execute("select * from user where id=? and password=?", (id, md5(oldpassword))).fetchall()
                if result:
                    updates = cur.execute('update user set password=? where id = ?', (md5(newpassword), id)).fetchall()
                    msg = str(id) + ' password changed  successfully!'
                    return render_template('login+.html', msg=msg)
                else:
                    msg = 'password changed failed'
                    return render_template('updatepwd.html', msg=msg)
        except:
            print('error')
            con.rollback()
        finally:
            con.close()


"""课程信息的操作 course"""


# 添加课程啊
@app.route('/addcoursepage')
def addcoursepage():
    return render_template('addcourse.html')


@app.route('/addcourse', methods=['POST', 'GET'])
def addcourse():
    msg = None
    if request.method == 'POST':
        try:
            id = request.form['id']
            courseid = request.form['courseid']
            coursename = request.form['coursename']
            teachername = request.form['teachername']
            score = request.form['score']
            print(id, courseid, coursename, teachername, score)
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                print(id, courseid, coursename, teachername, score)
                cur.execute("insert into course(id,courseid,coursename,teachername,score) values(?,?,?,?,?)",
                            (id, courseid, coursename, teachername, score))
                con.commit()
                msg = "Record  " + coursename + "  successfully added"
        except:
            con.rollback()
            msg = "error in insert course operation"
        finally:
            return render_template("result.html", msg=msg)


# 查看全部课程信息
@app.route('/listcourse')
def listcourse():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from course left join userinfo on userinfo.id = course.id")
    rows = cur.fetchall()
    return render_template("listcourse.html", rows=rows)


# 删除学生的课程
@app.route('/deleteusercourse/<int:id>')
def deleteusercourse(id):
    global msg
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            n = cur.execute("delete from course where id =?", (id,))
            print(n.rowcount)
            con.commit()
            msg = "Delete  " + str(id) + " course  successfully"
    except:
        con.rollback()
        msg = 'Delete user\'s course failed'
    finally:
        return render_template("result.html", msg=msg)


# 删除课程
@app.route('/deletecourse/<courseid>')
def deletecourse(courseid):
    global msg
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            n = cur.execute("delete from course where courseid =?", (courseid,))
            print(n.rowcount)
            con.commit()
            msg = "Delete  " + courseid + "  successfully"
    except:
        con.rollback()
        msg = 'Delete ' + courseid + ' failed'
    finally:
        return render_template("result.html", msg=msg)


# 成绩分析
# 到成绩分析的页面里边去
@app.route('/analize')
def analize():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        "select course.id as id,userinfo.username as username,userinfo.sex as sex, sum(course.score) as sum,count(course.id) as count,sum(course.score)/count(course.id) as average from course left join userinfo on userinfo.id = course.id left join user on user.id = userinfo.id where role='学生' group by course.id order by sum(course.score)/count(course.id) desc")
    rows = cur.fetchall()
    return render_template("analize.html", rows=rows)


if __name__ == '__main__':
    app.run(debug=True)
