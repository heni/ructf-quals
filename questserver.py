#!/usr/bin/env python2
#-*- encoding: utf-8 -*-
from __future__ import with_statement
from common  import *
from errors  import *
from libquest import *
from users   import *
from viewers import *

import imp, os, sys, re, logging, shutil, tempfile, itertools, time, weakref
import bisect
import pickle as _pickle


class QuestSolution(Unpickable(timeStamp=float, 
                        username=str,
                        actionString=unicode,
                        callObject=default,
                        solutionID=str,
                        status=default,
                        verdict=unicode)):

    def __init__(self, username, actionString, verdictStatus, verdictMessage, ref = None):
        super(QuestSolution, self).__init__()
        self.timeStamp = time.time()
        self.username = username
        self.actionString = actionString
        self.callObject = ref
        self.ChangeVerdict(verdictStatus, verdictMessage)
        self.solutionID = str(id(self))

    def ChangeVerdict(self, verdictStatus, verdictMessage):
        self.status = verdictStatus
        self.verdict = verdictMessage
        if getattr(self, "callObject", None):
            self.callObject.OnChangeVerdict(self)


class QuestActions(Unpickable(descriptor=default,
            solutions=list,
            status=default,
            callbacks=set)):

    def __init__(self):
        self.descriptor = None
        self.solutions = []
        self.status = None
        self.callbacks = set()

    def ChangeStatus(self, status):
        if self.status != status:
            old_status = self.status
            checklist = [sol.status for sol in self.solutions if sol.status is not None]
            self.status = any(checklist) or (False if len(checklist) > 0 else None)
            if self.status != old_status:
                for cb in self.callbacks:
                    cb(self.status)

    def OnUserAction(self, solution):
        if not self.status:
            self.solutions.append(solution)
            self.ChangeStatus(solution.status)

    def OnChangeVerdict(self, solution):
        self.ChangeStatus(solution.status)

    def SetChangeCallback(self, cb):
        assert callable(cb), "Can't register non-callable functions"
        self.callbacks = set([cb])


class NewsItem(Unpickable(timeStamp=float,
                authorName=str,
                message=unicode)):

    def __init__(self, author, text):
        super(NewsItem, self).__init__()
        self.timeStamp = time.time()
        self.authorName = author
        self.message = SmartDecoder.decode(text)


class NewsStorage(Unpickable(container=list)):
    news4page = 10
   
    @classmethod
    def create(cls, o=None):
        if isinstance(o, cls):
            return o
        return cls()

    def AddNewsItem(self, event):
        assert isinstance(event, NewsItem)
        self.container.insert(0, event)

    def DeleteNewsItem(self, timeStamp):
        timeStamp = float(timeStamp)
        indices = [i for i in xrange(len(self.container)) if abs(self.container[i].timeStamp - timeStamp) < 0.1]
        assert len(indices) == 1, "can't delete non-single eventlist %r for timestamp %r" % (indices, timeStamp)
        self.container.pop(indices[0])

    def ListNewsItems(self, pageID):
        pageID = int(pageID)
        return {"news": self.container[pageID * self.news4page : (pageID + 1) * self.news4page], 
            "next": pageID + 1 if (pageID + 1) * self.news4page < len(self.container) else None,
            "prev": min(pageID - 1, len(self.container) / self.news4page) if pageID > 0 else None}


class ViewsStorage(Unpickable(container=dict)):
    PerUserViews = 50
    
    @classmethod
    def create(cls, o=None):
        if isinstance(o, cls):
            return o
        return cls()

    def RegisterViewer(self, user, viewer):
        teamID = user.profile.GetProperty("teamID").GetValue()
        userViewers = self.container.setdefault(user.name, [])
        if len(userViewers) > self.PerUserViews:
            userViewers[:len(userViewers) + 1 - self.PerUserViews] = []
        viewID = hex(int(time.time() * 100))[2:]
        userViewers.append((viewID, viewer.report))
        return viewID

    def GetViewer(self, user, viewID):
        teamID = user.profile.GetProperty("teamID").GetValue()
        userViewers = self.container.setdefault(user.name, [])
        idx = bisect.bisect_left(userViewers, (viewID, None))
        if idx < len(userViewers):
            fID, fReport = userViewers[idx]
            if fID == viewID:
                viewer = IViewer()
                viewer.report = fReport
                return viewer


