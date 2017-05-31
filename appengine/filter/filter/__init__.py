from google.appengine.ext.webapp import template
import datetime
from logging import info
import re

register = template.create_template_register()


@register.filter
def minsec(v):
	if v == v and isinstance(v,float):
		v = int(v)
		return "{0}:{1:02d}".format(v / 60, v % 60)


@register.filter
def gmt(v, a):
	if isinstance(v, datetime.date) or isinstance(v, datetime.datetime):
		return v + datetime.timedelta(seconds=60 * 60 * int(a))


@register.filter
def link(v):
	v = re.sub(r'(\w+://[\w/?.=&]+)', r'<a href="\1" >\1</a>', v)
	v = re.sub(r'(?<!/)item/(\d+)', r'<a href="/item/\1" >item/\1</a>', v)
	v = re.sub(r'(?<!/)sm(\d+)', r'<a href="//www.nicovideo.jp/watch/sm\1" >sm\1</a>', v)
	v = re.sub(r'(?<!/)@(\w+)', r'<a href="//twitter.com/\1" >@\1</a>', v)
	return v
