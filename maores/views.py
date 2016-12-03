import datetime

from itertools import chain

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from results.utils import *
from results.models import *
from results.figs import *

NUM_PAPERS_RENDER_IMMEDIATELY = 25

def display_about(request):
    return render(request, 'about.html', {})

def ping_pong(request):
    return HttpResponse('pong')
    
def home_page(request):
    return render(request, 'index.html', {})

def view_test_detail_report(
        request, 
        year, 
        month_abbr, 
        category, 
        division_abbr):
    year = int(year)
    month = get_num_month(get_full_month(month_abbr))
    category = category.title()
    division = get_full_division(division_abbr)

    try:
        test = Test.objects.get(
            competition__date__year=year, 
            competition__date__month=month,
            competition__category=category, 
            division = division)
    except:
        return Http404('Not a valid competition')

    fig1 = test_detail_report(test)
    return render(request, 'question_chart.html', {'fig1': fig1})

def view_mathletes(request):
    top = Mathlete.objects.annotate(num_tests=Count('testpaper')) \
        .filter(num_tests__gt=5) \
        .order_by('-avg_t')[:20]
    return render(request, 'mathletes.html', {'top':top})

def view_school(request, spec_id):
    try:
        school = School.objects.get(id_num = spec_id)
    except:
        return Http404('School ID number does not exist')

    mathletes = Mathlete.objects.annotate(num_tests=Count('testpaper')) \
        .filter(mao_id__startswith=str(school.id_num)) \
        .order_by('-avg_t')

    return render(request, 'school.html', {
        'school': school, 
        'mathletes':mathletes})

def view_schools(request):
    schools = School.objects.order_by('name')
    important_schools = School.objects.order_by('-num_mathletes')

    return render(request, 'schools.html', {
        'schools': schools, 
        'important_schools': important_schools})

def view_mathlete_menu(request, first, last):
    lst = Mathlete.objects.filter(first_name=first, last_name=last)
    num_mathletes = len(lst)

    if num_mathletes == 0:
        raise Http404(first + ' ' + last + ' does not appear in the MAO database.')
    elif num_mathletes == 1:
        return HttpResponseRedirect('/mathlete/%i' \
            % lst[0].pk)
    else:
    

        return render(request, 'mathlete_menu.html', {'lst':lst})

def view_mathlete_from_id(request, id):
    try:
        mathlete = Mathlete.objects.get(pk=int(id))
    except:
        return Http404('No such mathlete exists.')
    fig1 = scores_over_time(mathlete)
    fig2 = handling_difficulty(mathlete)
    fig3 = histogram_of_scores(mathlete)

    if request.user.is_authenticated():
        impression = MathleteImpression(mathlete=mathlete, user=request.user)
        impression.save()



    return render(request, 'mathlete.html', 
        {'mathlete': mathlete,
        'papers':mathlete.testpaper_set.order_by('-test__competition__date'),
        'fig1':fig1,
        'fig2':fig2,
        'fig3':fig3})

def view_mathlete(request, first, last, m_id):
    try:
        mathlete = Mathlete.objects.get(\
            first_name=first, 
            last_name=last, 
            mao_id=m_id)
    except:
        return HttpResponseRedirect('/mathlete/first=%s&last=%s' \
            % (first,last))

    return view_mathlete_from_id(request, str(mathlete.pk))

def mathlete_scores_csv(request, id):
    try:
        mathlete = Mathlete.objects.get(pk=id)
    except:
        return Http404("No such mathlete exists.")

    s = 'competition,tscore'
    for paper in mathlete.testpaper_set.order_by('test__competition__date'):
        s += '\n%s,%.3f' % (str(paper.test.competition) + ' (' + str(paper.test.division) + ')', 
            paper.t_score)

    return HttpResponse(s)

def view_competition(request, year, month, cat):
    cat = cat.title()
    months = {'dec':12, 'jan':1, 'feb':2, 'mar':3, 'apr':4,
        'january':1, 'february':2, 'march':3,}

    try:
        year = int(year)
        month = months[month.lower()]
    except:
        raise Http404("Could not parse month/year.")

    try:
        competition = Competition.objects.get(date__year=year,
            date__month=month, category=cat)
    except:
        raise Http404('Could not find such a competition.')

    tests = competition.test_set.all()

    return render(request, 'competition.html',
        {'competition':competition,
         'tests':tests})