class QuestHolder:

    def __init__(self, directory, description):
        items = description.split(":")
        loadFn = getattr(self, "load_" + items[0], None)
        assert callable(loadFn), "incorrect loader for type: %s" % items[0]
        loadFn(directory, items[1])

    def load_xml(self, directory, file):
        file = os.path.join(directory, file)
        self.provider = XMLQuestProvider(file)
        self.serial = os.stat(file).st_mtime

    def load_ext(self, directory, file):
        file = os.path.join(directory, file)
        self.provider = ScriptQuestProvider(file)
        self.serial = os.stat(file).st_mtime

    def load_py(self, directory, file):
        file = os.path.join(directory, file)
        modname, ext = os.path.splitext(file)
        sfx = [sfx for sfx in imp.get_suffixes() if sfx[0] == ext]
        assert len(sfx) == 1, "can't load %s as python module" % file
        mod = imp.load_module("questprovider", open(file, sfx[0][1]), file, sfx[0])
        providername = mod.__all__[0]
        self.provider = getattr(mod, providername)()
        self.serial = os.stat(file).st_mtime

    def CreateQuest(self, teamID):
        return self.provider.CreateQuest(teamID)

    def OnUserAction(self, desc, action):
        try:
            status, verdict = self.provider.OnUserAction(desc, action)
        except:
            status, verdict = None, "Checker error occured"
            logging.exception("QuestHolder.OnUserAction")
        verdict = SmartDecoder.decode(verdict)
        return status, verdict

    def GetId(self):
        return self.provider.GetId()

    def GetSerial(self):
        return self.serial

    def GetCategory(self):
        return self.provider.GetSeries()

    def GetName(self):
        name = self.provider.GetName()
        if isinstance(name, str):
            name = unicode(name, "utf-8")
        return name

    def SaveState(self, directory):
        saveId = re.sub(':', '-', self.GetId())
        saveDir = tempfile.mkdtemp(prefix = "%s_" % saveId, dir = directory)
        os.chmod(saveDir, 0777)
        self.provider.SaveState(saveDir)
        with open(os.path.join(directory, saveId), 'w') as savefile:
            _pickle.dump(saveDir, savefile)

    def LoadState(self, directory):
        saveId = re.sub(':', '-', self.GetId())
        if os.path.isfile(os.path.join(directory, saveId)):
            with open(os.path.join(directory, saveId), 'r') as savefile:
                saveDir = _pickle.load(savefile)
                saveDir = os.path.join(directory, os.path.split(saveDir)[1])
            self.provider.LoadState(saveDir)      
        else:
            logging.warning("QuestHolder %s can't be restored", saveId)


class TeamChangeCallback:

    def __init__(self, teamname, questId, tracker):
        self.tracker = tracker
        self.teamname = teamname
        self.questId = questId
        self.scoreValue = int(questId.split(":")[-1])

    def __call__(self, status):
        logging.info("TeamChangeCallback {user=%s questId=%s status=%s}", self.teamname, self.questId, status)
        tracker = self.tracker
        if status == True:
            tracker.questInfo.setdefault(self.questId, {}).setdefault("done", set()).add(self.teamname)
            if self.teamname in tracker.teamScores:
                tracker.teamScores[self.teamname] += self.scoreValue
        elif self.teamname in tracker.questInfo.get(self.questId, {}).get("done", set()):
            tracker.questInfo[self.questId]["done"].remove(self.teamname)
            if self.teamname in tracker.teamScores:
                tracker.teamScores[self.teamname] -= self.scoreValue
        logging.info("New values [questinfo: %s], [teamScores: %s]", tracker.questInfo, tracker.teamScores)


