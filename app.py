import tornado.web
import tornado.ioloop
import tornado.websocket
import os
from tornado.escape import json_decode
import json

import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy.orm import sessionmaker
from models import *
import json

from sqlalchemy.ext.declarative import DeclarativeMeta

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


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print('open connection')
        qBase = session.query(Base).all()
        payload = {'event': 'fillTable', 'data': qBase}

        self.write_message(json.dumps(payload, cls=AlchemyEncoder))
        #self.write_message('send connected message')

    def on_message(self, message):
        data = json_decode(message)
        event = data['event']
        data = data['data']

        payload = {}
        if event in ['updateIten', 'saveUser']:
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

            qBase = session.query(Base).all()
            payload = {'event': 'fillTable', 'data': qBase}
        elif event == 'loadPandas':
            print('>>> prev load')
            #df = pd.DataFrame.from_csv('db/b.txt', delimiter='\t', encoding='cp1252')
            df = pd.DataFrame.from_csv('db/b.txt', sep='\t', encoding='cp1252')
            df['extra'] = 999
            df.to_sql(name='base2', con=engine, if_exists='replace' ,index=False)
            print('>>> post load')
        elif event == 'deleteItem':
            item = session.query(Base).get(data['id'])
            print('>>> deleting', item)
            session.delete(item)
            session.commit()
            qBase = session.query(Base).all()
            payload = {'event': 'fillTable', 'data': qBase}

            self.write_message(json.dumps(payload, cls=AlchemyEncoder))

        else:
            payload = {'event': 'fillTable', 'data': data}

        print('writing message received: event: ', event, 'data: ',  data)
        #self.write_message(json.dumps(payload))
        self.write_message(json.dumps(payload, cls=AlchemyEncoder))

    def check_origin(self, origin):
        return True

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', state='Ready!!!')

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

def main():
    try:
        print('listen server IN port 8000')
        app.listen(8000)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt as e:
        print('stopping server')
        tornado.ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
    main()
