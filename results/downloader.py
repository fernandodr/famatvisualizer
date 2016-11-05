from results.models import *
import datetime
import urllib2
import BeautifulSoup

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
    Competition.objects.all().delete()
    Mathlete.objects.all().delete()
    Test.objects.all().delete()
    TestPaper.objects.all().delete()
    Question.objects.all().delete()
    QuestionAnswer.objects.all().delete()
    School.objects.all().delete()

def import_detail_report(comp_name, date, name, category, divs=None, region=None):
        # if user does not provide divisions, use default
        if divs==None:
            divisions = ['Calculus', 'Statistics', 'Precalculus', 
                         'Algebra 2', 'Geometry', 'Algebra 1', 
                         'Theta', 'Alpha', 'Calculus 1', 'Calculus 2']
        else:
            divisions = divs
            
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
                    try:
                        cells = row.findChildren('td')
                        cells = [cell.text for cell in cells]
                        mao_id = other_rows[i].findChildren('td')[4].text[0:7]
                        try:
                            mathlete = Mathlete.objects.get(first_name=cells[3].title().split(' ')[0],
                                                            last_name =cells[3].title().split(' ')[1],
                                                            mao_id = mao_id)
                        except:
                            mathlete = Mathlete(first_name=cells[3].title().split(' ')[0],
                                                last_name=cells[3].title().split(' ')[1],
                                                mao_id = mao_id)
                            mathlete.save()
                        
                        try:
                            school = School.objects.get(name=cells[2])
                        except:
                            school = School(name=cells[2])
                            school.save()
                        
                        if region != None:
                            if school.region != region:
                                school.region = region
                                school.save()
                                                
                        paper = TestPaper(mathlete=mathlete, school=school, test=test, place=i+1)
                        paper.save()
                        
                        cells = cells[4:]
                        for j, answer in enumerate(cells):
                            qa = QuestionAnswer(paper=paper, question=questions[j], givenanswer=answer.strip('&nbsp;'))
                            qa.save()
                        paper.save()
                    except:
                        num_failures += 1
                test.save()
                for paper in TestPaper.objects.filter(test=test):
                    paper.save_post_test()
                print "%s (%i)" % (division, num_failures)
                    
           except:
                print '\t\t\t%s' % division

        competition.save()
   
wipe()

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


