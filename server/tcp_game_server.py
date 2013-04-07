#!/usr/bin/env python
# encoding=utf-8
'''
TCPGameServer
'''

import config
from models import *
import tornado
from tornado import ioloop
from tornado.netutil import TCPServer
from tornado.autoreload import start as restarter
import logging
from hashlib import sha1
from uuid import uuid4
import datetime
import utils
import tank

class RegisterError(Exception):
    pass


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
        self.ret_code = None  # return code
        logging.info("new connection, from :"+str(self.address))
        self.stream.read_until("\r\n", self.process_msg)


    def process_msg(self, data):
        ''' when client write a \r\n , this method is called'''
        # debug logging
        msg = data.split()
#        logging.info("act = %r, data= %r", msg[0], msg[1])

        # handle msg
        act = msg[0]
        extend = msg[1:-1]
        detail = utils.my_decode(msg[-1])

        method_name = 'do_'+act.lower()
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            ret_data = method(act, detail, extend)
            print ret_data
            ret_code = self.ret_code or 'ok'
            ret_str = ''.join(
                [ret_code, '\n', utils.my_encode(ret_data), '\r\n'])
            logging.info("ret_str = %r" % ret_str)
            self.write(ret_str)
        else:
            # raise ActionNotDefined()
            # close connection
            logging.error("no handler for act: %r" % act)
            try:
                self.write("error\n\r\n")
            except IOError, e:
                logging.error("%r" % e)
            finally:
                self.close()

        # next loop
        try:
            if self.ret_code == 'end':  # close connection
                self.close()
                return
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
        self.user = None
        self._token = ''

    def do_test(self, act, detail, extend):
        logging.info("TESTING: act=%r, detail= %r, extend= %r" % (act, detail,
                                                                  extend))
        self.ret_code = 'end'
        return "testing\n\r\n"

    def do_clear_db(self, act, detail, extend):
        User.drop_table()
        User.create_table()
        Battle.drop_table()
        Battle.create_table()
        return {'hint': 'db cleared'}

    def do_show_db(self, act, detail, extend):
        us = [u.username for u in User.select()]
        battles = Battle.select().count()
        return {'users': us, 'battle': battles}

    def do_login(self, act, detail, extend):
        logging.info("LOGIN: %s:%s" % (detail['username'], detail['pwd']))
        u = User.select().where(User.username == detail['username'])
        try:
            u = list(u)[0]
            if u.pwd == detail['pwd']:
                self._token = str(uuid4())
                return {"token": self._token}
        except:
            pass
        self.ret_code = 'wrong'
        return {'hint': 'username or passwd wrong'}

    def do_regist(self, act, detail, extend):
        logging.info("REGISTER : %r" % detail)
        db.set_autocommit(False)
        try:

            with db.transaction():
                exist = User.select().where(
                    User.username == detail['username'])
                if list(exist):
                    logging.warn(
                        "username: %r , already exist" % detail['username'])
                    raise RegisterError("username already exist")
                logging.info(
                    "ok '%r' could be registered" % detail['username'])
                today_now = datetime.datetime.now()
                detail['pwd'] = sha1(detail['pwd']).hexdigest()  # sha1 pwd
                detail['join_date'] = today_now
                u = User(**detail)
                u.save()
            logging.info('save ok')
            return {'hint': 'registration success'}
        except Exception, e:
            logging.error("%r" % e)
            logging.info('save wrong')
            self.ret_code = 'wrong'
            return {'hint': 'registration failed, username/email may be used'}

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
