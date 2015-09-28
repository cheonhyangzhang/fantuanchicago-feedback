"""Hello World API implemented using Google Cloud Endpoints.

Defined here are the ProtoRPC messages needed to define Schemas for methods
as well as those methods defined in an API.
"""


import endpoints
import logging
import json
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from models import RestaurantsEntity
from models import FeedbackEntity
from models import RoleEntity
from dateutil import tz

ADMINS = ['fantuanchicago@gmail.com','cenhiangapply@gmail.com']

class Greeting(messages.Message):
  message = messages.StringField(1)

class CheckRoleMessage(messages.Message):
  role = messages.StringField(1)
class RoleMessage(messages.Message):
  name = messages.StringField(1)
  description = messages.StringField(2)
  members = messages.StringField(3, repeated=True)

class RoleNameMessage(messages.Message):
	name = messages.StringField(1)

class GreetingCollection(messages.Message):
  items = messages.MessageField(Greeting, 1, repeated=True)

class RestaurantMessage(messages.Message):
	name = messages.StringField(1)
	entries = messages.StringField(2, repeated = True)
class RestaurantAddMessage(messages.Message):
	location = messages.StringField(1)
	name = messages.StringField(2)
	entries = messages.StringField(3, repeated = True)

class RestaurantsMessage(messages.Message):
	restaurants = messages.MessageField(RestaurantMessage, 1, repeated=True)
	location = messages.StringField(2)
class LocationMessage(messages.Message):
	location = messages.StringField(1)
class FeedbackMessage(messages.Message):
	restaurant = messages.StringField(1)
	entrie = messages.StringField(2)
	quantity = messages.StringField(3)
	flavor = messages.StringField(4)
	deliverman = messages.StringField(5)
	overall_rating = messages.StringField(6)
	comment = messages.StringField(7)
	useremail = messages.StringField(8)
class FeedbackWithIdMessage(messages.Message):
	restaurant = messages.StringField(1)
	entrie = messages.StringField(2)
	quantity = messages.StringField(3)
	flavor = messages.StringField(4)
	deliverman = messages.StringField(5)
	overall_rating = messages.StringField(6)
	id = messages.StringField(7)
	date = messages.StringField(8)
	comment = messages.StringField(9)
	useremail = messages.StringField(10)
class FeedbackCollectionMessage(messages.Message):
	feedbacks = messages.MessageField(FeedbackWithIdMessage, 1, repeated = True)
class BooleanMessage(messages.Message):
	resp = messages.StringField(1)

STORED_GREETINGS = GreetingCollection(items=[
    Greeting(message='hello world!'),
    Greeting(message='goodbye world!'),
])

def check_admin(endpoints):
	logging.info("check_admin")
	logging.info(endpoints)
	user = endpoints.get_current_user()
	logging.info("User: " + str(user))
	if user is None:
		message = 'Unauthorized request: No account found'
		logging.debug("check_auth: " + str(message))
		raise endpoints.UnauthorizedException(message)
	else:
		try:
			user_email = user.email()
			logging.info(user_email)
			# if user_email == 'fantuanchicago@gmail.com':
			if user_email in ADMINS:
				logging.debug("check_auth: allowed by admin account")
				return
			else:
				logging.debug("check_auth: not allowed not a admin account")
				message = 'Unauthorized request: Not a admin account :' + str(user_email)
				raise endpoints.UnauthorizedException(message)
		except:
			logging.debug("check_auth: exception happens when checking the auth")
			message = 'Unauthorized request: Not a admin account :' + str(user_email)
			raise endpoints.UnauthorizedException(message)

