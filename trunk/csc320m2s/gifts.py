# Standard libraries
import wsgiref.handlers
import admin
import api

# AppEngine imports
from google.appengine.ext import webapp

# OpenSocial Gifts imports
import admin

# Map URLs to request handler class
application = webapp.WSGIApplication([('/admin', admin.AdminServer),
                                      ('/gifts', api.ApiServer),
                                      ('/giftTransactions', api.ApiServer)],
                                     debug=True)
# Fire it up!
wsgiref.handlers.CGIHandler().run(application)