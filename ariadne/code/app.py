"""define app entry point"""
import os
import logging
from starlette.applications import Starlette
from ariadne.asgi import GraphQL
from code.schema import schema
from lightning import channel
from bitcoin import client as btc_client

# TODO import and run environment tests

# end tests




app = Starlette(debug=True)

class Context:
    """class for passing context values"""

    def __init__(self):


        self.req = None
    
    def __call__(self, req):
        self.req = req
        return self


app.mount('/graphql', GraphQL(schema, debug=True, context_value=Context()))
