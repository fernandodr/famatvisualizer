import datetime
import urllib2
import BeautifulSoup
import re
import numpy as np
import itertools
from tqdm import tqdm

from results.models import *

def convert_answer_str(answer):
    formatted_answer = ''
    if answer.lower().find('throw') != -1:
        return 'ABCDE'
    if answer.find('A') != -1:
        formatted_answer += 'A'
    if answer.find('B') != -1:
        formatted_answer += 'B'
    if answer.find('C') != -1:
        formatted_answer += 'C'
    if answer.find('D') != -1:
        formatted_answer += 'D'
    if answer.find('E') != -1:
        formatted_answer += 'E'
    return formatted_answer

# TODO: must implement for states
def add_sweepstakes(competition):
    competition.sweeps_set.all().delete()
    schools = set([team.school for 
        bt in competition.bowltest_set.all() 
        for team in bt.team_set.all()])
    divisions = [test.division for test in 
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

    for i, result in enumerate(results):
        sweep = Sweeps(
            school=result[0],
            competition=competition,
            rank=i+1,
            total_t= result[1])
        sweep.save()

def wipe():
    """
    Purges the database.
    """
    Competition.objects.all().delete()
    Mathlete.objects.all().delete()
    Test.objects.all().delete()
    TestPaper.objects.all().delete()
    Question.objects.all().delete()
    QuestionAnswer.objects.all().delete()
    School.objects.all().delete()

def import_detail_report(
        comp_name, 
        date, 
        name, 
        category, 
        divs=None, 
        topics=None,
        region=None,
        is_150_scale=False):
    """
    Downloads the results from an indiv detail report.

    Parameters
    ----------
    comp_name : str
        Name of the competition as found in a famat.org URL. For example, 
        http://famat.org/Downloadable/Results/Combined02132016/Calculus_Detail.html
        would have comp_name = 'Combined02132016' 
    date : datetime.date
        The day that the competition was held on.
    name : str
        Name for internal tracking of the competition. 
        A couple of conventions to use:
        - for a regional, follow 'Jan Regional', 'Feb Regional', 
          or 'March Regional'
        - for an invite, the name of the school that hosted it
        - for State Convention, TODO: determine convention
    category : str
        One of "Regional", "Invite", or "States"
    divs : (list of str) or None
        A list of the names of the divisions at the competition.
        If None, will default to a master list of common divisions.
    topics: (list of str) or None
        A list of the names of the topic tests at the competition.
        Note that this is only relevant for States competitions,
        and otherwise this parameter should be None.
    region : int or None
        If you are downloading a regional competition, say so.
    is_150_scale : bool
        True if scores are being measured with the 150 scale.
    """

    # if user does not provide divisions, use default
    if divs==None:
        divisions = ['Calculus', 'Statistics', 'Precalculus', 
                     'Algebra 2', 'Geometry', 'Algebra 1', 
                     'Theta', 'Alpha', 'Calculus 1', 'Calculus 2']
    else:
        divisions = divs

    if topics is not None:
        test_ids = zip(divisions, [True]*len(divisions)) + \
            zip(topics, [False]*len(topics))
    else:
        test_ids = zip(divisions, [True]*len(divisions))
    
    # fail loudly if this competition is already in the database    
    assert type(date) == datetime.date
    assert Competition.objects.filter(date=date).count() == 0
    competition = Competition(date=date, name=name, category=category)
    competition.save()

    print '\n%s' % comp_name
    
    for division, is_main_test in test_ids:
        try:
            if is_main_test and category is not 'States':
                url_division = division
            elif is_main_test and category is 'States':
                url_division = division + ' Individual'
            else:
                url_division = division[1]

            url = ('http://famat.org/Downloadable/Results/' + 
                   comp_name + "/" + url_division + "_Detail.html").replace(' ', '%20')
            raw_page = urllib2.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(raw_page)
            
            url = ('http://famat.org/Downloadable/Results/' + 
                   comp_name + "/" + url_division + "_Indv.html").replace(' ', '%20')
            raw_page = urllib2.urlopen(url)
            other_soup = BeautifulSoup.BeautifulSoup(raw_page)
        except:
            print '\t\t\t%s' % str(division)
            continue
            
        if is_main_test:
            test = Test(competition=competition, division=division)
            test.save()
        else:
            test = Test(
                competition=competition, 
                division=division[1], 
                level=division[0])
            test.save()
        
        questions = []
        answers = [convert_answer_str(a.text) for a in soup.findAll(attrs={"class":"theanswer"})]
        for i, answer in enumerate(answers):
            q = Question(test=test, number=i+1, answer=answer)
            questions.append(q)
            q.save()
        
        table_of_results = soup.findAll('table')[-1]
        rows = table_of_results.findChildren(['th', 'tr'])
        other_table = other_soup.findAll('table')[0]
        other_rows = other_table.findChildren(['th', 'tr'])
        
        header = rows.pop(0)
        other_header = other_rows.pop(0)
    
        num_failures = 0
        for i,row in enumerate(rows):
            # try:
                cells = row.findChildren('td')
                mao_id = other_rows[i].findChildren('td')[4].text[0:7]

                names = cells[3].text.title().split(' ')
                if len(names) > 1:
                    first, last = names[0], names[-1]
                elif len(names) == 1:
                    first, last = "", names[0]
                else:
                    first, last = "", ""
                try:
                    mathlete = Mathlete.objects.get(first_name=first,
                                                    last_name =last,
                                                    mao_id = mao_id)
                except:
                    mathlete = Mathlete(first_name=first,
                                        last_name=last,
                                        mao_id = mao_id)
                    mathlete.save()
                
                try:
                    school = School.objects.get(name=cells[2].text)
                except:
                    school = School(name=cells[2].text)
                    school.save()
                
                if region != None:
                    if school.region != region:
                        school.region = region
                        school.save()
                
                place = int(re.match('([0-9]{1,4})', other_rows[i].findChildren('td')[0].text).groups(0)[0])                        
                paper = TestPaper(mathlete=mathlete, school=school, test=test, place=place)
                paper.save()
                
                cells = cells[4:]
                for j, answer in enumerate(cells):
                    a_class = dict(answer.attrs).get('class', '')
                    if 'R' in a_class:
                        points = 4
                    elif 'B' in a_class:
                        points = 0
                    else:
                        points = -1
                    qa = QuestionAnswer(paper=paper, 
                        question=questions[j], 
                        givenanswer=answer.text.strip('&nbsp;').upper(),
                        points=points)
                    qa.save()
                paper.save()
            # except:
            #     num_failures += 1
        test.save()
        for paper in TestPaper.objects.filter(test=test):
            paper.save_post_test()
        print "%s indiv data retrieved (%i failures)" % (division, num_failures)

        try:
            if not is_main_test:
                continue
            url = ('http://famat.org/Downloadable/Results/' + 
                   comp_name + "/" + division + "_Bowl.html").replace(' ', '%20')
            raw_page = urllib2.urlopen(url)
            team_soup = BeautifulSoup.BeautifulSoup(raw_page)
        except:
            continue

        bowl_test = BowlTest(competition=competition, division=division)
        bowl_test.save()

        ids = [row.findChildren('td')[4].text for row in other_soup.table.findChildren('tr')[1:]]
        for i, row in enumerate(team_soup.table.findChildren('tr')[1:]):
            cells = row.findChildren('td')

            score = int(cells[9].text)
            school_id = cells[3].text

            try:
                school = test.testpaper_set.filter(mathlete__mao_id__startswith=school_id)[0].school
            except:
                try:
                    school = School.objects.filter(id_num=int(school_id))[0]
                except:
                    user_input = raw_input('School with id %s is not found. Enter school name: ' % school_id)
                    school = School(name = user_input, id_num = int(school_id))
                    school.save()

            differences = [10000,]
            for team_number in range(1,5):
                team_member_ids = set([id[:7] for id in ids if re.match('%s[0-9]{4}%i' % (school_id, team_number), id)])
                indivs = list(itertools.chain(*[test.testpaper_set.filter(mathlete__mao_id=id) \
                    for id in team_member_ids]))
                indivs =  sorted(indivs, key=lambda x : x.score, reverse=True)

                if len(indivs) > 4:
                    indivs = indivs[:4]

                scores = [paper.score for paper in indivs]
                empirical_scores = [int(cells[j].text) for j in range(5,9) \
                    if re.match('[-]{0,1}[0-9]{1,3}', cells[j].text) is not None]
                if is_150_scale:
                    empirical_scores = [s-30 for s in empirical_scores]

                if len(scores) != len(empirical_scores):
                    differences.append(9999)
                else:
                    diff = np.linalg.norm(np.array(scores) - np.array(empirical_scores))
                    differences.append(diff)

            team_number = np.argmin(differences)
            if team_number == 0:
                team_number = 1
                print "%s (bowl score %i) appears to have no good fits." \
                    % (school, score)

            team_member_ids = set([id[:7] for id in ids if re.match('%s[0-9]{4}%i' % (school_id, team_number), id)])
            indivs = list(itertools.chain(*[test.testpaper_set.filter(mathlete__mao_id=id) \
                    for id in team_member_ids]))
            indivs =  sorted(indivs, key=lambda x : x.score, reverse=True)
            scores = [paper.score for paper in indivs]


            # in case of corrupted data, cap the size of a team
            # at four people
            if len(indivs) > 4:
                print "%s (team %i) tried to field more than 4 team members." \
                    % (school, team_number)
                coarse_attempt = indivs[-4:]
                try:
                    fine_attempt = []
                    while len(empirical_scores) > 0:
                        e_score = empirical_scores.pop(0)
                        j = scores.index(e_score)
                        scores.pop(j)
                        fine_attempt.append(indivs.pop(j))
                    indivs = fine_attempt
                    print "Succeeded in matching scores."
                except:
                    indivs = coarse_attempt
                    print "Failed in matching scores."

            if category is "States":
                indivs = test.testpaper_set \
                    .filter(mathlete__mao_id__startswith=str(school_id)) \
                    .order_by('-score')[:4]

            team = Team(
                school=school, 
                number=team_number,
                place=i+1,
                test=bowl_test,
                score=score)
            team.pre_save()
            team.indivs.add(*list(indivs))
            team.save()
        bowl_test.save()
        for team in Team.objects.filter(test=bowl_test):
            team.save_post_test()

        print "%s team data retrieved." % division

    competition.save()
    add_sweepstakes(competition)

def resolve_school_by_name(name):
    schools = list(School.objects.filter(name__iexact=name))
    if len(schools) > 1:
        'Resolving %s' % name
        ids = set([s.id_num for s in schools if s.id_num is not None])
        if len(ids) > 0:
            one_id =  list(ids)[0]
            new_s = School(name=name, id_num=one_id)
        else:
            new_s = School(name=name)

        new_s.save()

        for paper in TestPaper.objects.filter(school__in=schools):
            paper.school = new_s
            paper.save()

        for team in Team.objects.filter(school__in=schools):
            team.school = new_s
            team.save()

        for school in schools:
            school.delete()
        print 'Successfully resolved.'

def resolve_schools():
    for name in tqdm([s.name for s in School.objects.all()]):
        resolve_school_by_name(name)

if __name__ == "__main__":

    # states
    import_detail_report('State 2016',
        date=datetime.date(2016, 4, 16),
        name='States',
        category='States',
        topics=[
            ('Theta', '1T - Theta Functions'),
            ('Alpha', '1A - Analytic Geometry'),
            ('Mu', '1C - Calculus Applications'),
            ('Open', '1O - Statistics'),
            ('Theta', '2T - Logs & Exponents'),
            ('Alpha', '2A - Complex Numbers'),
            ('Mu', '2C - Limits & Derivatives'),
            ('Open', '2O - History Of Math'),
            ('Theta', '1T - Theta Applications'),
            ('Alpha', '1A - Trigonometry'),
            ('Mu', '1C - Integration'),
            ('Open', '1O - Gemini'),
            ('Theta', '2T - Geometry'),
            ('Alpha', '2A - Matrices & Vectors'),
            ('Mu', '2C - BC Calculus'),
            ('Theta', '1T - Quadrilaterals'),
            ('Alpha', '1A - Alpha Equations & Inequalities'),
            ('Mu', '1C - Sequences & Series'),
            ('Theta', '2T - Theta Equations & Inequalities'),
            ('Alpha', '2A - Alpha Applications'),
            ('Mu', '2C - Area & Volume'),
            ('Open', '2O - Probability'),
        ])

    import_detail_report('State 2015',
        date=datetime.date(2015, 4, 18),
        name='States',
        category='States',
        topics=[
            ('Theta', 'Theta Applications'),
            ('Alpha', 'Alpha Equations & Inequalities'),
            ('Mu', 'Area & Volume'),
            ('Open', 'Statistics'),
            ('Theta', 'Theta Logs & Exponents'),
            ('Alpha', 'Complex Numbers'),
            ('Mu', 'Integration'),
            ('Open', 'History of Math'),
            ('Theta', 'Theta Functions'),
            ('Alpha', 'Analytic Geometry'),
            ('Mu', 'Limits & Derivatives'),
            ('Open', 'Gemini'),
            ('Theta', 'Geometry'),
            ('Alpha', 'Matrices & Vectors'),
            ('Mu', 'Sequences & Series'),
            ('Theta', 'Circumference Perimeter Area & Volume'),
            ('Alpha', 'Trigonometry'),
            ('Mu', 'BC Calculus'),
            ('Theta', 'Theta Equations & Inequalities'),
            ('Alpha', 'Alpha Applications'),
            ('Mu', 'Calculus Applications'),
            ('Open', 'Probability')
        ])

    #2017 competitions -- without states

    import_detail_report('Combined03042017',
        date=datetime.date(2017, 3, 4),
        name='March Regional',
        category='Regional')

    import_detail_report('Palm Harbor Invitational February 2017',
        date-datetime.date(2017, 2, 18),
        name='Palm Harbor',
        category='Invite')

    import_detail_report('Combined02032017',
        date=datetime.date(2017, 2, 4),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined01202017',
        date=datetime.date(2017, 1, 21),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Chiles Invitational January 2017',
        date=datetime.date(2017, 1, 14),
        name='Chiles',
        category='Invite')

    # 2016 competitions -- without states

    import_detail_report('Palmetto Ridge Statewide March 2016',
        date=datetime.date(2016, 3, 19),
        name='Palmetto Ridge',
        category='Invite')

    import_detail_report('Combined03122016',
        date=datetime.date(2016,3,12),
        name='March Regional',
        category='Regional')

    import_detail_report('Sickles Statewide Feb 2016',
        date=datetime.date(2016, 2, 27),
        name='Sickles',
        category='Invite')

    import_detail_report('Combined02132016',
        date=datetime.date(2016, 2, 13),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined01292016',
        date=datetime.date(2016, 1, 29),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Vero Beach Statewide 2016',
        date=datetime.date(2016, 1, 16),
        name='Vero Beach',
        category='Invite')

    # 2015 competitions -- without states

    import_detail_report('Cypress Bay Statewide', 
        date=datetime.date(2015,3,21), 
        name='Cypress Bay', 
        category='Invite')

    import_detail_report('Combined03062015',
        date=datetime.date(2015, 3, 6),
        name='March Regional',
        category='Regional')

    import_detail_report('King High Statewide February 2015',
        date=datetime.date(2015, 2, 28),
        name='King',
        category='Invite')

    import_detail_report('Combined02142015',
        date=datetime.date(2015,2,14),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined01312015',
        date=datetime.date(2015,1,31),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Vero Beach Statewide Jan 2015',
        date=datetime.date(2015, 1, 17),
        name='Vero Beach',
        category='Invite')

    # 2014 competitions -- without states

    import_detail_report('Buchholz Invitational 3 15 14',
        date=datetime.date(2014, 3, 14),
        name='Buchholz',
        category='Invite')

    import_detail_report('Combined03012014',
        date=datetime.date(2014, 3, 1),
        name='March Regional',
        category='Regional')

    import_detail_report('February Statewide at Coral Glades HS',
        date=datetime.date(2014, 2, 15),
        name='Coral Glades',
        category='Invite')

    import_detail_report('Combined02012014',
        date=datetime.date(2014, 2, 1),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined01182014',
        date=datetime.date(2014, 1, 18),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Tampa Bay Tech January Statewide 2014',
        date=datetime.date(2014, 1, 11),
        name='Tampa Bay Tech',
        category='Invite')
 
    # 2013 competitions -- without states

    import_detail_report('Hagerty Student Delegate March Statewide',
        date=datetime.date(2013, 3, 16),
        name='Hagerty',
        category='Invite',
        is_150_scale=True)

    import_detail_report('Combined03022013',
        date=datetime.date(2013, 3, 2),
        name='March Regional',
        category='Regional',
        is_150_scale=True)
    
    import_detail_report('Tampa Bay Tech Statewide Feb  2013',
        date=datetime.date(2013, 2, 16),
        name='Tampa Bay Tech',
        category='Invite',
        is_150_scale=True)

    import_detail_report('Combined02012013',
        date=datetime.date(2013, 2, 2),
        name='Feb Regional',
        category='Regional',
        is_150_scale=True)

    import_detail_report('Combined01182013',
        date=datetime.date(2013, 1, 19),
        name='Jan Regional',
        category='Regional',
        is_150_scale=True)

    import_detail_report('Vero Beach January 2013',
        date=datetime.date(2013, 1, 12),
        name='Vero Beach',
        category='Invite',
        is_150_scale=True)

    # 2012 competitions -- without states

    import_detail_report('Buchholz Statewide March 2012',
        date=datetime.date(2012, 3, 17),
        name='Buchholz',
        category='Invite')

    import_detail_report('Combined03022012',
        date=datetime.date(2012, 3, 3),
        name='March Regional',
        category='Regional')

    import_detail_report('TBT 2012 Statewide',
        date=datetime.date(2012, 2, 18),
        name='Tampa Bay Tech',
        category='Invite')

    import_detail_report('Combined02032012',
        date=datetime.date(2012, 2, 4),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined01202012',
        date=datetime.date(2012, 1, 21),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Vero Beach Statewide - January 2012',
        date=datetime.date(2012, 1, 7),
        name='Vero Beach',
        category='Invite')

    # 2011 competitions -- without states

    import_detail_report('Hagerty Delegate Competition',
        date=datetime.date(2011, 12, 3),
        name='Hagerty',
        category='Invite')

    import_detail_report('Eastside Statewide Mail-in March 2011',
        date=datetime.date(2011, 3, 26),
        name='Eastside',
        category='Invite')

    import_detail_report('Combined03112011',
        date=datetime.date(2011, 3, 12),
        name='March Regional',
        category='Regional')

    import_detail_report('Seminole Statewide',
        date=datetime.date(2011, 2, 26),
        name='Seminole',
        category='Invite')

    import_detail_report('Combined02112011',
        date=datetime.date(2011, 2, 12),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined01272011',
        date=datetime.date(2011, 1, 29),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Palm harbor University Invitational Jan 2011',
        date=datetime.date(2011, 1, 15),
        name='Palm Harbor',
        category='Invite')

    # 2010 competitions -- without states

    ###they split up March Invite into two competitions??

    import_detail_report('Combined Regional Results - 3-13-2010',
        date=datetime.date(2010, 3, 13),
        name='March Regional',
        category='Regional')

    import_detail_report('Tiger Statewide Feb 27 2010',
        date=datetime.date(2010, 2, 27),
        name='Tiger',
        category='Invite')

    import_detail_report('Combined Regional Results - 2-13-2010',
        date=datetime.date(2010, 2, 13),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined Regional Results - 1-30-2010',
        date=datetime.date(2010, 1, 30),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Vero Beach Invitational 2010',
        date=datetime.date(2010, 1, 16),
        name='Vero Beach',
        category='Invite')

    # 2009 competitions -- without states

    import_detail_report('UF Blue Key Final  3-28-2009',
        date=datetime.date(2009, 3, 28),
        name='UF',
        category='Invite')

    import_detail_report('Combined Regional Results - 3-14-2009',
        date=datetime.date(2009, 3, 14),
        name='March Regional',
        category='Regional')

    import_detail_report('Ft Myers Invitational Feb 2009',
        date=datetime.date(2009, 2, 28),
        name='Ft Myers',
        category='Invite')

    import_detail_report('Combined Regional Results - 2-14-2009',
        date=datetime.date(2009, 2, 14),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Combined Regional Results - 1-31-2009',
        date=datetime.date(2009, 1, 31),
        name='Jan Regional',
        category='Regional')

    import_detail_report('Vero Beach Invitational January 2009',
        date=datetime.date(2009, 1, 17),
        name='Vero Beach',
        category='Invite')

    # 2008 competitions -- without states

    import_detail_report('FBK Invitational 2008',
        date=datetime.date(2008, 3, 22),
        name='FBK',
        category='Invite')

    import_detail_report('Combined Regional Results - 3-8-2008',
        date=datetime.date(2008, 3, 8),
        name='March Regional',
        category='Regional')

    import_detail_report('Florida Invitational at Middleton   February 23  2008',
        date=datetime.date(2008, 2, 23),
        name='Middleton',
        category='Invite') 

    import_detail_report('Combined Regional Results - 2-9-2008',
        date=datetime.date(2008, 2, 9),
        name='Feb Regional',
        category='Regional')

    import_detail_report('Ft Myers Invitational January 2008',
        date=datetime.date(2008, 1, 26),
        name='Ft Myers',
        category='Invite')

    import_detail_report('Combined Regional Results - 1-12-2008',
        date=datetime.date(2008, 1, 12),
        name='Jan Regional',
        category='Regional')









