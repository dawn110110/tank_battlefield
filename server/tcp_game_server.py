#!/usr/bin/env python
# encoding=utf-8
'''
TCPGameServer
'''

import config
import models
import tornado
from tornado import ioloop
from tornado.netutil import TCPServer
from tornado.autoreload import start as restarter
import logging
import utils
import tank


class GameRoom(object):
    def __init__(self):
        self.p1 = None
        self.p2 = None
        self.battle = tank.TankBattle()  # game logic


class TCPGameServer(TCPServer):
    '''
    Game Server Based On TCP protocol
    TODO: a lot
    '''
    def __init__(self, io_loop=None, ssl_options=None, **kwargs):
        TCPServer.__init__(self, io_loop=io_loop,
                           ssl_options=ssl_options, **kwargs)

    def handle_stream(self, stream, address):
        cli = GameConnection(address, stream, self)  # process the stream
        logging.info("new conn : %r" % cli)


class GameConnectionBase(object):
    '''
    game protocol implementation based on tcp
    TODO: a lot
    '''
    def __init__(self, address, stream, server):
        ''' init the'''
        self.address = address
        self.stream = stream
        self.server = server
        self.ret_code = None
        logging.info("new connection, from :"+str(self.address))
        self.stream.read_until("\r\n", self.process_msg)


    def process_msg(self, data):
        ''' when client write a \r\n , this method is called'''
        # debug logging
        logging.info("data = %r" % data)
        msg = data.split()
        logging.info("path = %r, data= %r", msg[0], msg[1])

        # handle msg
        act = msg[0]
        extend = msg[1:-1]
        detail = utils.my_decode(msg[-1])

        method_name = 'do_'+act.lower()
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            ret_data = method(act, detail, extend)
            ret_code = self.ret_code or 'ok'
            self.write(''.join([ret_code, '\n', utils.my_encode(ret_data),
                                '\r\n']))
        else:
            # raise ActionNotDefined()
            # close connection
            self.write("error\n\r\n")
            self.close()

        # next loop
        try:
            self.ret_code = None
            self.stream.read_until("\r\n", self.process_msg)
        except IOError, e:
            logging.info(e)
            self.close()

    def close(self):
        self.stream.close()

    def write(self, msg):
        self.stream.write(msg)


class GameConnection(GameConnectionBase):
    def __init__(self, address, stream, server):
        GameConnectionBase.__init__(self, address, stream, server)

    def do_test(self, act, detail, extend):
        logging.info("TESTING: act=%r, detail= %r, extend= %r" % (act, detail,
                                                                  extend))
        return "testing\n\r\n"
    def do_init(self, act, detail, extend):
        pass

    def do_random_room(self, act, detail, extend):
        pass

    def do_choose_room(self, act, detail, extend):
        pass

    def do_room_list(self, act, detail, extend):
        pass

    def do_user_info(self, act, detail, extend):
        pass





class ServerApp(object):
    ''' singleton '''
    _instace = ''

    @classmethod
    def instance(cls):
        if not cls._instace:
            cls._instace = cls()
        return cls._instace

    def __init__(self):
        self.rooms = []


def main():
    # asd
    server = TCPGameServer()
    server.listen(config.game_tcp_port)
    loop = ioloop.IOLoop.instance()
    if config.debug:
        restarter(loop)
    loop.start()
if __name__ == "__main__":
    lg = logging.getLogger()
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(utils.TornadoFormatter(color=True))

    lg.addHandler(console_handler)

    lg.setLevel(logging.INFO)

    main()
