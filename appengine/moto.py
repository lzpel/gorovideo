# coding=utf-8
import os, json, urllib, time, datetime, math, re
from logging import info
from google.appengine.ext.webapp import template, blobstore_handlers, RequestHandler
from google.appengine.api import app_identity, mail
from google.appengine.ext import blobstore, ndb


def getenviron(key):
	return os.environ.get(key)


def addfilter(file):
	template.register_template_library(file)


def getuploadurl(next, maxbytes=None):
	return blobstore.create_upload_url(next, max_bytes_per_blob=maxbytes)


def sendmail(data):
	data["sender"] = u"anything@{0}.appspotmail.com".format(app_identity.get_application_id())
	mail.send_mail(sender=data["sender"], to=data["to"], subject=data["subject"], body=data["body"])


def getunicode(t):
	for i in ["utf-8", "ascii", "shift_jis", "euc-jp"]:
		try:
			return unicode(t, i)
		except:
			pass
	return t


def get_multi_modify(n):
	r = ndb.get_multi(n)
	while n:
		n.pop()
	for i in r:
		n.append(i.key)


class base(ndb.Model):
	# default未使用低容量
	# 他から計算できる情報は保存しない。コメントマイリス数
	# 時刻
	bone = ndb.DateTimeProperty(auto_now_add=True)
	last = ndb.DateTimeProperty(auto_now=True)
	# 分類
	anal = ndb.StringProperty(default=u"base")
	# 関係性
	kslf = ndb.ComputedProperty(lambda s: s.key)
	kusr = ndb.KeyProperty()  # 作者
	kint = ndb.KeyProperty()  # 米等の対象物
	kner = ndb.KeyProperty(repeated=True)
	kfar = ndb.KeyProperty(repeated=True)
	# 基本
	name = ndb.StringProperty(validator=lambda p, v: v[:100])
	text = ndb.TextProperty(validator=lambda p, v: v[:200])
	mail = ndb.StringProperty()
	word = ndb.StringProperty()
	attr = ndb.StringProperty(repeated=True)
	gram = ndb.StringProperty(repeated=True)
	blob = ndb.BlobKeyProperty(repeated=True)
	icon = ndb.TextProperty()  # サムネイル
	head = ndb.TextProperty()
	view = ndb.IntegerProperty()
	coin = ndb.IntegerProperty()
	size = ndb.IntegerProperty()  # ファイルの数
	qone = ndb.IntegerProperty(repeated=True)
	qtwo = ndb.FloatProperty(repeated=True)
	qual = ndb.ComputedProperty(lambda s: float(sum(s.qtwo)))
	tpos = ndb.FloatProperty()
	tlen = ndb.FloatProperty()

	# 過去
	# authdate = ndb.FloatProperty(repeated=True)
	# authterm = ndb.ComputedProperty(lambda s: sum(s.authdate))
	# viewdate = ndb.IntegerProperty(repeated=True)
	# viewterm = ndb.ComputedProperty(lambda s: sum(s.viewdate))
	# flt0 = ndb.FloatProperty()
	# flt1 = ndb.FloatProperty()
	# flt2 = ndb.FloatProperty()
	# flt3 = ndb.FloatProperty()
	# int0 = ndb.IntegerProperty()
	# int1 = ndb.IntegerProperty()
	# int2 = ndb.IntegerProperty()
	# int3 = ndb.IntegerProperty()
	# khas = ndb.KeyProperty(repeated=True)  # 同階層友好

	@classmethod
	def getbyid(c, i, m=True):
		k = ndb.Key(c, int(i))
		if m: k = k.get()
		return k

	@classmethod
	def _pre_delete_hook(c, k):
		s = k.get()
		# delete blob
		blobstore.delete(s.blob)
		# delete kusr,kint
		ndb.delete_multi(base.query(ndb.OR(base.kusr == s.key, base.kint == s.key)).fetch(keys_only=True))

	def _pre_put_hook(s):
		c = s.__class__
		s.gram = c.getgram(s.getgramtext(), False)

	def getgramtext(s):
		# please custumize
		return (unicode().join(s.attr) + (getunicode(s.name) or unicode()) + (getunicode(s.text) or unicode()))[:200]

	@classmethod
	def getgram(c, txt, isquery):
		# 下処理
		txt = getunicode(txt)
		txt = txt.lower()
		# 分割
		num = 0
		one = []
		two = []
		while num < len(txt):
			one.append(txt[num:num + 1])
			two.append(txt[num:num + 2])
			num += 1
		# 削除
		if two:
			del two[-1]
		if isquery and len(one) > 2:
			del one[1:-1]
		return one + two

	@classmethod
	def getgramfilter(c, t):
		return [(c.gram == i) for i in c.getgram(t, True)]

	def putpoint(s, v):
		def rankadd(l, v):
			size = 12
			if len(l) != size:
				del l[:]
				l.extend(0 for i in xrange(size))
			num = (datetime.datetime.now() - datetime.datetime.min).seconds / 3600.0 % size
			if num % 1 <0.5:
				l[int(num)]=0#初期化
			else:
				l[int(num)]+=v

		u = s.kusr.get()
		if v and u.key != v.key:
			rankadd(s.qone, 1)
			rankadd(u.qone, 1)
			rankadd(s.qtwo, math.sqrt(sum(v.qone)))
			u.put()
		s.put()  # 必ずput


