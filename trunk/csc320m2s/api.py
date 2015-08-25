# App Engine imports
from google.appengine.ext import webapp

# Third party imports
import json
import oauth #also crypto

# OpenSocial Gifts imports
from db_model import Gift, GiftTransaction

#crypto  imports
import base64
import hashlib
import urllib
from Crypto.PublicKey import RSA
from Crypto.Util import number

class ApiServer(webapp.RequestHandler):
  """Handles requests to /gifts URLs and reponds with JSON strings."""
  def get(self):
    """Call the appropriate handler based on the path of the HTTP request."""
    #self.response.out.write(self.request.path)
    if not self._isValidSignature():
      self.response.out.write(json.write({}))
      return
      
    if self.request.path.startswith('/gifts'):
      self._handleGifts()
    elif self.request.path.startswith('/giftTransactions'):
      self._handleGiftTransactions()
      
  def post(self):
    """Store a new gift transaction in the datastore based on the POST data."""
    if not self._isValidSignature():
      return
      
    giftTransaction = GiftTransaction()
    giftTransaction.sender_id = self.request.get('sender_id')
    giftTransaction.receiver_id = self.request.get('receiver_id')
    giftTransaction.gift = Gift.get(self.request.get('gift_key')).key()
    giftTransaction.put()
    
  def _handleGifts(self):
    gifts = []
    for gift in Gift.all():
      item = {'key' : str(gift.key()),
              'name' : gift.name }
      gifts.append(item)
    self.response.out.write(json.write(gifts))
    #self.response.out.write('Welcome to the admin web interface')

  def _handleGiftTransactions(self):
    '''return a list of GiftTransactions as JSON'''
#    giftTransactions=[]
#    for tran in GiftTransaction.all():
#      item={'sender_id' : tran.sender_id,
#            'receiver_id' : tran.receiver_id,
#            'gift_name' : tran.gift.name }
#      giftTransactions.append(item)
#    self.response.out.write(json.write(giftTransactions))
    self._returnGiftTransactions()
    
  def _returnGiftTransactions(self):
    """Return the list of transactions specified by the URL query parameters."""
    sender_id = self.request.get("sender_id")
    receiver_id = self.request.get("receiver_id")
    giftTransactions = self._getGiftTransactions(sender_id, receiver_id)

    results = []
    for giftTransaction in giftTransactions:
      item = { 'sender_id' : giftTransaction.sender_id,
               'receiver_id' : giftTransaction.receiver_id,
               'gift_name' : giftTransaction.gift.name }
      results.append(item)
    self.response.out.write(json.write(results))

  def _getGiftTransactions(self, sender_id, receiver_id):
    results = []
    if sender_id:
      results = GiftTransaction.gql('WHERE sender_id=:sender_id', 
                                sender_id=sender_id)
    elif receiver_id:
      results = GiftTransaction.gql('WHERE receiver_id=:receiver_id',
                                receiver_id=receiver_id)
    else:
      results = GiftTransaction.all()

    return results;
    
  def _isValidSignature(self):
    # Construct a RSA.pubkey object
    exponent = 65537
    #DO NOT INDENT TRAILING LINES OF THE STRING - LEAVE THEM ON THE LEFT BORDER
    public_key_str = """0x\
00b1e057678343866db89d7dec2518\
99261bf2f5e0d95f5d868f81d600c9\
a101c9e6da20606290228308551ed3\
acf9921421dcd01ef1de35dd3275cd\
4983c7be0be325ce8dfc3af6860f7a\
b0bf32742cd9fb2fcd1cd1756bbc40\
0b743f73acefb45d26694caf4f26b9\
765b9f65665245524de957e8c547c3\
58781fdfb68ec056d1"""
    public_key_long = long(public_key_str, 16)
    public_key = RSA.construct((public_key_long, exponent))
        
    # Rebuild the message hash locally
    oauth_request = oauth.OAuthRequest(http_method=self.request.method, 
                                       http_url=self.request.url, 
                                       parameters=self.request.params.mixed())
    message = '&'.join((oauth.escape(oauth_request.get_normalized_http_method()),
                        oauth.escape(oauth_request.get_normalized_http_url()),
                        oauth.escape(oauth_request.get_normalized_parameters()),))
    local_hash = hashlib.sha1(message).digest()

    # Apply the public key to the signature from the remote host
    sig = base64.decodestring(urllib.unquote(self.request.params.mixed()["oauth_signature"]))
    remote_hash = public_key.encrypt(sig, '')[0][-20:]
    
    # Verify that the locally-built value matches the value from the remote server.
    if local_hash==remote_hash:
      return True
    else:
      return False