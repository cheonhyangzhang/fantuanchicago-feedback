from google.appengine.ext import ndb
class BaseEntity(ndb.Model):
	"""
  	Base model for various types of models
	"""
	date_created = ndb.DateTimeProperty(auto_now_add=True)
	date_updated = ndb.DateTimeProperty(auto_now=True)
	skip_properties = ['date_updated', 'date_created']

	def toDict(self):
		logging.debug("toDict")
		logging.debug(self.to_dict())
		idict = self.to_dict()
		idict['id'] = str(self.key.id())
		return idict

class RoleEntity(BaseEntity):
	name = ndb.StringProperty()
	description = ndb.StringProperty()
	members = ndb.StringProperty(repeated=True)

class RestaurantsEntity(BaseEntity):
	location = ndb.StringProperty()
	restaurants = ndb.TextProperty()

class FeedbackEntity(BaseEntity):
	restaurant = ndb.StringProperty() 
	useremail = ndb.StringProperty() 
	entrie = ndb.StringProperty() 
	quantity = ndb.StringProperty() 
	flavor = ndb.StringProperty() 
	deliverman = ndb.StringProperty() 
	overall_rating = ndb.StringProperty() 
	comment = ndb.StringProperty() 