class data:
	def __getattr__(s, k):
		return None


# https://cloud.google.com/appengine/docs/standard/python/blobstore/
#
class blobhandler(RequestHandler):
	def get(s, blob):
		s.response.headers.add_header('X-AppEngine-BlobKey', blob)
		if "Range" in s.request.headers:
			r = re.findall(r"\d+", s.request.headers['Range'])
			r0 = int(r[0])
			r1 = int(r[1]) if len(r) >= 2 else r0 + 1048576
			s.response.headers.add_header('X-AppEngine-BlobRange', "bytes={0}-{1}".format(r0, r1))


class workhandler(blobstore_handlers.BlobstoreUploadHandler, RequestHandler):
	def cget(s, k):
		return s.request.cookies.get(k, '')

	def cset(s, k, v, d=100):
		if not v:
			d = -d
		s.response.headers.add_header('Set-Cookie', '{0}={1}; path=/; max-age={2}'.format(k, v, 86400 * d))

	def kget(s, m=True):
		try:
			x = ndb.Key(urlsafe=s.cget('urlsafe'))
			if m: x = x.get()
			return x
		except:
			return None

	def kset(s, k):
		s.cset('urlsafe', k.urlsafe() if k else '')

	def url(s, pattern):
		s.o.url = s.request.url
		s.o.path = s.request.path
		url = s.o.path.split("/")
		pat = pattern.split("/")
		if len(url) != len(pat):
			return
		for u, p in zip(url, pat):
			if p and p[0] == "#":
				setattr(s.i, p[1:], urllib.unquote(u))
			elif p == u:
				pass
			else:
				return
		return True

	def blob(s, name=None):
		return s.get_uploads(name)

	def work(s, a, o):
		pass  # doing

	def post(s):
		s.get()

	def get(s):
		# 入力
		s.i = data()
		for k in s.request.arguments():
			setattr(s.i, k, s.request.get(k))
		if all(i.size for i in s.get_uploads()):
			s.i.upload = [i.key() for i in s.get_uploads()]
		else:
			blobstore.delete([i.key for i in s.get_uploads()])

		# 処理
		s.o = data()
		s.work(s.i, s.o)
		# 出力
		if s.o.redirect:
			s.redirect(str(s.o.redirect))
		if s.o.template:
			tmp = os.path.join(os.path.dirname(__file__), s.o.template)
			if os.path.exists(tmp):
				s.response.out.write(template.render(tmp, vars(s.o)))
		else:
			def jsondefault(o):
				if isinstance(o, ndb.Model):
					r = o.to_dict()
					r["key"] = o.key
					return r
				if isinstance(o, ndb.Key):
					return {"id": o.id(), "kind": o.kind(), "urlsafe": o.urlsafe()}
				if isinstance(o, blobstore.BlobKey):
					return str(o)
				return None

			s.response.headers['Content-Type'] = 'application/json'
			s.response.out.write(json.dumps(vars(s.o), default=jsondefault, indent=4))
