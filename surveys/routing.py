# School Votes / Community votes
#
# Author: Luca Cotter
#
# Date: August 2018
#
# (c) 2018 Copyright, Luca Cotter. All rights reserved.
#
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import votes.routing

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
                    URLRouter(votes.routing.websocket_urlpatterns)),
})
