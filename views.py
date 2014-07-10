from django.shortcuts import render, redirect
from PIL import Image
import os.path

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, DetailView, View, TemplateView, UpdateView
from django.shortcuts import get_object_or_404
from django.forms.models import modelform_factory
from django.forms import Textarea
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .models import Game, Demo, DemoComment, DemoPic, Vote, Cheat
from .forms import DemoImageForm, DemoDemoForm, GameIconForm

from braces.views import CsrfExemptMixin, OrderableListMixin, LoginRequiredMixin
# Create your views here.

THUMB_W=200
THUMB_H=200
#IMAGE_PATH="/home/akos/pycucc/dj1/dj1/static/cds/"
IMAGE_PATH=os.path.join(os.path.dirname(__file__), "static", "cds")

def makethumb(fn):
	i=Image.open(os.path.join(IMAGE_PATH,"image/",fn))
	(w,h)=i.size
	ratio=0.5
	if w>=h:
		ratio=float(THUMB_W)/float(w)
	else:
		ratio=float(THUMB_H)/float(h)
	i.thumbnail((int(w*ratio), int(h*ratio)), Image.ANTIALIAS)
	#i.save(IMAGE_PATH+"thumb/"+fn)
	i.save(os.path.join(IMAGE_PATH, "thumb", fn))

