from django.shortcuts import render
from results.models import *
from results.figs import *
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Count

def home_page(request):
    fig1 = participation_over_time()
    fig2 = difficulty_overall()
    return render(request, 'index.html', {'fig1': fig1, 'fig2':fig2})

def view_mathletes(request):
    if 'recent_mathletes' in request.COOKIES:
        has_recent = True
        r_mathletes = request.COOKIES['recent_mathletes']
        r_lst = [Mathlete.objects.get(pk=int(s)) for s in r_mathletes.split()]
    else:
        has_recent = False
        r_lst = []

    top = Mathlete.objects.annotate(num_tests=Count('testpaper')).filter(num_tests__gt=5).order_by('-avg_t')[:20]

    return render(request, 'mathletes.html', {'has_recent':has_recent,
       'recents':r_lst, 'top':top})

def view_school(request, spec_id):
    try:
        school = School.objects.get(id_num = spec_id)
    except:
        return Http404('School ID number does not exist')

    mathletes = Mathlete.objects.annotate(num_tests=Count('testpaper')).filter(mao_id__startswith=str(school.id_num)).order_by('-avg_t')
    return render(request, 'school.html', {'school': school, 'mathletes':mathletes})


def view_schools(request):
    schools = School.objects.order_by('name')
    return render(request, 'schools.html', {'schools': schools})

def view_mathlete_menu(request, first, last):
    lst = Mathlete.objects.filter(first_name=first, last_name=last)
    num_mathletes = len(lst)

    if num_mathletes == 0:
        raise Http404(first + ' ' + last + ' does not appear in the MAO database.')
    elif num_mathletes == 1:
        return HttpResponseRedirect('/mathlete/first=%s&last=%s&id=%s' \
            % (first, last, lst[0].mao_id))
    else:
        return render(request, 'mathlete_menu.html', {'lst':lst})

def view_mathlete(request, first, last, m_id):
    try:
        mathlete = Mathlete.objects.get(\
            first_name=first, 
            last_name=last, 
            mao_id=m_id)
    except:
        return HttpResponseRedirect('/mathlete/first=%s&last=%s' \
            % (first,last))

    fig1 = scores_over_time(mathlete)
    fig2 = handling_difficulty(mathlete)
    fig3 = histogram_of_scores(mathlete)

    response = render(request, 'mathlete.html', 
        {'mathlete': mathlete,
        'papers':mathlete.testpaper_set.order_by('-test__competition__date'),
        'fig1':fig1,
        'fig2':fig2,
        'fig3':fig3})

    if 'recent_mathletes' in request.COOKIES:
        r_mathletes = request.COOKIES['recent_mathletes']
        r_mathletes = str(mathlete.pk) + ' ' + r_mathletes
    else:
        r_mathletes = str(mathlete.pk)

    response.set_cookie('recent_mathletes', r_mathletes)
    return response

def redirect_competition(request, year, month, cat):
    cat = cat.title()
    months = {'dec':12, 'jan':1, 'feb':2, 'mar':3, 'apr':4,
        'january':1, 'february':2, 'march':3}

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

    return view_competition(request, c.date.year, c.date.month, c.date.day)

def view_competition(request, year, month, day):
    year = int(year)
    month = int(month)
    day = int(day)

    try:
        competition = Competition.objects.get(date=datetime.date(year, month, day))
    except:
        raise Http404("No competition on this day.")

    tests = competition.test_set.all()

    return render(request, 'competition.html',
        {'competition':competition,
         'tests':tests})

def view_test(request, year, month, day, division):
    year = int(year)
    month = int(month)
    day = int(day)

    try:
        competition = Competition.objects.get(date=datetime.date(year, month, day))
        test = competition.test_set.get(division=division)
    except:
        raise Http404("This is not a valid test URL.")

    testpapers = test.testpaper_set.all()

    return render(request, 'test.html',
        {'competition':competition,
        'test':test,
        'testpapers':testpapers})

def view_competitions(request):
    competitions = Competition.objects.all().order_by('-date')

    return render(request, 'competitions.html',
        {'competitions': competitions})


def return_static_file(request, fname):
    try:
        f = open(os.path.join(os.getcwd(), fname))
        return HttpResponse(f.read())
    except:
         raise Http404("File " + os.path.join(os.getcwd(), fname) + " does not exist.")
