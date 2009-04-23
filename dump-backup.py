#!/usr/bin/env python2.5
# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys, random, optparse, logging, re, time, codecs

from users import *
from questserver import QuestServer
from dispatcher import SmartDecoder

def parse_args():
    parser = optparse.OptionParser(description = "prepares new backup directory")
    parser.set_defaults(bootMode = None)
    parser.add_option("--boot", dest = "bootMode", type = "choice", choices = ["clean", "work"], metavar = "MODE",
        help = "set preparation mode (clean: create new backup dir; work: change existing backup dir)")
    parser.add_option("--users", dest = "usersFile", metavar = "FILE", help = "set file with user accounts")
    opt, args = parser.parse_args()
    if opt.bootMode is None or opt.usersFile is None:
        parser.error("necessary options are skipped")
    return opt, args


def DumpBackup():
    srv = QuestServer("questserver.cfg", True)
    auth = srv.authorizer
    out = codecs.lookup("utf-8")[3](sys.stdout)
    for authstring, user in auth.users.iteritems():
        print >>out, "user: %s\trole: %s\tauthstring: %s" % (user.name, user.profile.GetProperty("role").GetValue(), authstring)
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

