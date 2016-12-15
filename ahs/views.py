import datetime
# import pandas as pd

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Count
from django.contrib.auth.decorators import login_required

from results.models import *

# Create your views here.

@login_required
def first_points(request, school_id, year):
    if not request.user.email.endswith("@ahschool.com"):
        return Http404("You do not have access to this page.")

    school_id, year = int(school_id), int(year)

    try:
        school = School.objects.get(id_num=school_id)
    except:
        return Http404('No school with that id number exists.')

    papers = TestPaper.objects.filter(place=1, school=school, test__competition__date__year=year) \
        .order_by('test__competition__date')

    mathletes = papers.values('mathlete') \
        .annotate(num_wins=Count('test')) \
        .order_by('-num_wins')
    mathletes = [(Mathlete.objects.get(pk=m['mathlete']), m['num_wins']) for m in mathletes]

    years = sorted(list(set([c.date.year for c in Competition.objects.all()])))

    return render(request, 'first_points.html', {
        'school': school, 
        'year' : year,
        'years': years,
        'papers': papers, 
        'mathletes': mathletes})

def first_points_default(request, school_id):
    return first_points(request, school_id, datetime.datetime.now().year)

def get_class_of(school, year):

    lst = Mathlete.objects.filter(testpaper__school=school)

    for yr in range(year-3,year+1):
        lst = lst.filter(testpaper__test__competition__date__year=yr)

    lst = lst.distinct()
    print len(lst)
    return lst

@login_required
def hall_of_fame(request, school_id):

    try:
        school = School.objects.get(id_num=school_id)
    except:
        return Http404('No school with that id number exists.')

    years = sorted(list(set([c.date.year for c in Competition.objects.all()])), reverse=True)
    years = years[:-3]
    d = {}
    for y in years:
        d[y] = get_class_of(school, y)

    return render(request, 'hall_of_fame.html', {
        'years': years,
        'd' : d
        })

@login_required
def top_s_scores(request, school_id, year):
    if not request.user.email.endswith("@ahschool.com"):
        return Http404("You do not have access to this page.")
        
    school_id, year = int(school_id), int(year)

    try:
        school = School.objects.get(id_num=school_id)
    except:
        return Http404('No school with that id number exists.')

    competitions = Competition.objects.filter(date__year=year) \
        .order_by('date')[:5]

    threshold = min(
        competitions.count() / 2, 
        competitions.count() - 1)

    keys = [
        'mathlete__first_name', 
        'mathlete__last_name', 
        'test__division', 
        'test__competition__name' ]

    attrs = keys + ['s_score']

    papers_query = school.testpaper_set.filter(
            test__competition__in=competitions) \
        .values(*attrs)

    papers = pd.DataFrame(list(papers_query)) \
        .drop_duplicates(subset=keys) \
        .set_index(keys) \
        .unstack() \
        .dropna(thresh=threshold)

    papers['Top 3'] = papers.apply(lambda row : row.nlargest(3).sum(), axis=1)
    papers.sort_values(by='Top 3', ascending=False, inplace=True)

    years = sorted(list(set([c.date.year for c in Competition.objects.all()])))
    
    return render(request, 'top_s_scores.html', {
        'year': year, 
        'years' : years,
        'school': school,
        'papers': papers})
