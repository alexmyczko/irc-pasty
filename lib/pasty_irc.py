from irc.client import Reactor, ServerConnectionError

class IRC():
    def __init__(self, **kwargs):
        self.server = kwargs.get('server')
        self.port = int(kwargs.get('port'))
        self.username = kwargs.get('username')

        self.irc_reactor = Reactor()
    '''
        try:
            self.irc_client = self.irc_reactor.server().connect(self.server, self.port, self.username)
        except ic.ServerConnectionError:
            print('IRC client connection error')
            print(sys.exc_info()[1])

    def __del__(self):
        self.irc_client.quit()
    '''
    def connect(self):
        try:
            self.irc_client = self.irc_reactor.server().connect(self.server, self.port, self.username)
        except ServerConnectionError:
            print('IRC client connection error')
            # print(sys.exc_info()[1])

    def disconnect(self):
        try:
            self.irc_client.quit()
        except:
            print('Failed to disconnect from IRC server')

    def send(self, channel, msg):
        self.connect()
        try:
            self.irc_client.privmsg(channel, msg)
        except:
            print('Failed to send message to IRC server')
        self.disconnect()
