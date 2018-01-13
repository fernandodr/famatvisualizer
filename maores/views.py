import datetime
from itertools import chain
import csv
import numpy as np

from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.db.models import Count, Avg, Sum, Q
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from el_pagination.views import AjaxListView
from dal import autocomplete

from results.utils import *
from results.models import *
from results.figs import *
from results.forms import *

NUM_PAPERS_RENDER_IMMEDIATELY = 25

def _chk2_asarray(a, b, axis):
    if axis is None:
        a = np.ravel(a)
        b = np.ravel(b)
        outaxis = 0
    else:
        a = np.asarray(a)
        b = np.asarray(b)
        outaxis = axis
    return a, b, outaxis

def _ttest_finish(df,t):
    """Common code between all 3 t-test functions."""
    s = np.random.standard_t(df, size=100000)
    prob = 2.0*np.sum(s > np.abs(t)) / len(s)  # use np.abs to get upper tail
    if t.ndim == 0:
        t = t[()]

    return t, prob

def ttest_ind(a, b, axis=0, equal_var=True):
    a, b, axis = _chk2_asarray(a, b, axis)
    v1 = np.var(a, axis, ddof=1)
    v2 = np.var(b, axis, ddof=1)
    n1 = a.shape[axis]
    n2 = b.shape[axis]

    if (equal_var):
        df = n1 + n2 - 2
        svar = ((n1 - 1) * v1 + (n2 - 1) * v2) / float(df)
        denom = np.sqrt(svar * (1.0 / n1 + 1.0 / n2))
    else:
        vn1 = v1 / n1
        vn2 = v2 / n2
        df = ((vn1 + vn2)**2) / ((vn1**2) / (n1 - 1) + (vn2**2) / (n2 - 1))

        # If df is undefined, variances are zero (assumes n1 > 0 & n2 > 0).
        # Hence it doesn't matter what df is as long as it's not NaN.
        df = np.where(np.isnan(df), 1, df)
        denom = np.sqrt(vn1 + vn2)

    d = np.mean(a, axis) - np.mean(b, axis)
    t = np.divide(d, denom)
    t, prob = _ttest_finish(df, t)

    return t, prob

def display_about(request):
    return render(request, 'about.html')

def google_confirmation(request):
    return render(request, 'google.html', {})
    
def home_page(request):
    return render(request, 'index.html', {})

def view_test_detail_report(
        request, 
        year, 
        month, 
        cat, 
        division):
    year = int(year)
    month = get_num_month(get_full_month(month))
    category = cat.title()
    division = get_full_division(division)

    try:
        test = Test.objects.get(
            competition__date__year=year, 
            competition__date__month=month,
            competition__category=category, 
            division = division)
    except:
        raise Http404('Not a valid competition')
    return render(request, 'question_chart.html', {'test': test})

def test_question_breakdown_csv(
        request, 
        year, 
        month, 
        cat, 
        division):
    year = int(year)
    month = get_num_month(get_full_month(month))
    category = cat.title()
    division = get_full_division(division)

    try:
        test = Test.objects.get(
            competition__date__year=year, 
            competition__date__month=month,
            competition__category=category, 
            division = division)
    except:
        raise Http404('Not a valid competition')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="question_breakdown.csv"'

    writer = csv.writer(response)
    writer.writerow(['Question Number', 'Right', 'Blank', 'Wrong'])
    for q in test.question_set.all():
        r, w, b = q.num_correct, q.num_wrong, q.num_blank
        t = r + w + b
        writer.writerow([
            'Question #%i' % q.number,
            100.0*r / t,
            100.0*b / t,
            100.0*w / t])

    return response


def view_mathletes(request):
    top = Mathlete.objects.annotate(num_tests=Count('testpaper')) \
        .filter(num_tests__gt=5) \
        .order_by('-avg_t')
    return render(request, 'mathletes.html', {'top':top})

class MathleteListView(AjaxListView):
    context_object_name = "mathletes"
    template_name = "mathletes.html"
    page_template='mathletes_page.html'

    def get_queryset(self):
        return Mathlete.objects.annotate(num_tests=Count('testpaper')) \
            .filter(num_tests__gt=5) \
            .order_by('-avg_t')

def view_school(request, school_id):
    try:
        school = School.objects.filter(id_num = school_id)[0]
    except:
        raise Http404('School ID number does not exist')

    mathletes = Mathlete.objects.annotate(num_tests=Count('testpaper')) \
        .filter(mao_id__startswith=str(school.id_num)) \
        .order_by('-avg_t')

    return render(request, 'school.html', {
        'school': school, 
        'mathletes':mathletes})

