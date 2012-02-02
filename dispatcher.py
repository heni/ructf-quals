#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

import sys, codecs, urllib, logging, time
from common import *
from users import *
from viewers import *

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

    def Deferred(self, user, viewer):
        return RedirectViewer("deferred?id=%s" % self.srv.RegisterViewer(user, viewer))

    def dispatch(self, request):
        try:
            user = self.check_auth(request)
            if request.command not in self.dispatchTable:
                request.command = "default"
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
                    return RedirectViewer("login", cookies={'auth': auth})
            return LoginViewer(tryCount = int(count) + 1)
        return HelloViewer(user)
    dispatchTable['login'] = do_login

    def do_fetchview(self, subcommand, user, id = "", **kws):
        viewer = self.srv.GetViewer(user, str(id))
        if isinstance(viewer, IViewer):
            return viewer
        return ErrorViewer(message="Проверьте, что всё делает правильно")
    dispatchTable['deferred'] = do_fetchview

    def do_quest(self, subcommand, user, questId = None, actionString = "", solution = None, **kws):
        if isinstance(user, LegalUser):
            if subcommand == "view" or not subcommand:
                return QuestListViewer(self.srv, user)
            elif subcommand == "get":
                qd = self.srv.GetQuest(user.name, questId)
                if qd: 
                    return QuestViewer(qd, questId, self.srv.GetQuestName(questId))
                return ErrorViewer(message = "Вы не можете получить этот квест")
            elif subcommand == "check":
                verdict = self.srv.CheckQuest(user.name, questId, actionString)
                if verdict: 
                    viewer = QuestCheckViewer(verdict, questId, self.srv.GetQuestName(questId))
                else:
                    viewer = ErrorViewer(message = "Вы не можете отправлять решения для этого квеста. Возможно вы отвечаете слишком быстро :)")
                return self.Deferred(user, viewer)
        elif isinstance(user, AdminUser):
            if not subcommand or subcommand in ("accept", "all", "get", "reject", "open", "close"):
                if not questId:
                    return MonitorViewer(*self.srv.GetJuryMonitor())
                if subcommand in ("open", "close"):
                    if subcommand == "open":
                        self.srv.tracker.OpenQuest(questId)
                    elif subcommand == "close":
                        self.srv.tracker.CloseQuest(questId)
                    return RedirectViewer("monitor")
                questName = self.srv.GetQuestName(questId)
                if not solution:
                    questInfo = self.srv.tracker.GetQuestStat(questId, checkAvailability=True)
                    solList = list(questInfo["sollist"])
                    questInfo["tries"] = len(solList)
                    if solList:
                        questInfo["last"] = time.ctime(solList[-1].timeStamp)
                    if subcommand != "all":
                        solList = [s for s in solList if s.status is None]
                    questInfo["sollist"] = solList
                    return JuryQuestViewer(None, questId, questName, questInfo)
                solList = self.srv.GetQuestSolutions(questId, lambda s: s.solutionID == solution)
                for sol in solList: #process only first solution if it exists
                    if subcommand == "get":
                        qd = self.srv.GetQuest(sol.username, questId)
                        return JuryQuestViewer(qd, questId, questName, sol)
                    sol.ChangeVerdict(subcommand == "accept", actionString)
                    logging.info("tracker changed: %s", self.srv.tracker.__dict__)
                    return RedirectViewer("monitor")
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

    def do_news(self, subcommand, user, page = 0, event = None, text = None, **kws):
        if isinstance(user, LegalUser) or isinstance(user, GuestUser):
            return GV_News(**self.srv.ListNewsItems(page))
        elif isinstance(user, AdminUser):
            if not subcommand:
                return AV_News(**self.srv.ListNewsItems(page))
            if subcommand == "add":
                if text is None:
                    return ErrorViewer(message = "Проверьте, что всё делаете правильно")
                self.srv.AddNewsItem(user, text)
            if subcommand == "delete":
                if event is None:
                    return ErrorViewer(message = "Проверьте, что всё делаете правильно")
                self.srv.DeleteNewsItem(event)
            return RedirectViewer("news")
    dispatchTable['news'] = do_news
