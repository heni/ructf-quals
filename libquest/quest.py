#!/usr/bin/env python2.5

from xml.dom import minidom
import cgi, logging, os
factory = minidom.Document()

class QuestDescriptor:
    @staticmethod
    def decode(text):
        if not isinstance(text, unicode):
            assert isinstance(text, str)
            text = unicode(text, "utf-8")
        return text

    def __init__(self, questID, text = None, html = None, file = None):
        self.questID = questID
        self.xmlNode = factory.createElement("quest")
        self.xmlNode.setAttribute("id", str(questID))
        view = None
        if html:
            try:
                view = factory.createElement("view") 
                view.setAttribute("mode", "html")
                view.appendChild(minidom.parseString(html).documentElement)
            except:
                view = None
        if view is None and text:
            text = self.decode(text)
            view = factory.createElement("view")
            view.setAttribute("mode", "text")
            view.appendChild(factory.createTextNode(text))
        if view:
            self.xmlNode.appendChild(view)
        if file and (not os.access(file, os.R_OK) or not os.path.isfile(file)):
            logging.warning("Can't get access to file '%s', skipping...", file)
            file = None
        if file:
            view = factory.createElement("view")
            view.setAttribute("mode", "attachment")
            view.setAttribute("src", file)
            self.xmlNode.appendChild(view)
        self.text, self.html, self.file = text, html, file

    def GetXMLCode(self):
        return self.xmlNode.toxml()

    def GetXMLNode(self):
        return self.xmlNode

    def GetID(self):
        return self.questID

    @classmethod
    def FromTextMessage(self, message):
        quest = {'questID': None, 'text': None, 'html': None, 'file': None}
        cur = None
        for line in message.split("\n"):
            if line.startswith('ID:'):
                cur = 'questID'; quest[cur] = line[3:]
            elif line.startswith('text:'):
                cur = 'text'; quest[cur] = line[5:]
            elif line.startswith('html:'):
                cur = 'html'; quest[cur] = line[5:]
            elif line.startswith('file:'):
                cur = 'file'; quest[cur] = line[5:]
            elif cur:
                quest[cur] += line
        for q, v in quest.iteritems():
            if v is not None: 
                quest[q] = v.strip()
        return QuestDescriptor(**quest)