@endpoints.api(name='fantuan', version='v1', allowed_client_ids=['547523974349-oalhr2lmk5fjrlrvqs52dq3uivq659bq.apps.googleusercontent.com',endpoints.API_EXPLORER_CLIENT_ID])
class FantuanFeedbackAPI(remote.Service):
	"""FantuanChicago Feedback"""
	@endpoints.method(RoleMessage, RoleMessage,
	                path='roles', http_method='POST',
	                name='roles.patch')
	def roles_patch(self, request):
		check_admin(endpoints)	
		role = RoleEntity(id=request.name, name = request.name, description = request.description, members = request.members)
		role.put()
		return RoleMessage(
			name = role.name,
			description = role.description,
			members = role.members
			)
	@endpoints.method(RoleNameMessage, RoleMessage,
	                path='roles', http_method='GET',
	                name='roles.get')
	def roles_get(self, request):
		check_admin(endpoints)	
		role = RoleEntity.get_by_id(request.name)
		return RoleMessage(
			name = role.name,
			description = role.description,
			members = role.members
			)

	@endpoints.method(CheckRoleMessage, BooleanMessage,
	                path='roles/check', http_method='GET',
	                name='roles.check')
	def roles_check(self, request):
		user = endpoints.get_current_user()
		user_email = user.email()
		role = RoleEntity.get_by_id(request.role)
		resp = 'false'
		if user_email in role.members:
			resp = 'true'
		return BooleanMessage(
			resp = resp
			)
	@endpoints.method(RestaurantAddMessage, RestaurantsMessage,
	                path='restaurant', http_method='POST',
	                name='restaurants.add')
	def restaurants_add(self, request):
		check_admin(endpoints)	
		re = RestaurantsEntity.get_by_id(request.location)
		rest_dict = json.loads(re.restaurants)
		rest_dict.append({'name':request.name, 'entries':request.entries});
		re.restaurants = json.dumps(rest_dict)
		re.put()
		rm_list = []
		for rest in rest_dict:
			# logging.info(rest)
			# logging.info(rest['name'])
			rm = RestaurantMessage(name = rest['name'], entries = rest['entries'])
			rm_list.append(rm)

		return RestaurantsMessage(location = re.location, restaurants = rm_list)

	@endpoints.method(RestaurantsMessage, RestaurantsMessage,
	                path='restaurants', http_method='POST',
	                name='restaurants.patch')
	def restaurants_patch(self, request):
		check_admin(endpoints)	
		rest_list = []
		for rest in request.restaurants:
			rest_dict = {}
			rest_dict['name'] = rest.name
			rest_dict['entries'] = rest.entries
			rest_list.append(rest_dict)
		re = RestaurantsEntity(id=request.location,location = request.location, restaurants= json.dumps(rest_list))
		re.put()
		return request

	@endpoints.method(LocationMessage, RestaurantsMessage,
	                path='restaurants', http_method='GET',
	                name='restaurants.get')
	def restaurants_get(self, request):
		re = RestaurantsEntity.get_by_id(request.location)
		rest_dict = json.loads(re.restaurants)
		# logging.info(rest_dict)	
		rm_list = []
		for rest in rest_dict:
			# logging.info(rest)
			# logging.info(rest['name'])
			rm = RestaurantMessage(name = rest['name'], entries = rest['entries'])
			rm_list.append(rm)

		return RestaurantsMessage(location = re.location, restaurants = rm_list)

	@endpoints.method(FeedbackMessage, FeedbackWithIdMessage,
	                path='feedback', http_method='POST',
	                name='feedback.insert')
	def feedback_insert(self, request):
		fm = FeedbackEntity(
			restaurant = request.restaurant,  
			entrie = request.entrie,  
			quantity = request.quantity, 
			flavor = request.flavor,  
			deliverman = request.deliverman,
			overall_rating = request.overall_rating,
			comment = request.comment,
			useremail = request.useremail
		)	
		fm.put()
		return FeedbackWithIdMessage(
			id = str(fm.key.id()),  
			restaurant = fm.restaurant,  
			entrie = fm.entrie,  
			quantity = fm.quantity, 
			flavor = fm.flavor,  
			deliverman = fm.deliverman,
			overall_rating = fm.overall_rating,
			comment = fm.comment,
			useremail = fm.useremail
			)

	ID_RESOURCE = endpoints.ResourceContainer(
      message_types.VoidMessage,
      id=messages.IntegerField(1, variant=messages.Variant.INT32))
	@endpoints.method(ID_RESOURCE, FeedbackWithIdMessage,
	                path='feedback', http_method='GET',
	                name='feedback.get')
	def feedback_get(self, request):
		fm = FeedbackEntity.get_by_id(request.id)
		return FeedbackWithIdMessage(
			id = str(fm.key.id()),  
			restaurant = fm.restaurant,  
			entrie = fm.entrie,  
			quantity = fm.quantity, 
			flavor = fm.flavor,  
			deliverman = fm.deliverman,
			overall_rating = fm.overall_rating,
			comment = fm.comment,
			date = fm.date_created.strftime('%Y-%m-%d'),
			useremail = fm.useremail
			)

	@endpoints.method(message_types.VoidMessage, FeedbackCollectionMessage,
	                path='feedbacks', http_method='GET',
	                name='feedback.list')
	def feedback_list(self, request):
		check_admin(endpoints)
		qry = FeedbackEntity.query().order(-FeedbackEntity.date_created)
		fbs = qry.fetch()
		fms = []
		for fb in fbs:
			created_time = fb.date_created
			if created_time:
				utc_zone = tz.gettz('UTC')
				cst_zone = tz.gettz('America/Chicago')
				created_time = created_time.replace(tzinfo=utc_zone)
				created_time_cst = created_time.astimezone(cst_zone)
				created_time_cst = created_time_cst.strftime('%Y-%m-%d')
			else:
				created_time_cst = ""
			fm = FeedbackWithIdMessage(
			id = str(fb.key.id()),  
			restaurant = fb.restaurant,  
			entrie = fb.entrie,  
			quantity = fb.quantity, 
			flavor = fb.flavor,  
			deliverman = fb.deliverman,
			comment = fb.comment,
			overall_rating = fb.overall_rating,
			date = created_time_cst,
			useremail = fb.useremail
			)
			fms.append(fm)
		return FeedbackCollectionMessage(feedbacks = fms)

  # @endpoints.method(message_types.VoidMessage, GreetingCollection,
  #                   path='hellogreeting', http_method='GET',
  #                   name='greetings.listGreeting')
  # def greetings_list(self, unused_request):
  #   return STORED_GREETINGS

  # ID_RESOURCE = endpoints.ResourceContainer(
  #     message_types.VoidMessage,
  #     id=messages.IntegerField(1, variant=messages.Variant.INT32))

  # @endpoints.method(ID_RESOURCE, Greeting,
  #                   path='hellogreeting/{id}', http_method='GET',
  #                   name='greetings.getGreeting')
  # def greeting_get(self, request):
  #   try:
  #     return STORED_GREETINGS.items[request.id]
  #   except (IndexError, TypeError):
  #     raise endpoints.NotFoundException('Greeting %s not found.' %
  #                                       (request.id,))

APPLICATION = endpoints.api_server([FantuanFeedbackAPI])