class AvailQuestChecker:
    def __init__(self, tracker, testMode=False):
        self.tracker = tracker
        self.testMode = testMode

    def IsQuestAvailable(self, qId, user = None):
        if self.testMode or self.tracker.IsQuestOpenedManually(qId): 
            return True
        cat = qId.split(":")[0]
        if cat not in self.tracker.catlist: return False
        availFlag = True
        for _q in self.tracker.catlist[cat]:
            if qId == _q: break
            availFlag = availFlag and self.tracker.IsQuestDone(_q)
        return availFlag

    def GetStat(self, fn):
        stat = {}
        for cat, catlist in self.tracker.catlist.iteritems():
            stat[cat] = []
            availFlag = True
            for qId in catlist:
                localAvailFlag = self.testMode or self.tracker.IsQuestOpenedManually(qId) or availFlag
                stat[cat].append(fn(qId, localAvailFlag))
                availFlag = availFlag and self.tracker.IsQuestDone(qId)
        return stat


class TrackerInternals(Unpickable(teamActions=dict,
                teamScores=emptydict,
                questInfo=dict,
                newsStorage=NewsStorage.create,
                views=ViewsStorage.create)): pass


class TeamActionsTracker:

    def __init__(self, questserver):
        self.__dict__.update(TrackerInternals().__dict__)
        self.qholder = dict((qh.GetId(), qh) for qh in questserver.quest.itervalues())
        self.catlist = dict((catname, list(catlist)) for catname, catlist \
                                in itertools.groupby(
                                        sorted(self.qholder), 
                                        key = lambda qId: self.qholder[qId].GetCategory()))
        self.availChecker = AvailQuestChecker(self, questserver.openAll)

    def GetTeamScore(self, teamname):
        score = self.teamScores.get(teamname, None)
        if score is not None: return score
        score = self.CalcTeamScore(teamname)
        self.teamScores[teamname] = score
        return score

    def CalcTeamScore(self, teamname):
        return sum(int(qId.split(":")[-1]) for qId, st in self.GetTeamQuestFreeze(teamname) if st)

    def RankTeams(self, teamlist):
        return sorted(teamlist, key = lambda team: self.GetTeamScore(team.name), reverse = True)

    def GetTeamQuestFreeze(self, teamname):
        actions = self.teamActions.get(teamname, {})
        return ((qId, bool(actions[qId].status) if qId in actions else None) for qId in self.qholder)

    def CheckQuestDepends(self, teamname, qId):
        return self.availChecker.IsQuestAvailable(qId, teamname)

    def GetTeamAction(self, teamname, qId, create = False):
        if create and self.CheckQuestDepends(teamname, qId):
            qi = self.teamActions.setdefault(teamname, {})
            if qId not in qi:
                qi[qId] = act = QuestActions()
                act.SetChangeCallback(TeamChangeCallback(teamname, qId, self))
        return  self.teamActions.get(teamname, {}).get(qId, None)

    def GetQuest(self, teamname, teamID, qId):
        act = self.GetTeamAction(teamname, qId, True)
        if act is not None:
            questHolder = self.qholder[qId]
            gotInformation = self.questInfo.setdefault(qId, {}).setdefault("got", {})
            if isinstance(gotInformation, set): #LEGACY scheme
                gotInformation = self.questInfo.setdefault(qId, {})["got"] = dict((u, 0.0) for u in gotInformation)
            if gotInformation.get(teamname, 0.0) < questHolder.GetSerial() \
                    or act.descriptor is None \
                    or getattr(act.descriptor, "waitingTime") and act.descriptor.waitingTime < time.time():
                act.descriptor = self.qholder[qId].CreateQuest(teamID)
                gotInformation[teamname] = questHolder.GetSerial()
            return act.descriptor
        
    def OnSubmit(self, teamname, qId, actionString):
        act = self.GetTeamAction(teamname, qId, True)
        if act is not None and act.descriptor:
            #restriction not more than one submit in 30 seconds on 1 task
            if not act.solutions or time.time() - act.solutions[-1].timeStamp > 30:
                verdict = self.qholder[qId].OnUserAction(act.descriptor, actionString)
                act.OnUserAction(QuestSolution(teamname, actionString, *verdict, **{'ref': act}))
                return verdict

    def IsQuestDone(self, qId, user = None):
        doneSet = self.questInfo.get(qId, {}).get("done", set())
        return (user in doneSet) if user else bool(doneSet)

    def IsQuestOpenedManually(self, qId):
        return self.questInfo.get(qId, {}).get("open", False)

    def OpenQuest(self, qId):
        self.questInfo.setdefault(qId, {})["open"] = True

    def CloseQuest(self, qId):
        self.questInfo.setdefault(qId, {})["open"] = False

    def GetQuestStat(self, qId, checkAvailability=False):
        qi = self.questInfo.get(qId, {})
        gotTeams = qi.get("got", dict())
        doneCount = len(qi.get("done", set()))
        solList = itertools.chain(*(self.GetTeamAction(teamname, qId).solutions for teamname in gotTeams))
        return {"got": len(gotTeams), "done": doneCount, "sollist": solList, 
            "available": self.CheckQuestDepends(None, qId) if checkAvailability else None}

    def GetTeamStat(self, teamname):
        freeze = dict(self.GetTeamQuestFreeze(teamname))
        def infoFun(qId, availFlag):
            if freeze[qId]: return qId, True
            return qId, None if availFlag else False
        return self.availChecker.GetStat(infoFun)

    def GetCommonStat(self):
        def infoFun(qId, availFlag):
            return qId, availFlag, len(self.questInfo.get(qId, {}).get("done", set()))
        return self.availChecker.GetStat(infoFun)

    def GetJuryStat(self):
        def infoFun(qId, availFlag):
            st = self.GetQuestStat(qId)
            doneCount = st["done"]
            postponedCount = len([1 for s in st["sollist"] if s.status is None])
            return qId, availFlag, doneCount, postponedCount 
        return self.availChecker.GetStat(infoFun)

    def LoadState(self, file):
        _firstObject = _pickle.load(file)
        if isinstance(_firstObject, dict):
            #legacy loading scheme
            logging.warning("using LEGACY startup scheme for TeamActionsTracker object")
            self.teamActions = _firstObject
            self.teamScores = _pickle.load(file)
            self.questInfo = _pickle.load(file)
            self.newsStorage = NewsStorage.create()
            self.views = ViewsStorage.create()
        elif isinstance(_firstObject, TrackerInternals):
            #new loadin scheme
            internals = _firstObject
            self.__dict__.update(internals.__dict__)
            for teamname, qi in self.teamActions.iteritems():
                for qId, act in qi.iteritems():
                    try:
                        act.SetChangeCallback(TeamChangeCallback(teamname, qId, self))
                    except:
                        logging.exception("can't load team %s action for task %s", teamname, qId)

    def SaveState(self, file):
        internals = TrackerInternals()
        for attr in internals.__dict__:
            setattr(internals, attr, getattr(self, attr))
        _pickle.dump(internals, file)


