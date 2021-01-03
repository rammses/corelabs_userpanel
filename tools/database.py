import pymysql
import datetime
import requests
import json


class UserData:

    def __init__(self, server, user, password, database):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        self.connection = pymysql.connect(host=self.server,
                                     user=self.user,
                                     password=self.password,
                                     db=self.database,
                                     cursorclass=pymysql.cursors.DictCursor)

    def get_lab_status(self, gns3_server_ip, lab_uuid):
        uri = 'http://' + str(gns3_server_ip) + ':3080/v2/projects/' + lab_uuid
        # print(uri)
        response = requests.get(uri)
        details = json.loads(response.content)
        if details['status'] == 'opened':
            return True
        else:
            return False

    def get_lab_name(self, gns3_server_ip, lab_uuid):
        uri = 'http://' + str(gns3_server_ip) + ':3080/v2/projects/' + lab_uuid
        # print(uri)
        response = requests.get(uri)
        details = json.loads(response.content)
        return details['name']

    def get_mail(self, fk_user_id):
        # Connect to the database
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT email FROM user WHERE pk_user_id=" + fk_user_id
                # print('doing :', sql)
                cursor.execute(sql)
                result = cursor.fetchone()
        except Exception as e:
            print('error on get_mail :', e)

        return result['email']

    def get_user_id(self, users_mail):
        # Connect to the database
        sql_fixed_user_mail = '\''+users_mail+'\''
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT pk_user_id FROM user WHERE email=" + sql_fixed_user_mail
                print('doing :', sql)
                cursor.execute(sql)
                result = cursor.fetchone()
        except Exception as e:
            print('error on get_user_id :', e)

        return result['pk_user_id']

    def get_all_labs(self):

        # Connect to the database
        try:
            with self.connection.cursor() as cursor:
                # Read a single record
                sql = "SELECT fk_user_id, lab_name, lab_created_at, lab_expires_at, lab_ports_start, running_on, new_lab_id FROM lab"
                print('doing :', sql)
                cursor.execute(sql)
                all_labs = cursor.fetchall()
        except Exception as e:
            print('error on get all labs :',e)
        return all_labs

    def get_formatted_lab_data(self, labs):
        render_data = []
        for lab in labs:
            render_member = []
            gns3_ip = None
            lab_name = None
            new_lab_id = None
            for k, v in lab.items():
                if k == 'fk_user_id':
                    users_mail = self.get_mail(fk_user_id=str(v))
                    render_member.append(users_mail)
                elif isinstance(v, datetime.datetime):
                    string_it = v.strftime("%m/%d/%Y, %H:%M:%S")
                    render_member.append((string_it))
                else:
                    render_member.append(v)
            # statü sor
            for k, v in lab.items():
                if k == 'running_on':
                    gns3_ip = v
                elif k == 'lab_name':
                    lab_name = v
                elif k == 'new_lab_id':
                    new_lab_id = v
                if gns3_ip is not None and new_lab_id is not None:
                    if self.get_lab_status(gns3_server_ip=gns3_ip, lab_uuid=new_lab_id) is True:
                        render_member.append('running')
                    else:
                        render_member.append('stopped')
            render_data.append(tuple(render_member))
        return tuple(render_data)

    def get_users_labs(self,user_mail):
        fk_user_id = self.get_user_id(user_mail)
        # Connect to the database
        try:
            with self.connection.cursor() as cursor:
                sql = "SELECT new_lab_id, lab_created_at, lab_expires_at, lab_ports_start, running_on FROM core_labs.lab" \
                      " WHERE fk_user_id =" + str(fk_user_id)
                print('doing :', sql)
                cursor.execute(sql)
                users_labs = cursor.fetchall()
        except Exception as e:
            print('error on get all labs :',e)
        return users_labs


    def get_formatted_user_lab_data(self, users_labs):
        render_data = []
        for lab in users_labs:
            render_member = []
            gns3_ip = None
            lab_name = None
            new_lab_id = None
            for k, v in lab.items():
                if k == 'fk_user_id':
                    users_mail = self.get_mail(fk_user_id=str(v))
                    render_member.append(users_mail)
                elif isinstance(v, datetime.datetime):
                    string_it = v.strftime("%m/%d/%Y, %H:%M:%S")
                    render_member.append((string_it))
                else:
                    render_member.append(v)
            # statü sor
            for k, v in lab.items():
                if k == 'running_on':
                    gns3_ip = v
                elif k == 'lab_name':
                    lab_name = v
                    print('lab_name is : ', lab_name )
                elif k == 'new_lab_id':
                    new_lab_id = v
                if gns3_ip is not None and new_lab_id is not None:
                    if self.get_lab_status(gns3_server_ip=gns3_ip, lab_uuid=new_lab_id) is True:
                        render_member.append('running')
                    else:
                        render_member.append('stopped')
            render_data.append(tuple(render_member))
        return tuple(render_data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()