def view_sweepstakes(request, year, month, cat):
    cat = cat.title()
    months = {'dec':12, 'jan':1, 'feb':2, 'mar':3, 'apr':4,
        'january':1, 'february':2, 'march':3,}

    try:
        year = int(year)
        month = months[month.lower()]
    except:
        raise Http404("Could not parse month/year.")

    try:
        competition = Competition.objects.get(date__year=year,
            date__month=month, category=cat)
    except:
        raise Http404('Could not find such a competition.')

    schools = set([team.school for bt in competition.bowltest_set.all() for team in bt.team_set.all()])
    divisions = ['Total T-Score'] + [test.division for test in 
        competition.bowltest_set.exclude(division='Algebra 1')]

    def school_to_res(school):
        lst = [school]
        for test in competition.bowltest_set.exclude(division='Algebra 1'):
            if test.team_set.filter(school=school).exists():
                lst.append(test.team_set.filter(school=school)[0].t_score)
            else:
                lst.append(0)
        lst.insert(1, sum(lst[1:]) - min(lst[1:]))
        return lst

    results = map(school_to_res, schools)
    results = sorted(results, key=lambda x : -x[1])

    return render(request, 'sweepstakes.html',{
        'competition': competition,
        'schools': schools,
        'divisions' : divisions,
        'results': results})

def view_bowl(request, year, month_abbr, category, division_abbr):

    year = int(year)
    month = get_num_month(get_full_month(month_abbr))
    category = category.title()
    division = get_full_division(division_abbr)

    try:
        competition = Competition.objects.get(
            date__year=year, 
            date__month=month, 
            category=category)
        bowl = competition.bowltest_set.get(division=division)
    except:
        return Http404('Not a valid competition')

    teams = bowl.team_set.all().order_by('place')


    return render(request, 'bowl.html', {
        'competition': competition,
        'bowl': bowl,
        'teams': teams})

def view_test_extra_rows(request, year, month_abbr, types, abbr):
    year = int(year)
    month = get_full_month(month_abbr)
    cat = types.title()
    division = get_full_division(abbr)

    try:
        competition = Competition.objects.get(date__year=year,
            date__month=int(get_num_month(month)), category=cat)
        test = competition.test_set.get(division=division)
    except:
        raise Http404('Could not find such a test')

    if test.testpaper_set.count() > NUM_PAPERS_RENDER_IMMEDIATELY:
        testpapers = test.testpaper_set.all()[NUM_PAPERS_RENDER_IMMEDIATELY:]
    else:
        testpapers = []



    return render(request, 'test_rows.html',
        {'testpapers':testpapers})  


def view_test(request, year, month_abbr, types, abbr):
    year = int(year)
    month = get_full_month(month_abbr)
    cat = types.title()
    division = get_full_division(abbr)

    try:
        competition = Competition.objects.get(date__year=year,
            date__month=int(get_num_month(month)), category=cat)
        test = competition.test_set.get(division=division)
    except:
        raise Http404('Could not find such a test')

    if test.testpaper_set.count() > NUM_PAPERS_RENDER_IMMEDIATELY:
        testpapers = test.testpaper_set.all()[:NUM_PAPERS_RENDER_IMMEDIATELY]
    else:
        testpapers = test.testpaper_set.all()



    return render(request, 'test.html',
        {'competition':competition,
        'test':test,
        'testpapers':testpapers})   


def view_competitions(request):
    competitions = Competition.objects.all().order_by('-date')


    return render(request, 'competitions.html',
        {'competitions': competitions})

def view_competitions_tabbed(request):
    years = sorted(list(set([c.date.year for c in Competition.objects.all()])), reverse=True)
    seasons = []
    for year in years:
        seasons.append((year, list(Competition.objects.filter(date__year=year).order_by('date'))))


    return render(request, 'experimental_competitions.html',
                    {'seasons' : seasons, 'years' : years})


def view_competitions_year(request, year):
    year = int(year)
    competitions = Competition.objects.filter(date__year = year)


    return render(request, 'competitions.html',
        {'competitions': competitions})

def view_competition_report(request, year, month, types, id_school):
    try:
        year = int(year)
        month = get_full_month(month)
        cat = types.title()
        id_school = int(id_school)
    except:
        raise Http404('Not a valid URL')

    try:
        competition = Competition.objects.get(date__year = year,
            date__month = int(get_num_month(month)), category = cat)
    except:
        raise Http404('Not a valid competition')

    try:
        school = School.objects.get(id_num = id_school)
    except:
        raise Http404('Not a valid school ID')  

    dictio = {}
    for test in competition.test_set.all():
        dictio[test.division] = test.testpaper_set.filter(school = school)


    return render(request, 'school_competition_report.html',
                    {'dictio': dictio, 'competition' : competition, 
                    'school' : school})

@login_required
def view_profile(request):
    if request.user.first_name and request.user.last_name:
        mathletes = Mathlete.objects.filter(
            first_name=request.user.first_name,
            last_name=request.user.last_name)
    else:
        mathletes = []


    return render(request, 'account/profile.html', {
        'request': request,
        'mathletes': mathletes})

def return_static_file(request, fname):
    try:
        f = open(os.path.join(os.getcwd(), fname))
        return HttpResponse(f.read())
    except:
         raise Http404("File " + os.path.join(os.getcwd(), fname) + " does not exist.")
