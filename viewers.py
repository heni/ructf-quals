#!/usr/bin/env python2.5
import cgitb
from users import *
import itertools, os, re, time
from xml.dom import minidom
factory = minidom.Document()


###################
# Base Interfaces #
###################

class IReport:
    @staticmethod
    def CreateReportRoot():
        xmlNode = factory.createElement("response")
        xmlNode.setAttribute("base", IViewer.BASE_URL)
        return xmlNode

    @staticmethod
    def CreateChild(parent, tag, **attrs):
        node = factory.createElement(tag)
        for attr, value in attrs.iteritems():
            node.setAttribute(attr, str(value))
        if parent: parent.appendChild(node)
        return node

    def GetXMLCode(self):
        return self.xmlNode.toprettyxml()

    def GetXMLNode(self):
        return self.xmlNode

class IViewer:
    BASE_URL = "http://localhost/qserver"

    def output(self, out):
        out.write('Content-Type: text/xml\n\n')
        out.write('<?xml version="1.0" encoding="utf-8" ?>\n')
        out.write('<?xml-stylesheet type="text/xsl" href="%s/static/qserver.xsl" ?>\n' % self.BASE_URL)
        self.report.GetXMLNode().writexml(out, addindent = "    ", newl = "\n")


"""LoginView"""
class LoginReport(IReport):
    def __init__(self, tryCount, sourceLocation):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "login")
        self.CreateChild(viewNode, "param", name = "count", value = tryCount)
        self.CreateChild(viewNode, "param", name = "source", value = sourceLocation)


class LoginViewer(IViewer):
    def __init__(self, tryCount = 0, sourceLocation = ""):
        self.report = LoginReport(tryCount, sourceLocation)


"HelloView"
class HelloReport(IReport):
    def __init__(self, username):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "hello")
        self.CreateChild(viewNode, "param", name = "username", value = username)

class HelloViewer(IViewer):
    def __init__(self, user):
        self.report = HelloReport(user.name)


"ErrorView"
class ErrorReport(IReport):
    def __init__(self, message, sourceLocation):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "error")
        self.CreateChild(viewNode, "param", name="source", value = sourceLocation)
        viewNode.appendChild(factory.createTextNode(message))

class ExceptionReport(IReport):
    def __init__(self, etype, evalue, etb):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "error")
        traceNode = self.CreateChild(viewNode, "traceback")
        traceNode.appendChild(factory.createTextNode(unicode(cgitb.text((etype, evalue, etb)), "utf-8")))
 
class ErrorViewer(IViewer):
    def __init__(self, message = "", exc = None, sourceLocation = ""):
        if message:
            self.report = ErrorReport(unicode(message, "utf-8"), sourceLocation)
        else:
            self.report = ExceptionReport(*exc)


"QuestListView"
class TeamQListReport(IReport):
    def __init__(self, stat):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "quest-list")
        for cat, catlist in sorted(stat.items()):
            catnode = self.CreateChild(viewNode, "category", id = cat, name = cat)
            for qId, done in catlist:
                questLabel = qId.split(":", 1)[-1]
                status = {True: "completed", None: "available", False: "unavailable"}[done]
                self.CreateChild(catnode, "quest", id = qId, status = status, label = questLabel)

class QuestListViewer(IViewer):
    def __init__(self, srv, user):
        stat = srv.GetQuestList(user.name)
        self.report = TeamQListReport(stat)


"QuestView"
class QuestGetReport(IReport):
    def __init__(self, qd, questId, questName):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "quest")
        self.CreateChild(viewNode, "param", name = "questId", value = questId)
        self.CreateChild(viewNode, "param", name = "questName").appendChild(factory.createTextNode(questName))
        viewNode.appendChild(qd.GetXMLNode())

class QuestViewer(IViewer):
    def __init__(self, qd, questId, questName):
        self.report = QuestGetReport(qd, questId, questName)


