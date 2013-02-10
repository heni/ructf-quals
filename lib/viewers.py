#!/usr/bin/env python2
import cgitb
from users import *
import os, re, time, logging
from xml.dom import minidom
factory = minidom.Document()


###################
# Base Interfaces #
###################

class IReport(object):
    """
    Represents body for IReport
    Consists of XML document
    """
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


class IViewer(object):
    """
    Represents CGI answer for WebServer
    Contains headers and body

    Headers is set of Name-Value pairs delimeted by ':'
    Body is empty
    """
    #this variable must be rewrited in qserver.py (during server start)
    BASE_URL = "http://localhost/qserver"
    DELIMETER = "\r\n"

    def __init__(self, *args, **kwargs):
        self.headers = {}
    
    def default_headers(self):
        return {
            'Status' : '200 OK'
        } 

    def output_headers(self,out):
        for name, value in self.headers.items():
            out.write("{name}: {value}{DELIMETER}".format(
                name=name, 
                value=value,
                DELIMETER=IViewer.DELIMETER
                )
            )
        out.write(IViewer.DELIMETER)
    def output_body(self, out):
        pass
        
    def output(self, out):
        self.headers = getattr(self, 'headers', {})
        for name, value in self.default_headers().items():
            if name not in self.headers:
                self.headers[name]=value

        self.output_headers(out)
        self.output_body(out)

class XMLViewer(IViewer):
    """    
    Represents XML body answer for WebServer
    """
    def __init__(self, *args, **kwargs):
        super(XMLViewer, self).__init__()

    def default_headers(self):
        return {
            'Status'        : '200 OK',
            'Content-Type'  : 'text/xml'
        }
    def output_body(self, out):
        out.write('<?xml version="1.0" encoding="utf-8" ?>\n')
        out.write('<?xml-stylesheet type="text/xsl" href="%s/static/qserver.xsl" ?>\n' % IViewer.BASE_URL)
        #self.report.GetXMLNode().writexml(out, addindent = "    ", newl = "\r\n")
        self.report.GetXMLNode().writexml(out)
        


class RedirectViewer(IViewer):
    def __init__(self, location, cookies=None):
        super(RedirectViewer, self).__init__()
        self.location = location
        if isinstance(cookies, dict):
            cookies = ';'.join('%s=%s' % kv for kv in cookies.iteritems())
        self.cookies = cookies

        if self.cookies is not None:
            self.headers['Set-Cookie'] = self.cookies
    def default_headers(self):
        return { 
            'Status' : '302 Found',
            'Location' : os.path.join(IViewer.BASE_URL, self.location)
        }


"""LoginView"""
class LoginReport(IReport):
    def __init__(self, tryCount, sourceLocation):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "login")
        self.CreateChild(viewNode, "param", name = "count", value = tryCount)
        self.CreateChild(viewNode, "param", name = "source", value = sourceLocation)


class LoginViewer(XMLViewer):
    def __init__(self, tryCount = 0, sourceLocation = ""):
        self.report = LoginReport(tryCount, sourceLocation)


"HelloView"
class HelloReport(IReport):
    def __init__(self, username, usertype):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "hello")
        self.CreateChild(viewNode, "param", name = "userrole", value = usertype)
        self.CreateChild(viewNode, "param", name = "username", value = username)

class HelloViewer(XMLViewer):
    def __init__(self, user):
        usertype = "team" if isinstance(user, LegalUser) \
                        else ("org" if isinstance(user, AdminUser) else "guest")
        self.report = HelloReport(user.name, usertype)


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
 
class ErrorViewer(XMLViewer):
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

class QuestListViewer(XMLViewer):
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

class QuestViewer(XMLViewer):
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

class QuestCheckViewer(XMLViewer):
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
                    status = "postponed" if qi[3] > 0 else ("j-available" if qi[1] else "j-unavailable")
                    self.CreateChild(catNode, "quest", id = qId, label = questLabel, done = qi[2], status = status, postponed = qi[3])
        rankNode = self.CreateChild(viewNode, "ranklist")
        for team, score in teams:
            self.CreateChild(rankNode, "team", name = team.name, score = score)

class MonitorViewer(XMLViewer):
    def __init__(self, stat, teams):
        self.report = MonitorReport(stat, teams)


"NewsView"
class NewsReport(IReport):
    def __init__(self, news=None, prev=None, next=None, editable=False):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type="news")
        self.CreateChild(viewNode, "param", name="prevPage", value=(prev if prev is not None else ""))
        self.CreateChild(viewNode, "param", name="nextPage", value=(next if next is not None else ""))
        self.CreateChild(viewNode, "param", name="editable", value = "true" if editable else "false")
        for event in news:
            newsNode = self.CreateChild(viewNode, "news", time=time.ctime(event.timeStamp), author=event.authorName, id=event.timeStamp)
            try:
                doc = minidom.parseString("<div class=\"news\">" + event.message.encode("utf-8") + "</div>")
                newsNode.appendChild(doc.documentElement)
            except:
                logging.exception("while processing text [%s]", event.message)
                self.CreateChild(newsNode, "div", **{"class": "news"}).appendChild(factory.createTextNode(event.message))

class GV_News(XMLViewer):
    def __init__(self, news=None, prev=None, next=None):
        self.report = NewsReport(news, prev, next)

class AV_News(XMLViewer):
    def __init__(self, news=None, prev=None, next=None):
        self.report = NewsReport(news, prev, next, True)


"JuryQuestView"
class JuryQuestListReport(IReport):
    def __init__(self, questId, questName, questInfo):
        self.xmlNode = self.CreateReportRoot()
        viewNode = self.CreateChild(self.xmlNode, "view", type = "jury-quest-list")
        questNode = self.CreateChild(viewNode, "quest", id=questId, 
            got=questInfo["got"], done=questInfo["done"], tries=questInfo["tries"], last=questInfo.get("last", ""))
        self.CreateChild(questNode, "name").appendChild(factory.createTextNode(questName))
        self.CreateChild(questNode, "param", name = "quest4open", value="true" if not questInfo["available"] else "false")
        self.CreateChild(questNode, "param", name = "quest4close", value="true" if (questInfo["available"] and questInfo["got"] == 0) else "false")
        ppndFlag = True
        for sol in sorted(questInfo["sollist"], key = lambda s: s.timeStamp):
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
            solNode.setAttribute("file", os.path.join("upload-files", sol.actionString))
        CreateVerdictNode(solNode, status, sol.verdict)

class JuryQuestViewer(XMLViewer):
    def __init__(self, qd, questId, questName, *args):
        if qd:
            self.report = JuryQuestGetReport(qd, questId, questName, *args)
        else:
            self.report = JuryQuestListReport(questId, questName, *args)

