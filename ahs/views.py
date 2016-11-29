import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Count

from results.models import *

# Create your views here.

def first_points(request, school_id, year):
    start_time = datetime.datetime.now()
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

    end_time = datetime.datetime.now()
    load_time = end_time - start_time
    return render(request, 'first_points.html', {
        'school': school, 
        'year' : year,
        'years': years,
        'papers': papers, 
        'mathletes': mathletes, 
        'loadtime': load_time})

def first_points_default(request, school_id):
    return first_points(request, school_id, datetime.datetime.now().year)