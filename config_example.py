from ldap3 import Server
import os
from dataclasses import dataclass

@dataclass
class Ldap:  # constants for LDAP
    _uri = ''
    _user = 'CN=,OU=,DC=DC='
    _passw = ''
    _server = Server(_uri)

    @property
    def uri(self):
        return self._uri
    
    @property
    def user(self):
        return self._user
    
    @property
    def passw(self):
        return self._passw
    
    @property
    def server(self):
        return self._server


@dataclass
class Rchat:  # constants for rocketchat
    _user = ''
    _passw = ''
    _url = ''
    _welcome_message_id = ''

    @property
    def user(self):
        return self._user
    
    @property
    def passw(self):
        return self._passw
    
    @property
    def url(self):
        return self._url
    
    @property
    def welcome_message_id(self):
        return self._welcome_message_id


LOG_FILE = '/var/log/RocketBot.log' if os.name == 'posix' else './RocketBot.log'  # log file path depending on OS

ldap = Ldap()
rchat = Rchat()
