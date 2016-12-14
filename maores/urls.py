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
from ahs.views import *
from haystack.generic_views import SearchView


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home_page),
    url(r'^mathletes/$', view_mathletes),
    url(r'^mathlete/first=([A-Za-z]+)&last=([A-Za-z]+)$', view_mathlete_menu),
    url(r'^mathlete/first=([A-Za-z]+)&last=([A-Za-z]+)&id=([0-9]+)$', view_mathlete),
    url(r'^mathlete/([0-9]+)/$', view_mathlete_from_id),
    url(r'^mathlete/([0-9]+)/competition_scores.csv', mathlete_scores_csv),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/$', view_competition),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/sweepstakes.html$', view_sweepstakes),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/([0-9]+)/$', view_competition_report),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/([A-Za-z0-9]+)/$', view_test),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/([A-Za-z0-9]+)/extra_rows$', view_test_extra_rows),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/([A-Za-z0-9]+)/detail/$', view_test_detail_report),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/([A-Za-z0-9]+)/detail/question_breakdown.csv$', test_question_breakdown_csv),
    url(r'^competitions/([0-9]+)/([a-z]+)/([a-z]+)/([A-Za-z0-9]+)/bowl/$', view_bowl),
    url(r'^competitions/$', view_competitions_tabbed),
    url(r'^competitions/all/$', view_competitions),
    url(r'^competitions/([0-9]+)/$',view_competitions_year),
    url(r'^schools/$', view_schools),
    url(r'^schools/([0-9]{4})/$', view_school),
    url(r'^schools/([0-9]{4})/firstpoints/$', first_points_default),
    url(r'^schools/([0-9]{4})/firstpoints/([0-9]{4})/$', first_points),
    url(r'^schools/([0-9]{4})/top-s-scores/([0-9]{4})/$', top_s_scores),
    url(r'^schools/([0-9]{4})/hall-of-fame/$', hall_of_fame),
    url(r'^search/', include('haystack.urls')),
    #url(r'^search/$', SearchView(), name='haystack_search'),
    url(r'^about.html', display_about),
    url(r'^ping/$', ping_pong),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', view_profile),
    url(r'^google1b28fba45037c690.html$', google_confirmation),
]
