import webapp2
# from oauth2client.appengine import OAuth2Decorator
import csv
from models import FeedbackEntity
import logging
import cStringIO
import codecs
from dateutil import tz
from google.appengine.api import users
from oauth2client.appengine import OAuth2Decorator
from models import RoleEntity

# decorator = OAuth2Decorator(client_id='823696479254-mm9arog20nd675a176cvn2h7tnerom19.apps.googleusercontent.com',
#                             client_secret='lSvqusP2vp0P-0-e98p8QnNy',
#                             scope=['https://www.googleapis.com/auth/plus.profiles.read','https://www.googleapis.com/auth/userinfo.email'], approval_prompt='force')
class UnicodeWriter:
	"""
	A CSV writer which will write rows to CSV file "f",
	which is encoded in the given encoding.
	"""

	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		# Redirect output to a queue
		self.queue = cStringIO.StringIO()
		self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
		self.stream = f
		self.encoder = codecs.getincrementalencoder(encoding)()

	def writerow(self, row):
		self.writer.writerow([s.encode("utf-8") for s in row])
		# Fetch UTF-8 output from the queue ...
		data = self.queue.getvalue()
		data = data.decode("utf-8")
		# ... and reencode it into the target encoding
		data = self.encoder.encode(data)
		# write to the target stream
		self.stream.write(data)
		# empty queue
		self.queue.truncate(0)

	def writerows(self, rows):
		for row in rows:
			self.writerow(row)

decorator = OAuth2Decorator(client_id='547523974349-oalhr2lmk5fjrlrvqs52dq3uivq659bq.apps.googleusercontent.com',
                            client_secret='R_JVA4UDD2DZu1XoY3S9o4P-',
                            scope=['https://www.googleapis.com/auth/plus.profiles.read','https://www.googleapis.com/auth/userinfo.email'], approval_prompt='force')


class FeedbacksExportHandler(webapp2.RequestHandler):
	@decorator.oauth_aware
	def get(self):
		user = users.get_current_user()
		logging.info(user)
		user_email = user.email()
		role = RoleEntity.get_by_id('admin')
		members = role.members
		if not members:
			members = []
		if user_email not in members:
			logging.critical("Unauthorized request : " + user_email)
			self.response.write("Unauthorized request")
			return

		self.response.headers['Content-Type'] = 'application/csv;charset=UTF-8'
		self.response.headers['Content-disposition'] = 'attachment; filename=all_feedbacks.csv' 
		csv_writer = csv.writer(self.response.out, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		u_csv_writer = UnicodeWriter(self.response.out)
		qry = FeedbackEntity.query().order(-FeedbackEntity.date_created)
		fbs = qry.fetch()
		fms = []
		# csv_writer.writerow(['id','restaurant','entrie','quantity','flavor','deliverman','overall','timestamp'])
		u_csv_writer.writerow(['id','restaurant','entrie','quantity','flavor','deliverman','overall','timestamp','comment'])
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
			u_csv_writer.writerow([str(fb.key.id()),fb.restaurant or "",fb.entrie or "", fb.quantity or "", fb.flavor or "", fb.deliverman or "", fb.overall_rating or "", created_time_cst, fb.comment or ""])





app = webapp2.WSGIApplication([
	('/feedbacks/export', FeedbacksExportHandler),
	# (decorator.callback_path, decorator.callback_handler()),
], debug=True)