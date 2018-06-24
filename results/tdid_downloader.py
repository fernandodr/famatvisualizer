import re
import BeautifulSoup
import requests

from results.models import *


def construct_args_from_test(test):
    div_overrides = {
        'Algebra 2' : 'Algebra II'
    }
    
    
    assert (test.competition.category == 'Regional')
    return {'category': 'Regionals - %s' % test.competition.date.strftime('%B'),
       'style' : '(Individual)',
       'level': div_overrides.get(test.division, test.division),
       'year' : test.competition.date.strftime('%Y'),
       'qy' : True}

def soup_from_test(test):
    args = construct_args_from_test(test)
    r = requests.get('http://famat.org/PublicPages/TestArchive.aspx', params=args)
    soup = BeautifulSoup.BeautifulSoup(r.text)
    return soup

def extract_tdid_from_link(link):
    try:
        return int(re.findall('TDID=([0-9]{1,8})', link['href'])[0])
    except IndexError:
        return None

def download_regional_tdids():
    for test in Test.objects.all():
        if test.competition.category != 'Regional':
            continue
        
        soup = soup_from_test(test)
        tdids = {'Answers': [], 'Solutions': [], 'Test': []}
        for link in soup.findAll('a', href=True):
            if link.text in tdids.keys():
                tdid = extract_tdid_from_link(link)
                if tdid:
                    tdids[link.text].append(tdid)

        print test
        print tdids
        
        if len(tdids['Answers']) == 1 and not test.answers_tdid:
            test.answers_tdid = tdids['Answers'][0]
        if len(tdids['Solutions']) == 1 and not test.solns_tdid:
            test.solns_tdid = tdids['Solutions'][0]
        if len(tdids['Test']) == 1 and not test.test_tdid:
            test.test_tdid = tdids['Test'][0]

        test.save()

if __name__ == "__main__":
    
    download_regional_tdids()
