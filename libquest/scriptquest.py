#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
"""Python Quest Module for external script quests
"""

from subprocess import Popen, PIPE, CalledProcessError
import logging, os, tempfile, shutil
from quest import QuestDescriptor

class ScriptQuestError(Exception): pass

class ScriptQuestProvider:

  def __init__(self, file):
    self.progname = file
    self.dir = tempfile.mkdtemp()
    self.executable = os.path.abspath(file)
    assert os.access(self.executable, os.X_OK)
    self.questId = self.getProgOutput("id", self.dir)
    self.series = self.getProgOutput("series", self.dir)
    self.name = self.getProgOutput("name", self.dir)

  def getProgOutput(self, *args):
    logging.info("Executing external application: %s %s", self.progname, args)
    executor = Popen((self.progname,) + args, stdout = PIPE, stderr = PIPE, stdin = PIPE, executable = self.executable)
    out, err = executor.communicate("")
    progline = "%s %s" % (self.progname, " ".join(args))
    if err != "":
      logging.warning(" nonempty stderr from '%s': %s", progline, err)
    if executor.poll() != 0:
      raise CalledProcessError(executor.poll(), progline)
    return out.strip()

  def CreateQuest(self):
    return QuestDescriptor.FromTextMessage(self.getProgOutput("create", self.dir))

  def GetId(self):
    return self.questId

  def GetSeries(self):
    return self.series

  def GetName(self):
    return self.name

  def OnUserAction(self, desc, actionString):
    qId = desc.GetID()
    logging.info("Executing external application: %s user %s %s", self.progname, self.dir, qId)
    executor = Popen([self.progname, "user", self.dir, qId], stdin = PIPE, stdout = PIPE, stderr = PIPE, executable = self.executable)
    out, err = executor.communicate(actionString)
    if err != "":
        logging.warning(" nonempty stderr from '%s user %s': %s", self.progname, qId, err)
    return (executor.poll() == 0, out)

  def SaveState(self, directory):
    shutil.rmtree(directory)
    shutil.copytree(self.dir, directory)
    os.chmod(directory, 0777)

  def LoadState(self, directory):
    shutil.rmtree(self.dir)
    shutil.copytree(directory, self.dir)

