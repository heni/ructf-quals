#!/usr/bin/env python2
from xml.dom import minidom
import logging
import os
import time
import copy
import hashlib
import six
from six.moves import cStringIO

factory = minidom.Document()

from ..common import *


class QuestDescriptor(Unpickable(questID=str,
                                 xmlNode=default,
                                 text=default,
                                 html=default,
                                 file=str,
                                 waitingTime=default)):
    @staticmethod
    def decode(text):
        if not isinstance(text, six.text_type):
            assert isinstance(text, six.binary_type)
            text = six.text_type(text, "utf-8")
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
        self.timeout = None
        if isinstance(timeout, (six.binary_type, six.text_type)):
            timeout = int(timeout.strip())
        if timeout:
            self.timeout = timeout
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

    @staticmethod
    def raw_replace_patterns(text, questId, teamId, salt=None):
        ### TODO salt to config
        salt = salt if salt else "RuCTF-quALs_2013-SaLt!"
        text = text.replace("%TEAM%", teamId)
        text = text.replace("%HASH%", hashlib.md5(questId + teamId + salt).hexdigest())
        return text

    def replace_patterns(self, text, questId, user, salt=None):
        teamId = str(user.profile.GetProperty('teamID').GetValue())
        return self._replace_patterns(text, questId, teamId, salt)

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

        quest = {'questID': [], 'text': {'en': [], 'ru': []}, 'html': {'en': [], 'ru': []}, 'file': [],
                 'timeout': []}
        cur = None
        for line in message.split("\n"):
            if line.startswith('ID:'):
                cur = quest['questID']
                cur.append(line[3:])
            elif line.startswith('text:'):
                cur = quest['text']['ru']
                cur.append(line[5:])
            elif line.startswith('text[en]:'):
                cur = quest['text']['en']
                cur.append(line[9:])
            elif line.startswith('text[ru]:'):
                cur = quest['text']['ru']
                cur.append(line[9:])
            elif line.startswith('html:'):
                cur = quest['html']['ru']
                cur.append(line[5:])
            elif line.startswith('html[ru]:'):
                cur = quest['html']['ru']
                cur.append(line[9:])
            elif line.startswith('html[en]:'):
                cur = quest['html']['en']
                cur.append(line[9:])
            elif line.startswith('file:'):
                cur = quest['file']
                cur.append(line[5:])
            elif line.startswith('timeout:'):
                cur = quest['timeout']
                cur.append(line[8:])
            elif cur:
                cur.append(line)
        recursevly_concat(quest)
        return QuestDescriptor(**quest)


def recursevly_concat(dkt):
    for q, v in six.iteritems(dkt):
        if v:
            if type(v) is dict:
                recursevly_concat(v)
            elif type(v) is list:
                dkt[q] = ''.join(v).strip()
        else:
            dkt[q] = None