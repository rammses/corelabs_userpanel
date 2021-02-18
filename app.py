from flask import Flask, render_template, request, redirect, url_for, session
from tools.database import UserData
import flask_login
import requests

app = Flask(__name__)
app.secret_key = '12qwasZX'  # Change this!

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

users = {'mesut@mikronet.net': {'password': '12qwasZX'}}


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request1):
    email = request1.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request1.form['password'] == users[email]['password']

    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
               <form action='login' method='POST'>
                <input type='text' name='email' id='email' placeholder='email'/>
                <input type='password' name='password' id='password' placeholder='password'/>
                <input type='submit' name='submit'/>
               </form>
               '''
    email = request.form['email']

    if request.form['password'] == users[email]['password']:
        user = User()
        user.id = email
        flask_login.login_user(user)
        if 'url' in session:
            return redirect(session['url'])
        return redirect(url_for('protected'))
        # return redirect(url_for('protected'))

    return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'


@login_manager.unauthorized_handler
def unauthorized_handler():
    session['url'] = request.path
    return redirect('/login')


@app.route('/PowerOff/<uuid>', methods=['GET'])
def poweroff(uuid):
    if request.method == 'GET':
        servername = 'https://api.corelabs.com.tr/PowerOff/'
        print("stopping", uuid)
        try:
            response = requests.post(servername + uuid, verify=False)
            print(response, response.content)
        except Exception as e:
            detail = {'success': 'False',
                      'errors': e}
            return detail
        finally:
            print("successfully power off :", uuid )
            succes = 'success'
            return succes


@app.route('/PowerOn/<uuid>', methods=['GET'])
def poweron(uuid):
    if request.method == 'GET':
        servername = 'https://api.corelabs.com.tr/PowerOn/'
        print("starting :", uuid)
        try:
            response = requests.post(servername + uuid)
            print(response, response.content)
        except Exception as e:
            detail = {'success': 'False',
                      'errors': e}
            return detail
        finally:
            print("successfully power off :", uuid)
            succes = 'success'
            return succes


@app.route('/controlpanel/', methods=['GET', 'POST'])
@flask_login.login_required
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
        return render_template('user_landing_1.html')
    elif request.method == 'POST':
        user_mail = request.form['email']
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
    app.run(debug=True)
