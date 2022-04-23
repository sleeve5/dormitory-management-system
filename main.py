import sqlite3

from flask import render_template, request, Flask, url_for
from werkzeug.utils import redirect

sql_insert_userinfo = 'insert into userinfo(id,username,depart,idnumber,sex) values(?,?,?,?,?)'
app = Flask(__name__)


# 主页
@app.route('/home')
def home():
    return render_template('index.html')


# 项目介绍
@app.route('/about')
def about():
    return render_template('about.html')


# 使用md5加密(未使用)
def md5(string):
    c = string
    return c


"""

用户信息操作

"""


# 添加学生
@app.route('/AddUser0')
def AddUser0():
    return render_template('addUser.html')


@app.route('/AddUser', methods=['POST', 'GET'])
def AddUser():
    message = None
    if request.method == 'POST':
        try:
            id = request.form['id']
            username = request.form['username']
            depart = request.form['depart']
            idnumber = request.form['idnumber']
            sex = request.form['sex']
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute(sql_insert_userinfo, (id, username, depart, idnumber, sex))
                cur.execute('insert into user(id,password,role) values(?,?,?)', (id, md5(str(id)), '学生'))
                con.commit()
                message = id + "添加成功"
        except:
            con.rollback()
            message = "添加错误"

        finally:
            return render_template("result.html", msg=message)


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
    cur.execute("select * from userinfo where id=" + str(id))
    row = cur.fetchall()
    return render_template("listUserInfoWithId.html", row=row)


# 修改学生信息
@app.route('/modifyuser', methods=['POST', 'GET'])
def modifyuser():
    message = None
    try:
        id = request.form['id']
        username = request.form['username']
        depart = request.form['depart']
        idnumber = request.form['idnumber']
        sex = request.form['sex']
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("update userinfo set username=?, depart=?, idnumber=?, sex=? where id =?",
                        (username, depart, idnumber, sex, id))
            con.commit()
            message = id + "修改成功"
    except:
        con.rollback()
        message = "修改失败"

    finally:
        return render_template("result.html", msg=message)


# 删除学生信息
@app.route('/deleteuser/<int:id>')
def deleteuser(id):
    message = None
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            # 删除信息
            n = cur.execute("delete from userinfo where id =?", (id,))
            # 删寝室
            cur.execute("delete from course where id =?", (id,))
            # 删除密码
            cur.execute("delete from user where id =?", (id,))
            print(n.rowcount)
            con.commit()
            message = str(id) + "删除成功"
    except:
        con.rollback()
        message = '删除失败'
    finally:
        return render_template("result.html", msg=message)


"""

密码表的操作

"""


# 用户登录
@app.route('/')
def menu():
    return render_template('login+.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    message = None
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
                    message = '帐号或密码错误'
                    return render_template('login+.html', msg=message)
        except:
            print('登录时发生错误')
        finally:
            con.close()


# 修改密码
@app.route('/ModifyPasswd0')
def ModifyPasswd0():
    return render_template('modifypasswd.html')


@app.route('/ModifyPasswd', methods=['POST', 'GET'])
def ModifyPasswd():
    if request.method == 'POST':
        id = request.form['id']
        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        newpassword1 = request.form['newpassword1']
        if newpassword != newpassword1:
            return render_template('modifypasswd.html', msg='两次密码输入不同')
        try:
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                result = cur.execute("select * from user where id=? and password=?", (id, md5(oldpassword))).fetchall()
                if result:
                    updates = cur.execute('update user set password=? where id = ?', (md5(newpassword), id)).fetchall()
                    message = str(id) + '密码修改成功'
                    return render_template('login+.html', msg=message)
                else:
                    message = '密码修改失败'
                    return render_template('modifypasswd.html', msg=message)
        except:
            print('发生错误')
            con.rollback()
        finally:
            con.close()


"""

寝室操作

"""


# 添加课程
@app.route('/AddDormitory0')
def AddDormitory0():
    return render_template('adddormitory.html')


@app.route('/AddDormitory', methods=['POST', 'GET'])
def AddDormitory():
    message = None
    if request.method == 'POST':
        try:
            id = request.form['id']                         # 帐号/QQ号
            courseid = request.form['courseid']             # 未使用
            coursename = request.form['coursename']         # 寝室号
            teachername = request.form['teachername']       # 寝室长姓名
            score = request.form['score']                   # 用水量
            print(id, courseid, coursename, teachername, score)
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                print(id, courseid, coursename, teachername, score)
                cur.execute("insert into course(id,courseid,coursename,teachername,score) values(?,?,?,?,?)",
                            (id, courseid, coursename, teachername, score))
                con.commit()
                message = coursename + "寝室添加成功"
        except:
            con.rollback()
            message = "寝室添加失败"
        finally:
            return render_template("result.html", msg=message)


# 查看全部课程信息
@app.route('/listcourse')
def listcourse():
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from course left join userinfo on userinfo.id = course.id")
    rows = cur.fetchall()
    return render_template("listcourse.html", rows=rows)


# 删除寝室
@app.route('/deletedordormitory/<int:id>')
def deletedormitory(id):
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            n = cur.execute("delete from course where id =?", (id,))
            print(n.rowcount)
            con.commit()
            message = str(id) + "寝室删除失败"
    except:
        con.rollback()
        message = '寝室删除失败'
    finally:
        return render_template("result.html", msg=message)


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
