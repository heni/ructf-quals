#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
"""Python Quest Module for xml-encoded quests
Sample quest description:

  <quest series="arith" id="arith:10" proto="xmlquest-1.0">
    <name>Arith 10</name>
    <task>Вычислите выражение: 2 + 2</task>
    <checker strict="yes">
        <solution>4</solution>
    </checker>
  </quest>

Usage:
    try:
      provider = XMLQuestProvider("arith-10.xml")
    except e:
      print >>sys.stderr, "Can't create quest provider"
      sys.exit(1)
    quest = provider.CreateQuest()
    print "Please solve out quest [%s]" % provider.GetName()
    print provider.GetTextDescription(quest)
    userString = sys.stdin.readline()
    if provider.OnUserAction(userString) == True:
      print "You are right. :)"
    else:
      print "You are wrong. :("    
"""

from xml.dom.minidom import parse as parseXML
from quest import QuestDescriptor
import cgi, logging 

def StripActionString(line):
  return line.strip()

def GetText(nodes):
  rc = None
  for node in nodes:
    rc = ""
    for node in node.childNodes:
      if node.nodeType == node.TEXT_NODE:
        rc += node.data
  return rc
    
def ParseXMLQuest(file):
  doc = parseXML(file)
  root = doc.documentElement
  assert root.tagName == "quest" 
  assert root.getAttribute("proto") == "xmlquest-1.0"
  quest = {
      "series": root.getAttribute("series"),
      "id": root.getAttribute("id"),
      "name": GetText(root.getElementsByTagName("name")),
      "text": None,
      "html": None,
      "solution": [],
      "uncheck_verdict": None,
      "file": GetText(root.getElementsByTagName("file"))
      #"dependencies": [node.getAttribute("quest-id") for node in root.getElementsByTagName("dependency")]
  }
  if root.getElementsByTagName("checker"):
      checker = root.getElementsByTagName("checker")[0]
      quest["solution"] = [GetText([node]) for node in checker.getElementsByTagName("solution")]
      quest["uncheck_verdict"] = False if checker.getAttribute("strict").lower() == "yes" else None
  taskNode = root.getElementsByTagName("task")[0]
  if taskNode.getAttribute("type") == "html":
      quest["html"] = '<?xml version="1.0" encoding="utf-8" ?>' + ''.join(ch.toxml() for ch in taskNode.childNodes).encode('utf-8')
  else:
      quest["text"] = GetText([taskNode])
  return quest


class XMLQuestProvider:

  def __init__(self, file):
    descriptor = ParseXMLQuest(file)
    self.series = descriptor["series"]
    self.id = descriptor["id"]
    self.name = descriptor["name"]
    self.text = descriptor["text"]
    self.html = descriptor["html"]
    self.solution = set(descriptor["solution"])
    self.file = descriptor["file"]
    self.uncheckVerdict = descriptor["uncheck_verdict"]
    #self.dependencies = descriptor["dependencies"]
  
  def CreateQuest(self):
    return QuestDescriptor(0, text = self.text, html = self.html, file = self.file)

  def GetId(self):
    return self.id

  def GetSeries(self):
    return self.series

  def GetName(self):
    return self.name

  #def CheckDependencies(self, *solved):
  #  acceptFlag = all([depQuest in solved for depQuest in self.dependencies])
  #  return acceptFlag
  #
  #def GetTextDescription(self, qId):
  #  return self.task
  #
  #def GetHTMLDescription(self, qId):
  #  return cgi.escape(self.task)

  def OnUserAction(self, dscr, actionString):
    actionString = StripActionString(actionString)
    solveFlag = (actionString in self.solution) or self.uncheckVerdict
    return (solveFlag, "")

  def SaveState(self, directory):
    pass

  def LoadState(self, directory):
    pass

