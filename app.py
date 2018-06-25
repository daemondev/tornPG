import tornado.web
import tornado.ioloop
import tornado.websocket
import os
from tornado.escape import json_decode
from tornado import gen
import json

import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy.orm import sessionmaker
from models import *
import json
import datetime
import tornado
import time
tornado.httputil.format_timestamp(time.localtime())

if not hasattr(os, 'scandir'):
    import scandir
    os.scandir = scandir.scandir

#-------------------------------------------------- BEGIN [async] - (22-06-2018 - 03:17:57) {{
import psycopg2.extensions

conn = psycopg2.connect('dbname=termux user=termux password=123')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
#-------------------------------------------------- END   [async] - (22-06-2018 - 03:17:57) }}

from sqlalchemy.ext.declarative import DeclarativeMeta

io_loop  = tornado.ioloop.IOLoop.instance()
engine = create_engine("postgresql://termux:123@localhost/termux")
#df = pd.Dataframe.from_csv('db/b.txt', delimiter='\t', encoding='cp1252')
#df.to_sql(name='base2', con=engine, if_exists='replace' ,index=False)

Session = sessionmaker(engine)
session= Session()

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


class AjaxHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body
        print('printing data:', data)

    def get(self):
        data = self.request.body
        self.write('ajax ready!!!')
        print('printing data:', data)

def listen(ch):
    '''Listen to a channel.'''
    curs = conn.cursor()
    curs.execute("LISTEN %s;" % ch)

@gen.coroutine
def watch_db(fd, events):
    state = conn.poll()
    if state == psycopg2.extensions.POLL_OK:
        if conn.notifies:
            notify = conn.notifies.pop()
            print(notify.payload)
            qBase = session.query(Base).all()
            for cnx in connections:
                payload1 = {'event': 'notifyFromDB', 'data': notify.payload}
                payload2 = {'event': 'fillTable', 'data': qBase}
                multi_payload = {'event': 'multi', 'data': [payload1, payload2]}
                #cnx.write_message(json.dumps(payload))
                print('\n>>> multi_payload: ', multi_payload, '\n<<<')
                cnx.write_message(json.dumps(multi_payload, cls=AlchemyEncoder))
    print(">>> notified")

connections = set()
#connections = {}

@gen.coroutine
def websocketManager(self, request):
    print(">>> websocketManager executed")
    pass

def getHRFileSize(size, precition=2):
    suffixes = ['B', 'KB', 'MB', 'GB']
    suffixesIndex = 0
    while size > 1024:
        suffixesIndex += 1
        size = size / 1024.0
    return '%.*f %s' % (precition, size, suffixes[suffixesIndex])

def getScandirIterator(path):
    return os.scandir(path)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        qBase = session.query(Base).all()
        payload = {'event': 'fillTable', 'data': qBase}
        connections.add(self)
        self.write_message(json.dumps(payload, cls=AlchemyEncoder))

    def on_message(self, message):
        data = json_decode(message)
        event = data['event']
        data = data['data']

        payload = {}
        if event == 'listFiles':
            cwd = os.path.join(os.getcwd(), 'db')
            #files = [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f))]
            files = {'name': [], 'size': [], 'date': [], 'total':0}
            counter = 1
            #with os.scandir(cwd) as it:
            it = getScandirIterator(cwd)
            for entry in it:
                f_spec = entry.stat()
                files['name'].append(entry.name)
                files['size'].append(getHRFileSize(f_spec.st_size))
                files['date'].append(datetime.datetime.fromtimestamp(f_spec.st_mtime).strftime('%Y-%m-%d %H:%M'))
                files['total'] += 1

            print('>>> cwd: ', cwd, '\nfiles', files)
            payload = {'event': 'listFiles', 'data': files}
        elif event in ['updateIten', 'saveUser']:
            base = None
            if event == 'saveUser':
                base = Base()
            if event == 'updateIten':
                base = session.query(Base).get(data['id'])

            base.nombre = data['user']
            base.direccion = data['address']
            base.telefono = data['phone']
            base.usuario = data['email']

            if event == 'saveUser':
                session.add(base)
            session.commit()
        elif event == 'loadPandas':
            #df = pd.DataFrame.from_csv('db/b.txt', delimiter='\t', encoding='cp1252')
            df = pd.DataFrame.from_csv('db/b.txt', sep='\t', encoding='cp1252')
            df['extra'] = 999
            df.to_sql(name='base2', con=engine, if_exists='replace' ,index=False)
            print('>>> post load')
        elif event == 'deleteItem':
            item = session.query(Base).get(data['id'])
            session.delete(item)
            session.commit()
        else:
            qBase = session.query(Base).all()
            payload = {'event': 'fillTable', 'data': qBase}

        print('\n\nwriting message received: event: ', event, 'data: ',  data,'\n\n')

        if event not in ['updateIten', 'saveUser', 'deleteItem']:
            for cnx in connections:
                cnx.write_message(json.dumps(payload, cls=AlchemyEncoder))

    def check_origin(self, origin):
        return True

    def on_close(self):
        connections.remove(self)
        print('>>> client disconected: ', self)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + str(time.tzname)
        self.render('index.html', state='Ready!!!', date=date)

handlers = [
            (r'/', IndexHandler),
            (r'/static/(.*)', tornado.web.StaticFileHandler),
            (r'/ws', WebSocketHandler),
            (r'/ajax', AjaxHandler),
        ]

settings = dict(
        template_path=os.path.join(os.getcwd(),'templates'),
        static_path=os.path.join(os.getcwd(), 'static'),
        debug=True
        )

app = tornado.web.Application(handlers, **settings)
io_loop.add_handler(conn.fileno(), watch_db, io_loop.READ)

def main():
    try:
        print('listen server IN port 8000')
        app.listen(8000)
        #app.listen(8888)
        #listen('data')
        listen('base_changes')
        #tornado.ioloop.IOLoop.current().add_callback(watch_db)
        #tornado.ioloop.IOLoop.instance().start()

        io_loop.start()
    except KeyboardInterrupt as e:
        print('stopping server')
        tornado.ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
    main()