def handle_uploaded_file(f, to):
	with open(to, 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

##cheat
class CheatCreate(CsrfExemptMixin, LoginRequiredMixin, CreateView):
	model=Cheat
##game
class GameCreate(CsrfExemptMixin, LoginRequiredMixin, CreateView):
	model=Game

class GameList(OrderableListMixin,ListView):
	model=Game
	context_object_name="games"
	orderable_columns=(u"title", u"short_name")
	orderable_columns_default=u"title"

class GameDetail(DetailView):
	model=Game


##demo
class DemoCreate(CsrfExemptMixin, LoginRequiredMixin, CreateView):
	model=Demo
	fields=["game", "title", "description", "infraction"]

	def form_valid(self, form):
		form.instance.uploader=self.request.user

		#demo_ids=[int(x) for x in form.cleaned_data['infraction']]
		#cheats=Cheat.objects.filter(pk__in=demo_ids)
		#form.instance.infractions=form.cleaned_data['infraction']
		#form.instance.save()
		return super(DemoCreate, self).form_valid(form)


class DemoList(OrderableListMixin, ListView):
	model=Demo
	context_object_name="demos"
	orderable_columns=(u"title", u"infraction", u"game.title", u"uploaded")
	orderable_columns_default=u"uploaded"

class DemoDetail(DetailView):
	model=Demo
	def get_context_data(self, **kwargs):
		context=super(DetailView, self).get_context_data(**kwargs)
		y,n=context['object'].get_votes()
		context['total']=y+n
		if y+n>0:
			context['y_pct']=int((y/float(y+n))*100)
			context['n_pct']=100-context['y_pct']
		context['vote_yes']=y
		context['vote_no']=n
		context['can_vote']=True if self.request.user.is_authenticated() and not context['object'].has_user_voted(self.request.user) else False
		context['comment_form']=modelform_factory(DemoComment, fields=DemoCommentCreate.fields)
		context['comment_form'].widgets={'democomment':Textarea(attrs={"rows":3})}
		context['image_form']=DemoImageForm()
		return context

class DemoUpdate(CsrfExemptMixin, LoginRequiredMixin, UpdateView):
	model=Demo
	fields=DemoCreate.fields
	def form_valid(self, form):
		if form.instance.uploader != self.request.user:
			raise Http404
		return super(DemoUpdate, self).form_valid(form)
##comment
class DemoCommentCreate(CsrfExemptMixin, LoginRequiredMixin, CreateView):
	model=DemoComment
	fields=["democomment"]

	def get_context_data(self, **kwargs):
		context=super(DemoCommentCreate, self).get_context_data(**kwargs)
		context['demo_id']=self.kwargs['demop']
		return context

	def form_valid(self, form):
		form.instance.demo=get_object_or_404(Demo, pk=self.kwargs['demop'])
		form.instance.user=self.request.user
		rt=self.request.POST.get('reply_to', '')
		if rt.isdigit():
			reply_key=int(rt)
			if DemoComment.objects.filter(pk=reply_key).count() == 1:
				form.instance.reply=DemoComment.objects.get(pk=reply_key)
		return super(DemoCommentCreate, self).form_valid(form)

class DemoCommentList(ListView):
	model=DemoComment
	context_object_name="democomments"
	def get_queryset(self):
		demo=get_object_or_404(Demo, pk=self.kwargs['demo'])
		return DemoComment.objects.filter(demo=demo)

##filter
class DemoPerGame(ListView):
	model=Demo
	context_object_name="demos"
	def get_queryset(self):
		game=get_object_or_404(Game, pk=self.kwargs['game'])
		return Demo.objects.filter(game=game)

class DemoPerCheat(ListView):
	model=Demo
	context_object_name="demos"
	def get_queryset(self):
		cheat=get_object_or_404(Cheat, pk=self.kwargs['cheat'])
		return Demo.objects.filter(infraction__in=[cheat])

class DemoPicView(CsrfExemptMixin, View):
	def get_pictures(self):
		demo=get_object_or_404(Demo, pk=self.kwargs["demo"])
		return DemoPic.objects.filter(demo=demo)

	def post(self, request, *args, **kwargs):
		if request.method=="POST":
			form=DemoImageForm(request.POST, request.FILES)
			if form.is_valid():
				ext=os.path.splitext(request.FILES['imagefile'].name)[1]
				if ext != ".jpg" and ext != ".png":
					raise Http404
				demo=get_object_or_404(Demo, pk=self.kwargs["demo"])
				if demo.uploader!=request.user:
					raise Http404
				pic=DemoPic(demo=demo,description=form.cleaned_data["description"],fileloc="")
				pic.save()
				pic.fileloc=str(pic.pk)+ext
				pic.save()
				#handle_uploaded_file(request.FILES['imagefile'], IMAGE_PATH+"image/"+str(pic.pk)+ext)
				handle_uploaded_file(request.FILES['imagefile'], os.path.join(IMAGE_PATH,"image",str(pic.pk)+ext))
				makethumb(str(pic.pk)+ext)
				return redirect("cds_detaildemo", pk=kwargs["demo"])
				#return render(request, "cds/demopic_list.html", {"pics":self.get_pictures()})
			else:
				return HttpResponse("form nem valid")

		raise Http404

	def get(self, request, *args, **kwargs):
		return render(request, "cds/demopic_list.html", {"pics":self.get_pictures()})

class Voting(CsrfExemptMixin, LoginRequiredMixin, View):
	def get(self, request, *args, **kwargs):
		demo=get_object_or_404(Demo, pk=kwargs["demo"])
		y,n=demo.get_votes()
		return HttpResponse(str(y)+" "+str(n))

	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated():
			raise Http404
		v=True if request.POST.get('vote')=="1" else False
		demo=get_object_or_404(Demo, pk=kwargs["demo"])
		demo.vote(request.user, v)
		return redirect("cds_detaildemo", pk=kwargs["demo"])

class UploadDemo(CsrfExemptMixin, LoginRequiredMixin, TemplateView):
	template_name="cds/uploaddemo.html"
	def get_context_data(self, **kwargs):
		context=super(UploadDemo, self).get_context_data(**kwargs)
		context['demo']=self.kwargs['demo']
		context['form']=DemoDemoForm()
		return context
	def post(self, request, *args, **kwargs):
		demo=get_object_or_404(Demo, pk=self.kwargs['demo'])
		if demo.uploader != request.user:
			raise Http404
		form=DemoDemoForm(request.POST, request.FILES)
		if not form.is_valid():
			raise Http404
		ext=os.path.splitext(request.FILES['file'].name)[1]
		if ext!=".dem":
			raise Http404
		handle_uploaded_file(request.FILES['file'], os.path.join(IMAGE_PATH,"demo",str(demo.pk)+".dem"))
		demo.fileloc=str(demo.pk)+".dem"
		demo.save()
		return redirect("cds_detaildemo", pk=kwargs['demo'])

class UploadGameIcon(CsrfExemptMixin, LoginRequiredMixin, TemplateView):
	template_name="cds/uploadgameicon.html"
	#def get_context