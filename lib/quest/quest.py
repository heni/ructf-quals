#!/usr/bin/env python2
from xml.dom import minidom
import logging
import os
import cStringIO
import time
import copy
import hashlib


factory = minidom.Document()

from common import *


class QuestDescriptor(Unpickable(questID=str,
                                 xmlNode=default,
                                 text=default,
                                 html=default,
                                 file=str,
                                 waitingTime=default)):
    @staticmethod
    def decode(text):
        if not isinstance(text, unicode):
            assert isinstance(text, str)
            text = unicode(text, "utf-8")
        return text

    @classmethod
    def create(cls, o):
        if isinstance(o, cls):
            return o
        raise RuntimeError("can't copy non QuestDescriptor object")

    def __init__(self, questID, text=None, html=None, file=None, timeout=None):
        super(QuestDescriptor, self).__init__()
        self.questID = questID
        self.xmlNode = factory.createElement("quest")
        self.xmlNode.setAttribute("id", str(questID))
        if isinstance(timeout, (str, unicode)):
            timeout = int(timeout.strip())
        if timeout:
            self.waitingTime = int(time.time() + timeout)
            self.xmlNode.setAttribute("waitingTime", time.ctime(self.waitingTime))
        self.text, self.html, self.file = text, html, file

    def GetXMLCode(self, lang, questId, user):
        return self.GetXMLNode(lang, questId, user).toxml()

    def GetTextPresentation(self):
        buffer = cStringIO.StringIO()
        print >> buffer, "ID: %s" % self.questID
        if self.text:
            print >> buffer, "text: ", self.text
        if self.html:
            print >> buffer, "html: ", self.html
        if self.file:
            print >> buffer, "file: %s" % self.file
        if self.waitingTime:
            print >> buffer, "timeout: %s" % int(self.waitingTime - time.time())
        return buffer.getvalue()

    def replace_patterns(self, text, questId, user):
        ### TODO salt to config
        salt = "RuCTF-quALs_2013-SaLt!"
        teamId = str(user.profile.GetProperty('teamID').GetValue())
        text = text.replace("%TEAM%", teamId)
        text = text.replace("%HASH%", hashlib.md5(questId + teamId + salt).hexdigest())
        return text

    def GetXMLNode(self, lang, questId, user):
        view = None
        if self.html[lang]:
            try:
                html = self.replace_patterns(self.html[lang], questId, user)
                view = factory.createElement("view")
                view.setAttribute("mode", "html")
                view.appendChild(minidom.parseString(html).documentElement)
            except:
                logging.exception("can't parse html object: %s", self.html)
                view = None
        if view is None and self.text[lang]:
            text = self.replace_patterns(self.decode(self.text[lang]), questId, user)
            view = factory.createElement("view")
            view.setAttribute("mode", "text")
            view.appendChild(factory.createTextNode(text))
        xmlNode = copy.deepcopy(self.xmlNode)
        if view:
            xmlNode.appendChild(view)
 
        if self.file and (not os.access(self.file, os.R_OK) or not os.path.isfile(self.file)):
            logging.warning("Can't get access to file '%s', skipping...", self.file)
            self.file = None
        if self.file:
            view = factory.createElement("view")
            view.setAttribute("mode", "attachment")
            view.setAttribute("src", self.file)
            xmlNode.appendChild(view)
        return xmlNode

    def GetID(self):
        return self.questID

    @classmethod
    def FromTextMessage(self, message):
        quest = {'questID': None, 'text': None, 'html': None, 'file': None, 'timeout': None}
        cur = None
        for line in message.split("\n"):
            if line.startswith('ID:'):
                cur = 'questID';
                quest[cur] = line[3:]
            elif line.startswith('text:'):
                cur = 'text';
                quest[cur] = line[5:]
            elif line.startswith('html:'):
                cur = 'html';
                quest[cur] = line[5:]
            elif line.startswith('file:'):
                cur = 'file';
                quest[cur] = line[5:]
            elif line.startswith('timeout:'):
                cur = 'timeout';
                quest[cur] = line[8:]
            elif cur:
                quest[cur] += line
        for q, v in quest.iteritems():
            if v is not None:
                quest[q] = v.strip()
        return QuestDescriptor(**quest)
