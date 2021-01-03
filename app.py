from flask_table import Table, Col, LinkCol, ButtonCol
from flask import Flask, render_template, request, redirect, url_for
from tools.database import UserData

app = Flask(__name__)

@app.route('/PowerOff/<uuid>')
def poweroff(uuid):
    return uuid

@app.route('/PowerOn/<uuid>')
def poweron(uuid):
    return uuid

@app.route('/controlpanel')
def admin_panel():
    database = UserData(server='192.168.17.131',
                    user='root',
                    password='12qwasZX',
                    database='core_labs')
    headings = ('owner mail', 'owner uuid', 'started on', 'expire on', 'ports', 'running on', 'lab gns3 id', 'status')
    all_labs = database.get_all_labs()
    data = database.get_formatted_lab_data(all_labs)

    return render_template('admin_panel.html', headings=headings, data=data)


@app.route('/users/', methods=["POST", "GET"])
def user_land():
    if request.method == 'GET':
        return render_template('user_landing.html')
    elif request.method == 'POST':
        user_mail=request.form['email']
        return redirect(url_for('user_panel', user_mail=user_mail))

@app.route('/users/<user_mail>')
def user_panel(user_mail):
    database = UserData(server='192.168.17.131',
                        user='root',
                        password='12qwasZX',
                        database='core_labs')
    headings = ('new_lab_id', 'started on', 'expire on', 'ports', 'running on', 'status')
    users_labs = database.get_users_labs(user_mail)
    data = database.get_formatted_user_lab_data(users_labs)
    return render_template('user_panel.html', headings=headings, data=data)



if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port='7000')