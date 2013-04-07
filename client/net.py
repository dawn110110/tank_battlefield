#!/usr/bin/env python

import socket
from socket import *
import select
import utils
from hashlib import sha1
import time

__all__ = []

class LoginFailed(Exception):
    def __init__(self, code, hint):
        self.code = code
        self.hint = hint

    def __repr__(self):
        return '<LoginFailed, %d, %s>' % (self.code, self.hint)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def no_reply(cls):
        return LoginFailed(0, 'server no reply')

    @classmethod
    def wrong_info(cls):
        return LoginFailed(1, 'wrong passwd or username')

    @classmethod
    def server_error(cls):
        return LoginFailed(2, 'internal server error')



class GameConn(object):
    def __init__(self, addr=None):
        self._addr = addr or ('127.0.0.1', 8000)  # default
        self._sock = None
        self._token = None
        self.recv_buff = ''
        self.recv_msg = None

    def _new_sock(self, addr):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect(self._addr)
        self._sock = s
        return s

    def _get_sock(self):
        if self._sock:
            try:
                s = self._sock
                ret = select.select([s], [s], [s])
                return ret
            except socket.error, e:
                self._sock.close()
                self._sock = None
                return None
        else:
            return None

    def get_sock(self):
        sock = self._get_sock()
        if sock:
            return sock
        else:
            self._new_sock(self._addr)
            return self.get_sock()

    def wait_until_msg(self):
        ''' will block, 
        if get_msg() return None,
            will wait,
            if wait again,
                wait time *= 2
        wait time increase like:

        [0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 1.28, 2.56, 5.12, 10.24]

        up to 20.46 secs total timeout
        if finally not a full msg come,
            return None
        '''
        ret = self.get_msg()
        for wait in range(0, 10):  # max 20.48 secs
            if ret is None:
                time.sleep(2** wait * 0.02)
                ret = self.get_msg()
            else:
                break
        return ret


    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None
        return True

    def send_msg(self, act, data):
        sock = self.get_sock()
        send_sock = sock[1]
        if send_sock:
            send_sock[0].send(''.join(
                [act, '\n', utils.my_encode(data), '\r\n']))
            return True
        else:
            return False

    def get_msg(self):
        '''
        only when a complete msg end with \r\n comes,
        it will return the msg.
        else will return None,
        this function won't block
        '''
        sock = self.get_sock()
        read_sock = sock[0]
        if read_sock:
            self.recv_buff += read_sock[0].recv(99999)

            # cut \r\n from recv_buff
            if '\r\n' in self.recv_buff:
                parts = self.recv_buff.split('\r\n', 1)
                msg_buff = parts[0]
                if len(parts) == 2:
                    self.recv_buff = parts[1]
                else:
                    self.recv_buff = ''
            else:
                return None

            # split & decode msg
            msg = msg_buff.split()
            self.recv_msg = msg
            try:
                msg[-1] = utils.my_decode(msg[-1])
            except Exception, e:
                pass
            return msg
        else:
            return None

    def login(self, username, pwd):
        sha1_pw = sha1(pwd).hexdigest()
        detail = {'username': username, 'pwd': sha1_pw}
        self.send_msg('login', detail)
        ret = None
        ret = self.get_msg()

        ret = self.wait_until_msg()
        if ret is None:
            raise LoginFailed.no_reply()

        print ret
        if ret[0] == 'ok':  # here really no problem
            self._token = ret[-1]['token']
            return True
        elif ret[0] == 'wrong':
            self._token = None
            raise LoginFailed.wrong_info()
        else:
            self._token = None
            raise LoginFailed.server_error()

    def regist(self, detail):
        '''
        username, pwd, email,
        '''
        self.send_msg('regist', detail)
        ret = self.wait_until_msg()
        return ret

    def test(self):
        pass

    def get_serv_info(self):
        pass


if __name__ == "__main__":
    print '*' * 20
    print 'testing 4, clear db'
    c = GameConn()
    c.send_msg('clear_db', {})
    print c.wait_until_msg()

    print '*'* 20, 'register'
    import random
    userdata = {}
    userdata['username'] = 'user%d' % random.randint(0, 100)
    userdata['pwd'] = '123456'
    userdata['email'] = 'user%d@user.com' % random.randint(0, 100)
    print userdata
    ret = c.regist(userdata)
    print ret


#   print '*' * 20
#   print 'testing 4, show db'
#   c4 = GameConn()
#   c4.send_msg('show_db', {'word':'somewords'})
#   time.sleep(2)
#   ret = c4.get_msg()
#   print ret
#   c4.close()

    #print 'testing 1, right login'
    #c1 = GameConn()
    #print c1.login("debug", "debug")
    #c1.close()

    #print 'testing 2, wrong login'
    #c2 = GameConn()
    #try:
    #    c2.login("debug", "wrong")
    #except LoginFailed, e:
    #    print e
    #c2.close()

    #print 'testing 3, wrong act'
    #c3 = GameConn()
    #c3.send_msg("abc", "def")
    #print c3.get_msg()
    #c3.close()


