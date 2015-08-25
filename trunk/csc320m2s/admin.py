from db_model import Gift, GiftTransaction
from google.appengine.ext import webapp
from google.appengine.api import users

class Admin:
  """Initializes the list of gifts in the datastore."""
  def initGifts(self):
    """Deletes any existing gifts and add the default gifts."""
    for gift in Gift.all():
      gift.delete()
    GIFT_NAMES = ['a cashew nut',
                  'a peanut',
                  'a hazelnut',
                  'a red pistachio nut']
    for name in GIFT_NAMES:
      gift = Gift()
      gift.name = name
      gift.put()

  def initGiftTransactions(self):
    """Deletes any existing gift transactions."""
    for t in GiftTransaction.all():
      t.delete()

  def getGiftNames(self):
    names = []
    for gift in Gift.all():
      names.append(gift.name)
    
    return names

  def getGiftTransactions(self):
    giftTransactions = []
    for t in GiftTransaction.all():
      giftTransactions.append("sender: %s, reciever: %s, gift: %s" %
      (t.sender_id, t.receiver_id, t.gift.key()))
    return giftTransactions

class AdminServer(webapp.RequestHandler):
  """Handles requests to /admin URLs and delegates to the Admin class."""

#  def get(self):
#    """Handle GET requests."""
#    self.response.out.write('Welcome to the admin webapp')
  def get(self):
    """Ensure that the user is an admin."""
    if not users.GetCurrentUser():
      loginUrl = users.CreateLoginURL(self.request.uri)
      self.response.out.write('<a href="%s">Login</a>' % loginUrl)
      return

    if not users.IsCurrentUserAdmin():
      self.response.out.write('You must be an admin to view this page.')
      return

    self._handleRequest()
   
  def _handleRequest(self):
    """Invokes methods from the Admin class based on the 'action' parameter"""
    admin = Admin()
    action = self.request.get('action')
    if action == 'init':
      admin.initGifts()
      admin.initGiftTransactions()
      msg = "Gifts have been initialized, gift transactions have been cleared."
      self.response.out.write(msg)
    elif action == 'list':
      self.response.out.write("Gifts = %s" % admin.getGiftNames())
      self.response.out.write("<br>")
      self.response.out.write("Gift Transactions = %s" % admin.getGiftTransactions())
    else:
      html = []
      html.append('<a href="/admin?action=init">Initialize datastore</a><br>')
      html.append('<a href="/admin?action=list">List all data in datastore</a>')
      self.response.out.write(''.join(html))