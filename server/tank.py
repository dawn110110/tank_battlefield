#!/usr/bin/env python

import json
import time

class GameMap(object):
    def __init__(self):
        self.map = [range(0, 40) for i in xrange(60)]
        for x in xrange(40):
            for y in xrange(60):
                pass
    pass


class TankBattle(object):
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

        self.game_map = GameMap()

        self.start_time = time.time()
        self.end_time = None

        self.winner = None
