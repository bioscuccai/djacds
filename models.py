from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django.core.urlresolvers import reverse

import os.path
# Create your models here.

GAME_CHOICES=(("cs16", "CS 1.6"), ("css", "CS:S"), ("csgo", "CS:GO"), ("tf2", "TF2"))
INFRACTION_CHOICES=(("wh","wh"),("sh","sh"),("ab","ab"),("o","o"))

def path_gameicon(instance, filename):
	ext=os.path.splitext(filename)[1]
	#return os.path.abspath(os.path.join(os.path.dirname(__file__), "static", "cds", "icon", instance.short_name+ext))
	return os.path.join(settings.MEDIA_ROOT,'cds/icon/',instance.short_name+ext)

class Game(models.Model):
	title=models.CharField(max_length=256)
	short_name=models.CharField(max_length=256)
	icon=models.FileField(upload_to=path_gameicon)

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('cds_demopergame', kwargs={'game': self.pk })

	def get_icon_static(self):
		return self.icon.path.replace(settings.MEDIA_ROOT, '')

class Cheat(models.Model):
	cheat_class=models.CharField(max_length=256, choices=INFRACTION_CHOICES)
	cheat_name=models.CharField(max_length=256)

	def __unicode__(self):
		return self.cheat_name

	def get_absolute_url(self):
		return reverse('cds_demopercheat', kwargs={'cheat': self.pk})

class Demo(models.Model):
	game=models.ForeignKey(Game, blank=False)
	title=models.CharField(max_length=256)
	description=models.TextField(max_length=4096)
	fileloc=models.CharField(max_length=2048)
	uploader=models.ForeignKey(User)
	infraction=models.ManyToManyField(Cheat)
	uploaded=models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('cds_detaildemo', kwargs={'pk': self.pk})

	def get_votes(self):
		y=Vote.objects.filter(demo=self).filter(vote=True).count()
		n=Vote.objects.filter(demo=self).filter(vote=False).count()
		return (y,n)

	def vote(self, user, chc):
		if self.has_user_voted(user):
			return False
		vote=Vote(demo=self, user=user, vote=chc)
		vote.save()
		return True

	def has_user_voted(self, user):
		return Vote.objects.filter(user=user).filter(demo=self).count()==1

	def yes_pct(self):
		y,n=self.get_votes()
		return int((y/float(y+n))*100) if y+n>0 else 0

	def no_pct(self):
		y,n=self.get_votes()
		return int((n/float(y+n))*100) if y+n>0 else 0

class DemoPic(models.Model):
	demo=models.ForeignKey(Demo)
	description=models.TextField(max_length=2048)
	fileloc=models.CharField(max_length=2048)

	def get_absolute_url(self):
		return reverse('cds_detaildemo', kwargs={'pk':self.demo.pk})

class Vote(models.Model):
	user=models.ForeignKey(User)
	demo=models.ForeignKey(Demo)
	vote=models.BooleanField()
	vote_time=models.DateTimeField(auto_now=True)

class DemoComment(models.Model):
	user=models.ForeignKey(User)
	reply=models.ForeignKey('self', related_name='+', blank=True, null=True)
	demo=models.ForeignKey(Demo)
	democomment=models.TextField(max_length=4096)
	time=models.DateTimeField(auto_now=True)
	def get_absolute_url(self):
		return reverse('cds_listdemocomments', kwargs={'demo': self.demo.pk})
	def __unicode__(self):
		return self.user.username +" "+str(self.time)