import tornado.web
import tornado.ioloop
import tornado.websocket
import os
from tornado.escape import json_decode
import json

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
        self.write_message('send connected message')

    def on_message(self, message):
        data = json_decode(message)
        event = data['event']
        data = data['data']

        payload = {}


        if event == 'saveUser':
            payload = {'event': 'notifyStatus', 'data': data}
        else:
            payload = {'event': 'fillTable', 'data': data}

        print('writing message received: event: ', event, 'data: ',  data)
        self.write_message(json.dumps(payload))

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
