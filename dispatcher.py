#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-

import sys, codecs, urllib, logging
from users import *
from viewers import *

class SmartDecoder:
    enc_list = ["utf-8", "cp1251"]

    @classmethod
    def decode(cls, data):
        for enc in cls.enc_list:
            try:
                _data = unicode(data, enc)
                return _data
            except:
                pass
        return data


class Request:
    BASE_PATH = "crack"
    def __init__(self, req):
        self.req = req
        self.outstream = codecs.lookup("utf-8")[3](req.out)
        self.command, self.subcommand = self.ParsePath(req)
        self.cookie = self.ParseCookie(req)
        self.remoteAddr = req.env.get("REMOTE_ADDR", "") 
        fs = req.getFieldStorage()
        self.keywords = {'req': req}
        for p in fs:
            self.keywords[p] = SmartDecoder.decode(fs[p].value)
        logging.info("""
\trequest: {REMOTE_ADDR: '%s', REQUEST_URI: '%s', HTTP_COOKIE: '%s'}
\treqparam: %s""", req.env.get("REMOTE_ADDR"), req.env.get("REQUEST_URI"), req.env.get("HTTP_COOKIE"), self.keywords)

    def ParsePath(self, req):
        command, subcommand = None, None
        uri = req.env.get("REQUEST_URI", "").split('?', 1)[0]
        if uri.startswith(self.BASE_PATH):
            items = uri[len(self.BASE_PATH):].split('/', 1)
            command = items[0]
            if len(items) > 1: subcommand = items[1]
        return command, subcommand

    def ParseCookie(self, req):
        cookie = req.env.get("HTTP_COOKIE", "")
        return dict(pv.split("=", 1) for pv in cookie.split(";") if pv and pv.find("=") >= 0)

    def Finish(self):
        self.req.Finish()


class ExitRequest(Request):        

    def __init__(self):
        self.req = None
        self.outstream = sys.stdout
        self.command, self.subcommand = None, None
        self.cookie = {}
        self.keywords = {}
        self.remoteAddr = ''

    def Finish(self):
        pass



class RequestDispatcher:
    dispatchTable = {}
    processedCount = 0

    def __init__(self, srv):
        self.srv = srv

    def check_auth(self, request):
        user = None
        if 'auth' in request.cookie:
            user = self.srv.Authenticate(request.cookie['auth'])
        return user or GuestUser()

    def dispatch(self, request):
        try:
            user = self.check_auth(request)
            if request.command not in self.dispatchTable:
                request.command = 'default'
            viewer = self.dispatchTable[request.command](self, request.subcommand, user, **request.keywords)
        except:
            logging.exception("while dispatcher request")
            viewer = ErrorViewer(message = "Сервер не понимает что вы от него хотите")
        try:
            self.processedCount += 1
            viewer.output(request.outstream)
        finally:
            request.Finish()

    def do_login(self, subcommand, user, req = None, auth = "", count = "-1", **kws):
        if isinstance(user, GuestUser):
            if auth:
                user = self.srv.Authenticate(auth)
                if not isinstance(user, GuestUser):
                    req.out.write("Set-Cookie: auth=%s\n" % auth)
                    return HelloViewer(user)
            return LoginViewer(tryCount = int(count) + 1)
        return HelloViewer(user)
        #return ErrorViewer(message = "You are logged in already")
    dispatchTable['login'] = do_login

    def do_quest(self, subcommand, user, questId = None, actionString = "", solution = None, **kws):
        if isinstance(user, LegalUser):
            if subcommand == "view" or not subcommand:
                return QuestListViewer(self.srv, user)
            elif subcommand == "get":
                qd = self.srv.GetQuest(user.name, questId)
                if qd: return QuestViewer(qd, questId, self.srv.GetQuestName(questId))
                return ErrorViewer(message = "Вы не можете получить этот квест")
            elif subcommand == "check":
                verdict = self.srv.CheckQuest(user.name, questId, actionString)
                if verdict: return QuestCheckViewer(verdict, questId, self.srv.GetQuestName(questId))
                return ErrorViewer(message = "Вы не можете отправлять решения для этого квеста. Возможно вы отвечаете слишком быстро :)")
        elif isinstance(user, AdminUser):
            if not subcommand or subcommand in ("accept", "all", "get", "reject"):
                if not questId:
                    return MonitorViewer(*self.srv.GetJuryMonitor())
                questName = self.srv.GetQuestName(questId)
                if not solution:
                    if subcommand == "all":
                        solList = self.srv.GetQuestSolutions(questId) 
                    else:
                        solList = self.srv.GetQuestSolutions(questId, lambda s: s.status is None)
                    return JuryQuestViewer(None, questId, questName, solList)
                solList = self.srv.GetQuestSolutions(questId, lambda s: s.solutionID == solution)
                for sol in solList: #process only first solution if it exists
                    if subcommand == "get":
                        qd = self.srv.GetQuest(sol.username, questId)
                        return JuryQuestViewer(qd, questId, questName, sol)
                    sol.ChangeVerdict(subcommand == "accept", actionString)
                    logging.info("tracker changed: %s", self.srv.tracker.__dict__)
                    return MonitorViewer(*self.srv.GetJuryMonitor())
        return ErrorViewer(message = "Проверьте, что всё делаете правильно")
    dispatchTable['quest'] = do_quest

    def do_default(self, subcommand, user, auth = None, **kws):
        if isinstance(user, GuestUser):
            return LoginViewer(tryCount = 0)
        elif isinstance(user, LegalUser):
            return QuestListViewer(self.srv, user)
        return HelloViewer(user)
    dispatchTable['default'] = do_default

    def do_signout(self, subcommand, user, req = None, **kws):
        req.out.write('Set-Cookie: auth=\n')
        return LoginViewer(tryCount = 0)
    dispatchTable['signout'] = do_signout

    def do_monitor(self, subcommand, user, **kws):
        if isinstance(user, AdminUser):
            stat, teams = self.srv.GetJuryMonitor()
        else:
            stat, teams = self.srv.GetMonitor()
        return MonitorViewer(stat, teams)
    dispatchTable['monitor'] = do_monitor
