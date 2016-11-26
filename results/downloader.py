import datetime
import urllib2
import BeautifulSoup
import re
import numpy as np
import itertools

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
        region=None):
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
    region : int or None
        If you are downloading a regional competition, say so.
    """

    # if user does not provide divisions, use default
    if divs==None:
        divisions = ['Calculus', 'Statistics', 'Precalculus', 
                     'Algebra 2', 'Geometry', 'Algebra 1', 
                     'Theta', 'Alpha', 'Calculus 1', 'Calculus 2']
    else:
        divisions = divs
    
    # fail loudly if this competition is already in the database    
    assert type(date) == datetime.date
    assert Competition.objects.filter(date=date).count() == 0
    competition = Competition(date=date, name=name, category=category)
    competition.save()

    print '\n%s' % comp_name
    
    for division in divisions:
        try:
            url = ('http://famat.org/Downloadable/Results/' + 
                   comp_name + "/" + division + "_Detail.html").replace(' ', '%20')
            raw_page = urllib2.urlopen(url)
            soup = BeautifulSoup.BeautifulSoup(raw_page)
            
            url = ('http://famat.org/Downloadable/Results/' + 
                   comp_name + "/" + division + "_Indv.html").replace(' ', '%20')
            raw_page = urllib2.urlopen(url)
            other_soup = BeautifulSoup.BeautifulSoup(raw_page)
        except:
            print '\t\t\t%s' % division
            continue
            
        test = Test(competition=competition, division=division)
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
                    school = School(name = user_input, num_id = int(school_id))
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
                        j = scores.find(e_score)
                        fine_attempt.append(indivs.pop(j))
                    indivs = fine_attempt
                    print "Succeeded in matching scores."
                except:
                    indivs = coarse_attempt
                    print "Failed in matching scores."

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


if __name__ == "__main__":
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

