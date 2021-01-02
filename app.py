from flask_table import Table, Col, LinkCol, ButtonCol
from flask import Flask, render_template
from tools.database import UserData
import pymysql

"""A example for creating a simple table within a working Flask app.
Our table has just two columns, one of which shows the name and is a
link to the item's page. The other shows the description.
"""

app = Flask(__name__)


class ItemTable(Table):
    # name = LinkCol('Owner', 'single_item',
    #                url_kwargs=dict(id='id'), attr='name')
    name = Col('Owner')
    description = Col('Labname')

    power = ButtonCol(name='Power',
                    endpoint='poweroff',
                    url_kwargs=dict(uuid='id'),
                    button_attrs=dict(name='Power-On',)
                    )

class Item(object):
    """ a little fake database """
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    @classmethod
    def get_elements(cls):
        return [
            Item(1, 'mesut@mikronet.net', 'base-2243*0984203*942209348'),
            Item(2, 'hakan@mikronet.net', 'base-nmöbb234mn23bmn234b234'),
            Item(3, 'mesut@mikronet.net', 'base-2243*09842234m234nmsnb8')]

    @classmethod
    def get_element_by_id(cls, id):
        return [i for i in cls.get_elements() if i.id == id][0]


@app.route('/')
def index():
    items = Item.get_elements()
    table = ItemTable(items)

    # You would usually want to pass this out to a template with
    # render_template.
    return table.__html__()


@app.route('/item/<int:id>')
def single_item(id):
    element = Item.get_element_by_id(id)
    # Similarly, normally you would use render_template
    return '<h1>{}</h1><p>{}</p><hr><small>id: {}</small>'.format(
        element.name, element.description, element.id)

@app.route('/PowerOff/<uuid>')
def poweroff(uuid):
    return uuid

@app.route('/PowerOn/<uuid>')
def poweron(uuid):
    return uuid

@app.route('/controlpanel')
def test():
    database = UserData(server='192.168.17.131',
                    user='root',
                    password='12qwasZX',
                    database='core_labs')
    headings = ('owner mail', 'owner uuid', 'started on', 'expire on', 'ports', 'running on', 'lab gns3 id', 'status')
    all_labs = database.get_all_labs()
    data = database.get_formatted_lab_data(all_labs)

    return render_template('table.html', headings=headings, data=data)


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            port='7000')