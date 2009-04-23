#!/usr/bin/env python2.5
from __future__ import with_statement
import fcgi, os, sys, threading, signal, time
import logging, logging.handlers

from dispatcher import RequestDispatcher, Request, ExitRequest
from questserver import QuestServer
from balancer import LoadBalancer
from viewers import IViewer


def prepareLogger():
    LOG_DIRNAME = "/tmp/qserver"
    if not os.path.isdir(LOG_DIRNAME):
        os.makedirs(LOG_DIRNAME)
    LOG_FILENAME = os.path.join(LOG_DIRNAME, "qserver.log")
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes = 50000000, backupCount = 5)
    handler.setFormatter(logging.Formatter("%(asctime)s\t%(name)s\t%(module)s\t%(levelname)s:\t%(message)s"))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
        


class FCGIServer:
    configFile = "questserver.cfg"

    def __init__(self):
        prepareLogger()
        self.balancer = LoadBalancer()
        self.srv = QuestServer(self.configFile, True)
        self.working = True
        Request.BASE_PATH = self.srv.basePath
        IViewer.BASE_URL = self.srv.baseUrl
        for _ in xrange(self.srv.workersCount):
            threading.Thread(target = self.base_worker).start()
        threading.Thread(target = self.backup_worker).start()
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def base_worker(self):
        dispatcher = RequestDispatcher(self.srv)
        while self.working:
            req = self.balancer.Get()
            try:
                if isinstance(req, ExitRequest): return
                dispatcher.dispatch(req)
            except:
                logging.exception("while processing request [%s]", req)
            finally:
                self.balancer.OnFinish(req)

    def backup_worker(self):
        backupTime = time.time() + 5 * 60
        logging.info("next backup time: %s", time.ctime(backupTime))
        while self.working:
            try:
                if time.time() > backupTime:
                    self.srv.Backup()
                    backupTime = time.time() + 5 * 60
                    logging.info("next backup time: %s", time.ctime(backupTime))
                time.sleep(0.1)
            except:
                logging.exception("in backup loop")

    def __call__(self):
        while fcgi.isFCGI():
            try:
                req = Request(fcgi.Accept())
                self.balancer.Add(req)
            except:
                logging.exception("bad accepted request")

    def signal_handler(self, signum, frame):
        logging.warning("Signal %s got. Exiting...", signum)
        self.working = False
        self.srv.Backup()
        for _ in xrange(self.srv.workersCount):
            self.balancer.Add(ExitRequest())
        print "exiting..."


if __name__ == "__main__":
    try:
        srv = FCGIServer()
        srv()
        import time
        while threading.activeCount() > 1: 
            time.sleep(1)
    except:
        logging.exception("accept queries exception") 

