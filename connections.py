from rocketchat_API.rocketchat import RocketChat
from ldap3 import Connection, SAFE_SYNC, AUTO_BIND_NO_TLS
from config import rchat, ldap


class Connections:
    def __init__(self):
        self.rocketchat = RocketChat(rchat.user, rchat.passw, server_url=rchat.url)
        self.ldap = Connection(ldap.server,
                      ldap.user,
                      ldap.passw,
                      read_only=True,
                      client_strategy=SAFE_SYNC,
                      auto_bind=AUTO_BIND_NO_TLS)
        
    def connect(self):
        return self.rocketchat, self.ldap
    
    def close(self):
        self.rocketchat.close()
        self.ldap.unbind()


rocket, ldap = Connections().connect()