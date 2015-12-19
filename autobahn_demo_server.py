from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.python import log
from twisted.internet import reactor

import sys
import json
import time


# ClientCountResource deals with the synchronous JSONJ ajax call.
class ClientCountResource(Resource):

    def __init__(self, client_tracker):
        self.client_tracker = client_tracker

    def render_GET(self, request):
        # Need to return as a callback.
        callback = request.args['callback'][0]
        return_payload = {'time' : time.ctime(),
                          'client_count' : len(self.client_tracker.clients)}
        return "%s(%s)" % (callback, json.dumps(return_payload))

# BroadcastServerProtocol deals with the async websocket client connection.
class BroadcastServerProtocol(WebSocketServerProtocol):

    def onMessage(self, payload, isBinary):
        if not isBinary:
            in_data = json.loads(payload.decode('utf8'))
            in_message = in_data['data']
            return_message = 'Message from %s : %s' % (self.peer, in_message)
            return_payload = json.dumps({'type': 'chat', 'data' : return_message})
            self.factory.broadcast(return_payload)

    def onOpen(self):
        log.msg('Connection open on %s' % self.peer)
        self.factory.register(self)

    def connectionLost(self, reason):
        log.msg('Connection lost on %s' % self.peer)
        WebSocketServerProtocol.connectionLost(self, reason)
        self.factory.unregister(self)

# BroadcastServerFactory is the central websocket server side component shared between connections.
class BroadcastServerFactory(WebSocketServerFactory):

    def __init__(self, client_tracker, debug=False, debugCodePaths=False):
        WebSocketServerFactory.__init__(self, debug=debug, debugCodePaths=debugCodePaths)
        self.client_tracker = client_tracker

    def register(self, client):
        self.client_tracker.register(client)

    def unregister(self, client):
        self.client_tracker.unregister(client)

    def broadcast(self, msg):
        for c in self.client_tracker.clients:
            c.sendMessage(msg.encode('utf8'), isBinary = False)

# Helper to keep track of connections, accessed by the sync and async methods.
class ClientTracker:
    def __init__(self):
        self.clients = []

    def register(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def unregister(self, client):
        if client in self.clients:
            self.clients.remove(client)

if __name__ == '__main__':

    log.startLogging(sys.stdout)
    client_tracker = ClientTracker()

    # Simple file server, serving files from the html directory.
    resource = File(r'.\html')
    factory = Site(resource)
    reactor.listenTCP(9000, factory)

    # App server, handles synchronous ajax calls.
    root = Resource()
    root.putChild("get_client_count", ClientCountResource(client_tracker))
    factory = Site(root)
    reactor.listenTCP(9001, factory)

    # Web socket server, handles asynchronous web socket calls.
    factory = BroadcastServerFactory(client_tracker)
    factory.protocol = BroadcastServerProtocol
    reactor.listenTCP(9002, factory)

    reactor.run()
