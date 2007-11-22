
import copy,  os, pickle

from XSConsoleBases import *
from XSConsoleLang import *

class State:
    instance = None
    savePath = '/etc/xsconsole'
    saveLeafname = 'state.txt'
    thisVersion = 1
    
    def __init__(self):
        self.version = self.thisVersion
        self.authTimeoutSeconds = 5*60
        self.passwordChangeRequired = True
        self.modified = True
    
    @classmethod
    def SaveFilename(self):
        return self.savePath+'/'+self.saveLeafname
        
    @classmethod
    def Inst(cls):
        # Load the saved state if we can, otherwise create a default object
        if cls.instance is None:
            isFirstBoot = True
            try:
                if os.path.isfile(cls.SaveFilename()):
                    saveFile = open(cls.SaveFilename(), "r")
                    unpickler = pickle.Unpickler(saveFile)
                    cls.instance = unpickler.load()
                    saveFile.close()
                    isFirstBoot = False
                    if cls.instance.version != cls.instance.thisVersion:
                        # Version mismatch - don't use the state information
                        cls.instance = None
            except Exception, e:
                cls.instance = None
            
            if cls.instance is None:
                cls.instance = State()
            
            # Fill in pseudo-state
            cls.instance.isFirstBoot = isFirstBoot
            cls.instance.isRecoveryMode = os.path.isfile('/recovery')
                
            cls.instance.MakeSane()
            
        return cls.instance
        
    def AuthTimeoutSeconds(self):
        return self.authTimeoutSeconds
        
    def PasswordChangeRequired(self):
        return self.passwordChangeRequired
        
    def PasswordChangeRequiredSet(self, inValue):
        self.passwordChangeRequired = inValue
        self.modified = True
    
    def IsFirstBoot(self):
        return self.isFirstBoot
    
    def IsRecoveryMode(self):
        return self.isRecoveryMode
    
    def AuthTimeoutSecondsSet(self, inSeconds): # Don't call this directly - use Auth.TimeoutSecondsSet
        if inSeconds < 60:
            raise Exception("Cannot set a session timeout of less than one minute")
        if self.authTimeoutSeconds != inSeconds:
            self.authTimeoutSeconds = inSeconds
            self.modified = True
        
    def AuthTimeoutMinutes(self):
        return int((self.AuthTimeoutSeconds() + 30) / 60)
    
    def MakeSane(self):
        self.authTimeoutSeconds = int(self.authTimeoutSeconds)
        if self.authTimeoutSeconds < 60:
            AuthTimeoutSecondsSet(60)
    
    def SaveIfRequired(self):
        self.MakeSane()
        try:
            if not os.path.isdir(self.savePath):
                os.mkdir(self.savePath, 0700)
            
            saveFile = open(self.SaveFilename(), "w")
            pickler = pickle.Pickler(saveFile)
            self.modified = False # Modify before saving`
            pickler.dump(self)
            saveFile.close()
        except Exception, e:
            pass # Ignore failure

