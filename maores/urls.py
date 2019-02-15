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
from datetime import datetime

from django.conf.urls import include, url
from django.contrib import admin

from views import *
from ahs.views import *
from haystack.generic_views import SearchView

PRESENT_YEAR = str(datetime.datetime.today().year)

# views having to do with a single mathlete
mathlete_views = [
    url(r'^$', view_mathlete_from_id),
    url(r'^competition_scores.csv$', mathlete_scores_csv)
]

# views having to do with many mathletes
mathletes_views = [
    url(r'^$', MathleteListView.as_view()),
    url(r'^compare/$', compare_mathletes),
    url(r'^multiple$', multiple_mathletes),

]

school_views = [
    url(r'^$', view_school),
    url(r'^top-s-scores/(?P<year>[0-9]{4})/$', top_s_scores),
    url(r'^top-s-scores/$', top_s_scores, {
        'year': PRESENT_YEAR}),
    url(r'^first-points/(?P<year>[0-9]{4})/$', first_points),
    url(r'^first-points/$', first_points, {
        'year': PRESENT_YEAR}),
    url(r'^hall-of-fame/$', hall_of_fame),
    url(r'^sweeps.csv$', school_sweeps_csv)
]

test_views = [
    url(r'^$', view_test),
    url(r'^indiv.html$', view_test),
    url(r'^extra_rows/$', view_test_extra_rows),
    url(r'^detail/$', view_test_detail_report),
    url(r'^detail/question_breakdown.csv$', test_question_breakdown_csv),
    url(r'^bowl/$', view_bowl),
]

competition_views = [
    url(r'^$', view_competition),
    url(r'^sweepstakes.html$', view_sweepstakes),
    url(r'^(?P<division>[A-Za-z0-9&\%\- ]+)/', include(test_views))
]

insight_views = [
    url(r'^$', view_insights),
    url(r'^guessing-adeptly/$', view_guessing_adeptly),
]

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', home_page),
    url(r'^about.html', display_about),
    url(r'^search/', include('haystack.urls')),
    url(r'^suggest/$', submit_user_request),
    url(r'^suggest-elip/$', secret_user_request),
    url(r'^suggest/thanks/$', user_request_thanks),
    url(r'^google1b28fba45037c690.html$', google_confirmation),

    url(r'^mathletes/', include(mathletes_views)),
    url(r'^mathlete/(?P<id>[0-9]+)/', include(mathlete_views)),
    url(r'^mathlete-autocomplete/$', 
        MathleteAutocomplete.as_view(), 
        name='mathlete-autocomplete'),

    url(r'^competitions/$', view_competitions),
    url(r'^competitions/(?P<year>[0-9]+)/states/', 
        include(competition_views), 
        {'month': 'apr', 'cat': 'states'}),
    url(r'^competitions/(?P<year>[0-9]+)/(?P<month>[a-z]+)/(?P<cat>[a-z]+)/', 
        include(competition_views)),

    url(r'^schools/$', view_schools),
    url(r'^schools/(?P<school_id>[0-9]{4})/', include(school_views)),

    url(r'^insights/', include(insight_views)),

    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/$', view_profile),

    # legacy urls - soon to be deprecated
    url(r'^mathlete/first=([A-Za-z]+)&last=([A-Za-z]+)$', view_mathlete_menu),
    url(r'^mathlete/first=([A-Za-z]+)&last=([A-Za-z]+)&id=([0-9]+)$', view_mathlete),
]
