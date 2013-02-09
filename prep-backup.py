#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import with_statement
import sys, random, optparse, logging, re
from ConfigParser import ConfigParser

from users import *
from questserver import QuestServer

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


auth_voc = "abcdefghijklmnopqrstuvwxyz_0123456789"
def CreateAuthString():
    return "".join(random.choice(auth_voc) for _ in xrange(10))


def GetUsersList(usersFile):
    """\
File format:
team USERNAME AUTHSTRING
org  USERNAME AUTHSTRING"""
    userList = []
    with open(usersFile) as reader:
        for line in reader:
            if line.strip().startswith('#'):
                continue
            if not re.match("^[\x01-\x7F]+$", line):
                continue
            sRes = re.match("(\w+)\s+(\S+)\s+([<\w>]+)\s*$", line)
            if sRes and sRes.group(1) in ("org", "team"):
                userrole = sRes.group(1)
                username = sRes.group(2)
                authstring = sRes.group(3)
                if authstring == '<generate>':
                    authstring = CreateAuthString()
                userList.append((username, userrole, authstring))
    return userList


def CreateBackup(userList, restoreFlag):
    configurator = ConfigParser()
    assert "questserver.cfg" in configurator.read("questserver.cfg")
    srv = QuestServer(configurator, restoreFlag)
    for username, userrole, authstring in userList:
        if srv.CreateUser(username, userrole, authstring):
            print "user: %s\trole: %s\tauth: %s\tcreated." % (username, userrole, authstring)
    srv.Backup()


def main(opt, args):  
    logging.getLogger().setLevel(logging.DEBUG)
    try:
        userList = GetUsersList(opt.usersFile)
        restoreFlag = {"work": True, "clean": False}[opt.bootMode]
        CreateBackup(userList, restoreFlag)
    except:
        logging.exception("can't create backup directory")


if __name__ == "__main__":
    main(*parse_args())

