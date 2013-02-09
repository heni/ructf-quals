#!/usr/bin/env python2
from __future__ import with_statement
from time import time as _time
from Queue import deque as _deque
from threading import Condition

class Heap:
    """
Simple Heap object. Keeps objects and can extract object with minimal key.
>>> heap = Heap()
>>> for name in ("Jenny", "Ben", "Cartoon", "Lisa"): heap.Add(name, len(name))
>>> heap.Extract()
('Ben', 3)
>>> heap.Extract()
('Lisa', 4)
>>> heap.ChangeKey("Cartoon", 4)
>>> heap.Add("Ann", 3)
>>> while not heap.Empty(): print heap.Extract()
('Ann', 3)
('Cartoon', 4)
('Jenny', 5)
>>> import random
>>> arr = range(18); random.shuffle(arr)
>>> for k in arr: heap.Add(k, k)
>>> res = []
>>> while not heap.Empty(): res.append(heap.Extract()[0])
>>> res
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
"""

    def __init__(self):
        self.revindex = {}
        self.keys = {}
        self.list = []
    
    def swap(self, id1, id2):
        #import logging
        o1 = self.list[id1]
        o2 = self.list[id2]
        #logging.debug("SWAPPING: %s(%s) %s(%s)", id1, o1, id2, o2)
        self.revindex[id(o1)] = id2; self.list[id2] = o1
        self.revindex[id(o2)] = id1; self.list[id1] = o2
        #logging.debug("RESULT: %s", [(o, self.keys[id(o)]) for o in self.list])

    def rolldown(self, idx):
        #import logging
        #logging.debug("ROLLDOWN: %s", idx)
        key = self.keys[id(self.list[idx])]
        while 2 * idx + 1 < len(self.list):
            ch1 = 2 * idx + 1
            ch2 = 2 * idx + 2
            child = ch2 if ch2 < len(self.list) and self.keys[id(self.list[ch2])] < self.keys[id(self.list[ch1])] else ch1
            if self.keys[id(self.list[child])] < key:
                self.swap(idx, child)
                idx = child
            else:
                break
        return idx

    def rollup(self, idx):
        #import logging
        #logging.debug("ROLLUP: %s", idx)
        key = self.keys[id(self.list[idx])]
        while idx > 0:
            parent = (idx - 1) / 2
            if key < self.keys[id(self.list[parent])]:
                self.swap(idx, parent)
                idx = parent
            else:
                break
        return idx

    def Add(self, object, key):
        idx = len(self.list)
        self.revindex[id(object)] = idx
        self.keys[id(object)] = key
        self.list.append(object)
        self.rollup(idx)
        
    def ChangeKey(self, object, key):
        idx = self.revindex[id(object)]
        self.keys[id(object)] = key
        self.rollup(self.rolldown(idx))

    def Empty(self):
        return len(self.list) == 0

    def Extract(self):
        last = len(self.list) - 1
        if last > 0:
            self.swap(0, last)
        obj = self.list.pop(last)
        del self.revindex[id(obj)]
        key =self.keys.pop(id(obj))
        if last > 0:
            self.rolldown(0)
        return obj, key


class QuestLimitter:

    def __init__(self):
        pass
    
    def OnStart(self, req):
        pass

    def OnEnd(self, req):
        pass


class LoadBalancer:
    def __init__(self):
        self.actions = {}
        self.curact = {}
        self.reqlist = Heap()
        self.cn = Condition()

    def getClientActivity(self, client):
        act = self.actions.get(client, None)
        if act is None: return len(self.curact.get(client, []))
        minTime = _time() - 20 * 60
        while len(act) > 0 and act[0] < minTime:
            act.popleft()
        return len(act) + len(self.curact.get(client, []))

    def Add(self, req):
        with self.cn:
            client = req.remoteAddr
            self.curact.setdefault(client, set()).add(id(req))
            self.reqlist.Add(req, self.getClientActivity(client))
            self.cn.notify()

    def Get(self):
        with self.cn:
            while self.reqlist.Empty():
                self.cn.wait()
            req, count = self.reqlist.Extract()
            return req

    def OnStart(self, req):
        pass

    def OnFinish(self, req):
        with self.cn:
            client = req.remoteAddr
            self.curact[client].remove(id(req))
            self.actions.setdefault(client, _deque()).append(_time())


if __name__ == "__main__":
    import doctest
    doctest.testmod()
