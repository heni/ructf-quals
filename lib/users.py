#!/usr/bin/env python2
# -*- encoding: utf-8 -*-
import errors
import logging

__all__ = ['Authorizer', 'GuestUser', 'LegalUser', 'AdminUser', 'UserProfile']

class IProperty(object):

    def __init__(self, name, description, defaultValue = ""):
        self.name = name 
        self.description = description
        self.__value = defaultValue
        self.__resetCount = 0
    
    def CheckProperty(self, value):
        return self.__value == value
    
    def GetValue(self):
        return self.__value
    
    def SetValue(self, value):
        self.__value = value

    #использовать только для однократного установления значения
    def ResetValue(self, value):
        assert self.__resetCount == 0
        self.__value = value
        self.__resetCount += 1


class CheckProperty(IProperty):
    GetValue = None

class ReadOnlyProperty(IProperty):
    SetValue = None

class ReadWriteProperty(IProperty):
    pass


class UserProfile:

    def __init__(self, nick, role):
        self.__properties = {}
        self.__appendProperty(ReadOnlyProperty("nick", "Ник", nick))
        self.__appendProperty(ReadOnlyProperty("role", "Уровень полномочий", role))
        self.__appendProperty(ReadWriteProperty("team", "Команда", ""))
        self.__appendProperty(ReadWriteProperty("city", "Город", ""))
        self.__appendProperty(ReadOnlyProperty("teamID", "числовой идентификатор", None))

    def __appendProperty(self, prop):
        self.__properties[prop.name] = prop

    def GetProperties(self):
        return self.__properties.keys()

    def GetProperty(self, propname):
        if propname in self.__properties:
            return self.__properties[propname]
        raise errors.ArgumentError("No such property %s", propname)

    def SaveStatus(self, directory):
        raise errors.NotImplementedError()

    def LoadStatus(self, directory):
        raise errors.NotImplementedError()
    

class IUser(object): 
    def __init__(self):
        raise errors.NotImplementedError()

class GuestUser(IUser):
    def __init__(self):
        self.name = "guest"

class LegalUser(IUser):
    def __init__(self, nick):
        self.name = nick
        self.profile = UserProfile(nick, "team")

class AdminUser(IUser):
    def __init__(self, nick):
        self.name = nick
        self.profile = UserProfile(nick, "org")


class Authorizer:

    def __init__(self):
        self.users = {}
        self.objects = {}

    def Authenticate(self, authstring):
        if authstring in self.users:
            username = self.users[authstring]
            userobject = self.objects[username]
            return userobject

    def AddUser(self, authstring, userobject):
        username = userobject.name
        teamID = len(self.users)
        userobject.profile.GetProperty("teamID").ResetValue(teamID)
        self.users[authstring] = username
        self.objects[username] = userobject

    def GetTeams(self):
        return [u for u in self.objects.itervalues() if isinstance(u, LegalUser)]

    def GetAdmins(self):
        return [u for u in self.objects.itervalues() if isinstance(u, AdminUser)]

    def GetTeamID(self, teamname):
        if teamname in self.objects:
            return self.objects[teamname].profile.GetProperty("teamID").GetValue()