def CreateVerdictNode(root, status, message):
    verdictNode = IReport.CreateChild(root, "verdict", status = status)
    try:
        doc = minidom.parseString(message)
        verdictNode.appendChild(doc.documentElement)
    except:
        if isinstance(message, unicode):
            verdictNode.appendChild(factory.createCDATASection(message))
        elif isinstance(str, unicode):
            verdictNode.appendChild(factory.createCDATASection(unicode(message, "utf-8")))

"QuestCheckView"
class QuestCheckReport(IReport):
    def __init__(self, questId, questName, code, message):
        status = {True: "accepted", False: "rejected", None: "postponed"}[code]
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "quest-check")
        self.CreateChild(viewNode, "param", name = "questId", value = questId)
        self.CreateChild(viewNode, "param", name = "questName").appendChild(factory.createTextNode(questName))
        CreateVerdictNode(viewNode, status, message)

class QuestCheckViewer(IViewer):
    def __init__(self, verdict, questId, questName):
        self.report = QuestCheckReport(questId, questName, *verdict)


"MonitorView"
class MonitorReport(IReport):
    def __init__(self, stat, teams):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "monitor")
        statNode = self.CreateChild(viewNode, "stat")
        for cat, catlist in sorted(stat.items()):
            catNode = self.CreateChild(statNode, "category", id = cat, name = cat)
            for qi in catlist:
            #for qId, availFlag, doneCount in catlist:
                qId = qi[0]
                questLabel = qId.split(":")[-1]
                if len(qi) == 3:
                    status = "available" if qi[1] else "unavailable"
                    self.CreateChild(catNode, "quest", id = qId, label = questLabel, done = qi[2], status = status)
                else:
                    status = "postponed" if qi[3] > 0 else ("available" if qi[1] else "unavailable")
                    self.CreateChild(catNode, "quest", id = qId, label = questLabel, done = qi[2], status = status, postponed = qi[3])
        rankNode = self.CreateChild(viewNode, "ranklist")
        for team, score in teams:
            self.CreateChild(rankNode, "team", name = team.name, score = score)

class MonitorViewer(IViewer):
    def __init__(self, stat, teams):
        self.report = MonitorReport(stat, teams)

"JuryQuestView"
class JuryQuestListReport(IReport):
    def __init__(self, questId, questName, solutions):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "jury-quest-list")
        self.CreateChild(viewNode, "param", name = "questId", value = questId)
        self.CreateChild(viewNode, "param", name = "questName").appendChild(factory.createTextNode(questName))
        ppndFlag = True
        for sol in sorted(solutions, key = lambda s: s.timeStamp):
            status = {True: "accepted", False: "rejected", None: "postponed"}[sol.status]
            solNode = self.CreateChild(viewNode, "solution", time = time.ctime(sol.timeStamp), 
                                        team = sol.username, id = sol.solutionID, status = status)
            ppndFlag = ppndFlag and sol.status is None
        if ppndFlag: viewNode.setAttribute("postponed", "true")

class JuryQuestGetReport(IReport):
    def __init__(self, qd, questId, questName, sol):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "jury-quest-get")
        self.CreateChild(viewNode, "param", name = "questId", value = questId)
        self.CreateChild(viewNode, "param", name = "questName").appendChild(factory.createTextNode(questName))
        viewNode.appendChild(qd.GetXMLNode())
        status = {True: "accepted", False: "rejected", None: "postponed"}[sol.status]
        solNode = self.CreateChild(viewNode, "solution", time = time.ctime(sol.timeStamp), team = sol.username, 
                id = sol.solutionID, status = status)
        solNode.appendChild(factory.createTextNode(sol.actionString))
        if re.match("[-A-Za-z0-9_\.]+$", sol.actionString) and os.path.isfile(os.path.join("upload", sol.actionString)):
            solNode.setAttribute("file", os.path.join("upload", sol.actionString))
        CreateVerdictNode(solNode, status, sol.verdict)

class JuryQuestViewer(IViewer):
    def __init__(self, qd, questId, questName, sol):
        if qd:
            self.report = JuryQuestGetReport(qd, questId, questName, sol)
        else:
            self.report = JuryQuestListReport(questId, questName, sol)

