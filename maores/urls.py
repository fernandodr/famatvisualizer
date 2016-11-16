"""maores URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from views import *


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home_page),
    url(r'^mathletes/$', view_mathletes),
    url(r'^mathlete/first=([A-Za-z]+)&last=([A-Za-z]+)$', view_mathlete_menu),
    url(r'^mathlete/first=([A-Za-z]+)&last=([A-Za-z]+)&id=([0-9]+)$', view_mathlete),
    url(r'^mathlete/([0-9]+)/$', view_mathlete_from_id),
    url(r'^mathlete/([0-9]+)/competition_scores.csv', mathlete_scores_csv),
    url(r'^competition/([0-9]+)/([0-9]+)/([0-9]+)/$', view_competition),
    url(r'^competition/([0-9]+)/([a-z]+)/([a-z]+)/$', redirect_competition),
    url(r'^competition/([0-9]+)/([a-z]+)/([a-z]+)/([0-9]+)/$', view_competition_report),
    url(r'^competition/([0-9]+)/([a-z]+)/([a-z]+)/([A-Za-z0-9]+)/$', redirect_view_test),
    url(r'^competition/([0-9]+)/([a-z]+)/([a-z]+)/([A-Za-z0-9]+)/detail/$', view_test_detail_report),
    url(r'^competition/([0-9]+)/([0-9]+)/([0-9]+)/([A-Za-z]+[0-9]+)/$', view_test),
    url(r'^competitions/$', view_competitions_tabbed),
    url(r'^competitions/all/$', view_competitions),
    url(r'^competitions/([0-9]+)/$',view_competitions_year),
    url(r'^schools/$', view_schools),
    url(r'^school/([0-9]+)/$', view_school),
    url(r'^search/', include('haystack.urls')),
    url(r'^static/(.*)', return_static_file),
    url(r'ping/', ping_pong),
]