def view_schools(request):
    schools = School.objects.order_by('name')
    important_schools = School.objects \
        .annotate(rank=Coalesce(Sum('sweeps__total_t'), 0)) \
        .order_by('-rank')

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
        raise Http404('No such mathlete exists.')
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
        raise Http404("No such mathlete exists.")

    s = 'competition,T-Score'
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

    divisions = ['Total T-Score'] + [test.division for test in 
        competition.bowltest_set.exclude(division='Algebra 1')]

    def sweeps_to_res(sweeps):
        lst = [sweeps.school, sweeps.total_t]
        for test in competition.bowltest_set.exclude(division='Algebra 1'):
            if test.team_set.filter(school=sweeps.school).exists():
                lst.append(test.team_set.filter(school=sweeps.school)[0].t_score)
            else:
                lst.append(0)
        return lst

    sweeps = competition.sweeps_set.all()
    results = map(sweeps_to_res, sweeps)

    return render(request, 'sweepstakes.html',{
        'competition': competition,
        'divisions' : divisions,
        'results': results})

def view_bowl(request, year, month, cat, division):

    year = int(year)
    month = get_num_month(get_full_month(month))
    category = cat.title()
    division = get_full_division(division)

    try:
        competition = Competition.objects.get(
            date__year=year, 
            date__month=month, 
            category=category)
        bowl = competition.bowltest_set.get(division=division)
    except:
        raise Http404('Not a valid competition')

    teams = bowl.team_set.all().order_by('place')


    return render(request, 'bowl.html', {
        'competition': competition,
        'bowl': bowl,
        'teams': teams})

def view_test_extra_rows(request, year, month, cat, division):
    year = int(year)
    month = get_full_month(month)
    cat = cat.title()
    division = get_full_division(division)

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


def view_test(request, year, month, cat, division):
    year = int(year)
    month = get_full_month(month)
    cat = cat.title()
    division = get_full_division(division)

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
    years = sorted(list(set([c.date.year for c in Competition.objects.all()])), reverse=True)
    seasons = []
    for year in years:
        seasons.append((year, list(Competition.objects.filter(date__year=year).order_by('date'))))


    return render(request, 'competitions.html',
                    {'seasons' : seasons, 'years' : years})

def view_competition_report(request, year, month, cat, id_school):
    try:
        year = int(year)
        month = get_full_month(month)
        cat = cat.title()
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

class MathleteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        mathletes = Mathlete.objects.all().order_by('avg_place')

        if self.q:
            q = self.q.replace(',', '')
            q = q.replace('.', '')
            words = q.split()
            if len(words) == 1:
                mathletes = mathletes.filter(Q(first_name__istartswith=words[0]) | Q(last_name__istartswith=words[0]))
            else:
                mathletes = mathletes.filter(Q(first_name__istartswith=words[0]) | Q(first_name__istartswith=words[1])) \
                    .filter(Q(last_name__istartswith=words[0]) | Q(last_name__istartswith=words[1]))

        return mathletes


def compare_mathletes(request):
    if 'first' in request.GET and 'second' in request.GET:
        try:
            first = Mathlete.objects.get(pk=int(request.GET['first']))
            second = Mathlete.objects.get(pk=int(request.GET['second']))
        except:
            return HttpResponseRedirect('/mathletes/compare') 

        first_ts = [x.t_score for x in first.testpaper_set.all() if x.t_score is not None]
        second_ts = [x.t_score for x in second.testpaper_set.all() if x.t_score is not None]

        t, prob = ttest_ind(first_ts, second_ts, equal_var=False)

        ttest = {'t': t, 'prob': prob,}

        tests_both_took = Test.objects.filter(testpaper__mathlete=first) \
            .filter(testpaper__mathlete=second) \
            .order_by('-competition__date')


        head_to_head = [(t, t.testpaper_set.get(mathlete=first),t.testpaper_set.get(mathlete=second))
         for t in tests_both_took]

        wins, losses, ties = 0, 0, 0
        for t, t1, t2 in head_to_head:
            if t1.score > t2.score:
                wins += 1
            elif t1.score == t2.score:
                ties += 1
            else:
                losses += 1

        return render(request, 
            'compare_mathletes_report.html',
            {'first': first, 
                'second': second,
                'ttest': ttest,
                'head_to_head': head_to_head,
                'wins': wins,
                'ties': ties,
                'losses': losses})
        # TODO; make report!

    else:
        form = CompareMathletesForm()
        return render(request, 'compare_mathletes.html', {'form': form})


def submit_user_request(request):
    if request.method == 'POST':
        form = UserRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/suggest/thanks')
    else:
        form = UserRequestForm()
    
    return render(request, 'user_request.html', {'form': form})

def user_request_thanks(request):
    return render(request, 'user_request_thanks.html', {})
