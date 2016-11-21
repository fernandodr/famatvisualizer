import datetime

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404, HttpResponse

from results.models import *

# Create your views here.

def first_points(request, school_id, year):
    start_time = datetime.datetime.now()
    school_id, year = int(school_id), int(year)

    try:
        school = School.objects.get(id_num=school_id)
    except:
        return Http404('No school with that id number exists.')

    papers = TestPaper.objects.filter(place=1, school=school, test__competition__date__year=year)
    end_time = datetime.datetime.now()
    load_time = end_time - start_time
    return render(request, 'first_points.html', {'papers': papers, 'loadtime': load_time})

def first_points_default(request, school_id):
    return first_points(request, school_id, datetime.datetime.now().year)