from results.utils import *
from results.models import *
import datetime
from results.figs import *
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def ping_pong(request):
    return HttpResponse('pong')
    
def home_page(request):
    start_time = datetime.datetime.now()
    end_time = datetime.datetime.now()
    load_time = end_time-start_time
    return render(request, 'index.html', {'loadtime': load_time})

def view_test_detail_report(request, year, month_abbr, category, division_abbr):
    start_time = datetime.datetime.now()

    year = int(year)
    month = get_num_month(get_full_month(month_abbr))
    category = category.title()
    division = get_full_division(division_abbr)

    try:
        test = Test.objects.get(competition__date__year=year, competition__date__month=month,
                            competition__category=category, division = division)
    except:
        return Http404('Not a valid competition')

    fig1 = test_detail_report(test)
    end_time = datetime.datetime.now()
    load_time = end_time-start_time
    return render(request, 'question_chart.html', {'fig1': fig1, 'loadtime': load_time})

def view_mathletes(request):
    start_time = datetime.datetime.now()

    top = Mathlete.objects.annotate(num_tests=Count('testpaper')).filter(num_tests__gt=5).order_by('-avg_t')[:20]
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'mathletes.html', {'top':top, 'loadtime': load_time})

def view_school(request, spec_id):
    start_time = datetime.datetime.now()
    try:
        school = School.objects.get(id_num = spec_id)
    except:
        return Http404('School ID number does not exist')

    mathletes = Mathlete.objects.annotate(num_tests=Count('testpaper')).filter(mao_id__startswith=str(school.id_num)).order_by('-avg_t')
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'school.html', {'school': school, 'mathletes':mathletes, 'loadtime': load_time})


def view_schools(request):
    start_time = datetime.datetime.now()
    schools = School.objects.order_by('name')
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'schools.html', {'schools': schools, 'loadtime': load_time})

def view_mathlete_menu(request, first, last):
    lst = Mathlete.objects.filter(first_name=first, last_name=last)
    num_mathletes = len(lst)

    if num_mathletes == 0:
        raise Http404(first + ' ' + last + ' does not appear in the MAO database.')
    elif num_mathletes == 1:
        return HttpResponseRedirect('/mathlete/%i' \
            % lst[0].pk)
    else:
        end_time = datetime.datetime.now()
        load_time = end_time-start_time

        return render(request, 'mathlete_menu.html', {'lst':lst, 'loadtime': load_time})

def view_mathlete_from_id(request, id):
    start_time = datetime.datetime.now()
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

    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'mathlete.html', 
        {'mathlete': mathlete,
        'papers':mathlete.testpaper_set.order_by('-test__competition__date'),
        'fig1':fig1,
        'fig2':fig2,
        'fig3':fig3, 'loadtime': load_time})

def view_mathlete(request, first, last, m_id):
    start_time = datetime.datetime.now()
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

def redirect_competition(request, year, month, cat):
    start_time = datetime.datetime.now()
    cat = cat.title()
    months = {'dec':12, 'jan':1, 'feb':2, 'mar':3, 'apr':4,
        'january':1, 'february':2, 'march':3,}

    try:
        year = int(year)
        month = months[month.lower()]
    except:
        raise Http404("Could not parse month/year.")

    try:
        c = Competition.objects.get(date__year=year,
            date__month=month, category=cat)
    except:
        raise Http404('Could not find such a competition.')
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return view_competition(request, c.date.year, c.date.month, c.date.day)

def view_competition(request, year, month, day):
    start_time = datetime.datetime.now()
    year = int(year)
    month = int(month)
    day = int(day)
    date = datetime.date(year, month, day)

    try:
        competition = Competition.objects.get(date=date)
    except:
        raise Http404("No competition on this day.")

    tests = competition.test_set.all()
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'competition.html',
        {'competition':competition,
         'tests':tests, 'loadtime': load_time})

def view_bowl(request, year, month_abbr, category, division_abbr):
    start_time = datetime.datetime.now()

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

    end_time = datetime.datetime.now()
    load_time = end_time-start_time
    return render(request, 'bowl.html', {
        'competition': competition,
        'bowl': bowl,
        'teams': teams,
        'loadtime': load_time})

def view_test(request, year, month, day, abbr):
    start_time = datetime.datetime.now()
    year = int(year)
    month = int(month)
    day = int(day)

    date = datetime.date(year, month, day)

    try:
    	division = get_full_division(abbr)
        competition = Competition.objects.get(date=date)
        test = competition.test_set.get(division=division)
    except:
        raise Http404("This is not a valid test URL.")

    testpapers = test.testpaper_set.all().order_by('place')
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'test.html',
        {'competition':competition,
        'test':test,
        'testpapers':testpapers, 
        'loadtime': load_time})   

def redirect_view_test(request, year, month_abbr, types, category1):
    start_time = datetime.datetime.now()
    year = int(year)
    month = get_full_month(month_abbr)
    cat = types.title()

    try:
        c = Competition.objects.get(date__year=year,
            date__month=int(get_num_month(month)), category=cat)
    except:
        raise Http404('Could not find such a test')
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return view_test(request, c.date.year, c.date.month, c.date.day, category1)


def view_competitions(request):
    start_time = datetime.datetime.now()
    competitions = Competition.objects.all().order_by('-date')
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'competitions.html',
        {'competitions': competitions, 'loadtime': load_time})

def view_competitions_tabbed(request):
    start_time = datetime.datetime.now()
    years = sorted(list(set([c.date.year for c in Competition.objects.all()])), reverse=True)
    dict = {}
    for year in years:
        dict[year] = list(Competition.objects.filter(date__year=year).order_by('date'))
    end_time = datetime.datetime.now()
    load_time = end_time-start_time
    print years

    return render(request, 'experimental_competitions.html',
                    {'dict' : dict, 'years':years, 'loadtime': load_time})


def view_competitions_year(request, year):
    start_time = datetime.datetime.now()
    year = int(year)
    competitions = Competition.objects.filter(date__year = year)
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'competitions.html',
        {'competitions': competitions, 'loadtime': load_time})

def view_competition_report(request, year, month, types, id_school):
    start_time = datetime.datetime.now()
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
    end_time = datetime.datetime.now()
    load_time = end_time-start_time

    return render(request, 'school_competition_report.html',
                    {'dictio': dictio, 'competition' : competition, 
                    'school' : school, 'loadtime': load_time})

@login_required
def view_profile(request):
    return render(request, 'account/profile.html', {'request': request})

def return_static_file(request, fname):
    try:
        f = open(os.path.join(os.getcwd(), fname))
        return HttpResponse(f.read())
    except:
         raise Http404("File " + os.path.join(os.getcwd(), fname) + " does not exist.")
