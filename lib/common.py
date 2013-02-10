from __future__ import with_statement
import threading, time, logging, os, hashlib, re
import types

def default(o=None):
    return o

def emptydict(*argc):
    return {}

def Unpickable(**kws):
    class ObjBuilder(object):
        def __init__(self, desc):
            if callable(desc):
                self.fn = desc
                self.defargs = ()
            elif isinstance(desc, (tuple, list)):
                self.fn = desc[0]
                self.defargs = desc[1] if len(desc) == 2 and isinstance(desc[1], tuple) else desc[1:]
            else:
                raise RuntimeError("incorrect unpickle plan: \"%s\"" % desc)
        def __call__(self, *args):
            if args:
                return self.fn(*args)
            return self.fn(*self.defargs)
        
    class ObjUnpickler(object):
        def __setstate__(self, sdict):
            for attr, builder in scheme.iteritems():
                try:
                    if attr in sdict:
                        sdict[attr] = builder(sdict[attr])
                    else:
                        sdict[attr] = builder()
                except:
                    logging.exception("can't deserialize attribute \"%s\" with builder %s", attr, builder)
                    raise
            setter = getattr(super(ObjUnpickler, self), "__setstate__", self.__dict__.update)
            setter(sdict)

        def __init__(self):
            for attr, builder in scheme.iteritems():
                setattr(self, attr, builder())
            getattr(super(ObjUnpickler, self), "__init__")()

    scheme = dict((attr, ObjBuilder(desc)) for attr, desc in kws.iteritems())
    return ObjUnpickler 


class PickableLock(Unpickable(_object = threading.Lock)):
    @classmethod
    def create(cls, o = None):
        if isinstance(o, cls):
            return o
        return cls()

    def __getattr__(self, attrname):
        return getattr(self._object, attrname)

    def __getstate__(self):
        return {}    


class PickableRLock(Unpickable(_object = threading.RLock)):
    @classmethod
    def create(cls, o = None):
        if isinstance(o, cls):
            return o
        return cls()

    def __getattr__(self, attrname):
        return getattr(self._object, attrname)

    def __getstate__(self):
        return {}    


class FuncRunner(object):
    """simple function running object with cPickle support
    WARNING: this class works only with pure function and nondynamic class methods"""
    
    def __init__(self, fn, args, kws):
        self.object = None
        if isinstance(fn, types.MethodType):
            self.object = fn.im_self or fn.im_class
            self.methName = fn.im_func.func_name
        else:
            self.fn = fn
        self.args = args
        self.kws = kws

    def __call__(self):
        fn = getattr(self.object, self.methName, None) if self.object else fn
        if callable(fn):
            fn(*self.args, **self.kws)
        else:
            logging.error("FuncRunner: object '%s' can't be executed", fn)


class SmartDecoder:
    enc_list = ["utf-8", "cp1251"]

    @classmethod
    def decode(cls, data=None):
        if isinstance(data, unicode) or data is None:
            return data
        for enc in cls.enc_list:
            try:
                _data = unicode(data, enc)
                return _data
            except:
                pass
        if not isinstance(data, unicode):
            logging.warning(" can't recognize user string %r", data)
        return data


