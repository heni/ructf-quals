#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys,os, random, logging, re, time, codecs

import six
from six.moves.configparser import ConfigParser

#sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from lib.users import *
from lib.questserver import QuestServer
from lib.dispatcher import SmartDecoder

def DumpBackup():
    configurator = ConfigParser()
    assert "questserver.cfg" in configurator.read("questserver.cfg")
    srv = QuestServer(configurator, True)
    auth = srv.authorizer
    out = codecs.lookup("utf-8")[3](sys.stdout)
    for authstring, username in auth.users.iteritems():
        user = auth.objects[username]
        print >>out, "teamID: %s, user: %s\trole: %s\tauthstring: %s" \
            % (user.profile.GetProperty("teamID").GetValue(), user.name, user.profile.GetProperty("role").GetValue(), authstring)
        if isinstance(user, LegalUser):
            userScore = srv.tracker.GetTeamScore(user.name)
            print >>out, "\tscore: %s\n\tTask actions:" % userScore
            qi = srv.tracker.teamActions.get(user.name, {})
            for qId in sorted(qi):
                act = qi[qId]
                print >>out, "\t\ttask '%s' [%s]" % (qId, act.status)
                for sol in sorted(act.solutions, key = lambda sol: sol.timeStamp):
                    try:
                        msg = "\t\t\t[%s]\tanswer: %s\tverdict: %s, %s" % (time.ctime(sol.timeStamp), 
                            sol.actionString, sol.status, SmartDecoder.decode(sol.verdict))
                        if unicode(msg):
                            print >>out, msg
                    except:
                        logging.exception("")



def main():  
    logging.getLogger().setLevel(logging.DEBUG)
    DumpBackup()


if __name__ == "__main__":
    main()

