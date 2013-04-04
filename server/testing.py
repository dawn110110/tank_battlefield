#!/usr/bin/env python

from socket import *

def test(sock, msg):
    sock.send(msg)
    print '*' * 20
    print 'cli send: %r' % msg
    res = sock.recv(5000)
    print 'serv ans: %r' % res

if __name__ == "__main__":
    serv_addr = ("127.0.0.1", 8000)
    s = socket(AF_INET, SOCK_STREAM)
    s.connect(serv_addr)
    test(s, "test\n12345\r\n")
    test(s, "test\n12345\r\n")
    test(s, "test\n12345\r\n")
    test(s, "test\n12345\r\n")
    test(s, "test\n12345\r\n")
    test(s, "test\n12345\r\n")
    test(s, "test\n12345\r\n")

    s.close()

