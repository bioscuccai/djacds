from django.conf.urls import url, patterns

from cds import views

urlpatterns=patterns('',
    url(r'^$', views.DemoList.as_view()),

	url(r'^addgame/$', views.GameCreate.as_view(), name="cds_addgame"),
	url(r'^listgames/$', views.GameList.as_view(), name="cds_listgames"),
	url(r'^detailgame/(?P<pk>\d+)/$', views.GameDetail.as_view(), name="cds_detailgame"),

	url(r'^adddemo/$', views.DemoCreate.as_view(), name="cds_adddemo"),
	url(r'^listdemos/', views.DemoList.as_view(), name="cds_listdemos"),
	url(r'^detaildemo/(?P<pk>\d+)/$', views.DemoDetail.as_view(), name="cds_detaildemo"),
	url(r'^updatedemo/(?P<pk>\d+)/$', views.DemoUpdate.as_view(), name="cds_updatedemo"),

    url(r'^adddemocomment/(?P<demop>\d+)/$', views.DemoCommentCreate.as_view(), name="cds_adddemocomment"),
    url(r'^listdemocomments/(?P<demo>\d+)/$', views.DemoCommentList.as_view(), name='cds_listdemocomments'),

    url(r'^demopic/(?P<demo>\d+)/$', views.DemoPicView.as_view(), name="cds_demopic"),

    url(r'^voting/(?P<demo>\d+)/$', views.Voting.as_view(), name="cds_voting"),

    url(r'^addcheat/$', views.CheatCreate.as_view(), name="cds_addcheat"),

    url(r'^demopergame/(?P<game>\d+)/$', views.DemoPerGame.as_view(), name="cds_demopergame"),
    url(r'^demopercheat/(?P<cheat>\d+)/$', views.DemoPerCheat.as_view(), name="cds_demopercheat"),

    url(r'^uploaddemo/(?P<demo>\d+)/$', views.UploadDemo.as_view(), name="cds_uploaddemo"),
)