class QuestServer:
    BACKUP_PREFIX = "backup_"

    def __init__(self, configurator, restoreFlag = False):
        self.Load(configurator)
        if not restoreFlag:
            self.BackupPrepare()
        else:
            self.Restore()

    def Load(self, configurator):
        cp = configurator
        #initialize quest providers
        self.catlist = {}
        self.quest = {}
        categories = cp.get("DEFAULT", "categories").split(":")
        for cat in categories:
            name = cp.get(cat, "name")
            directory = cp.get(cat, "dir")
            for opt in cp.options(cat):
                desc = cp.get(cat, opt)
                sRes = re.match("q(\d+)", opt)
                if sRes and desc != "none":
                    try:
                        qholder = QuestHolder(directory, desc)
                        qId = qholder.provider.GetId()
                        self.quest[qId] = qholder
                    except:
                        logging.exception("can't load quest provider %s", desc)
            self.catlist[cat] = name
        #initialize backup subsystem
        self.backupdir = cp.get("backup", "dir")
        self.backupcnt = cp.getint("backup", "savecount")
        self.backupidx = 0
        self.savefile = cp.get("backup", "savefile")
        #http server parameters
        self.serverName = cp.get("DEFAULT", "srv_name")
        self.basePath = cp.get("DEFAULT", "base_path")
        self.baseUrl = cp.get("DEFAULT", "base_url")
        self.workersCount = cp.getint("DEFAULT", "workers")
        self.openAll = cp.getboolean("DEFAULT", "open_all")
        #initialize user authorizer and tracker
        self.authorizer = Authorizer()
        self.tracker = TeamActionsTracker(self)

    def BackupPrepare(self):
        if not os.path.isdir(self.backupdir):
            os.makedirs(self.backupdir)
            os.chmod(self.backupdir, 0777)
        if os.listdir(self.backupdir):
            raise InitializationError("Please manually remove files from %s directory" % self.backupdir)

    def GetBackupList(self):
        return sorted((item for item in os.listdir(self.backupdir) if self.GetBackupIndex(item) is not None), 
                    reverse = True, key = self.GetBackupIndex)

    def GetBackupIndex(self, dir):
        if dir.startswith(self.BACKUP_PREFIX):
            return int(dir[len(self.BACKUP_PREFIX):], 16)

    def Restore(self):
        assert os.path.isdir(self.backupdir), "Application can't restore. Backup directory [%s] doesn't exist" % self.backupdir
        backupList = self.GetBackupList()
        loadFlag = False
        for backupItem in backupList:
            try:
                self.LoadState(os.path.join(self.backupdir, backupItem))
                loadFlag = True
                break
            except:
                logging.exception("can't restore from %s, trying next", os.path.join(self.backupdir, backupItem))
        assert loadFlag, "Application can't automatically restore" 
        self.backupidx = 1 + self.GetBackupIndex(backupList[0])

    def SaveState(self, directory):
        with open(os.path.join(directory, self.savefile), "w") as writer:
            _pickle.dump(self.authorizer, writer)
            self.tracker.SaveState(writer)
        for qHolder in self.quest.itervalues():
            qHolder.SaveState(directory)

    def LoadState(self, directory):
        with open(os.path.join(directory, self.savefile), "r") as reader:
            self.authorizer = _pickle.load(reader)
            self.tracker.LoadState(reader)
        for qHolder in self.quest.itervalues():
            qHolder.LoadState(directory)

    def Backup(self):
        directory = os.path.join(self.backupdir, "%s%06x" % (self.BACKUP_PREFIX, self.backupidx))
        self.backupidx += 1
        os.makedirs(directory)
        os.chmod(directory, 0777)
        self.SaveState(directory)
        backupList = self.GetBackupList()
        for d in backupList[self.backupcnt:]:
            shutil.rmtree(os.path.join(self.backupdir, d))

    def GetQuestList(self, username):
        stat = self.tracker.GetTeamStat(username)
        return stat

    def GetQuestName(self, questId):
        return self.quest[questId].GetName() if questId in self.quest else ''

    def GetQuest(self, username, questId):
        teamID = self.authorizer.GetTeamID(username)
        qd = self.tracker.GetQuest(username, teamID, questId)
        return qd

    def CheckQuest(self, username, questId, actionString):
        verdict = self.tracker.OnSubmit(username, questId, actionString)
        return verdict

    def Authenticate(self, auth):
        user = self.authorizer.Authenticate(auth)
        return user or GuestUser()

    def CreateUser(self, username, role, authstring):
        user = self.authorizer.Authenticate(authstring)
        if user:
            logging.warning("can't rewrite existing user %s", user.name)
            return None
        else:
            user = LegalUser(username) if role == "team" \
                else AdminUser(username) if role == "org" \
                else None
            if user:
                self.authorizer.AddUser(authstring, user)
        return user

    def GetRankedTeams(self):
        teams = self.authorizer.GetTeams()
        return [(team, self.tracker.GetTeamScore(team.name)) for team in self.tracker.RankTeams(teams)]

    def GetMonitor(self):
        return self.tracker.GetCommonStat(), self.GetRankedTeams()

    def GetJuryMonitor(self):
        return self.tracker.GetJuryStat(), self.GetRankedTeams()

    def GetQuestSolutions(self, questId, filterFn = None):
        solList = itertools.ifilter(filterFn, self.tracker.GetQuestStat(questId)["sollist"])
        return solList

    def ListNewsItems(self, pageID):
        return self.tracker.newsStorage.ListNewsItems(pageID)

    def AddNewsItem(self, user, text):
        event = NewsItem(user.name, text)
        self.tracker.newsStorage.AddNewsItem(event)

    def DeleteNewsItem(self, eventID):
        self.tracker.newsStorage.DeleteNewsItem(eventID)

    def RegisterViewer(self, user, viewer):
        return self.tracker.views.RegisterViewer(user, viewer)

    def GetViewer(self, user, viewID):
        return self.tracker.views.GetViewer(user, viewID)
