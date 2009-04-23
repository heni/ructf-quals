#!/usr/bin/env python2.5
# -*- encoding: utf-8 -*-
import errors

__all__ = ['Authorizer', 'GuestUser', 'LegalUser', 'AdminUser', 'UserProfile']

class IProperty(object):

    def __init__(self, name, description, defaultValue = ""):
        self.name = name 
        self.description = description
        self.__value = defaultValue
    
    def CheckProperty(self, value):
        return self.__value == value
    
    def GetValue(self):
        return self.__value
    
    def SetValue(self, value):
        self.__value = value


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

    def Authenticate(self, authstring):
        if authstring in self.users:
            userobject = self.users[authstring]
            return userobject

    def AddUser(self, authstring, userobject):
        self.users[authstring] = userobject

    def GetTeams(self):
        return [u for u in self.users.itervalues() if isinstance(u, LegalUser)]

    def GetAdmins(self):
        return [u for u in self.users.itervalues() if isinstance(u, AdminUser)]

