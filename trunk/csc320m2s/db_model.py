from google.appengine.ext import db

class Gift(db.Model):
  name = db.StringProperty()

class GiftTransaction(db.Model):
  sender_id = db.StringProperty()
  receiver_id = db.StringProperty()
  gift = db.ReferenceProperty(Gift)