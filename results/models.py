from django.db import models
from results.utils import *
from django.utils.functional import cached_property
from django.contrib.auth.models import User
import numpy as np

class Mathlete(models.Model):
    first_name = models.CharField(max_length = 30)
    last_name = models.CharField(max_length = 30)
    mao_id = models.CharField(max_length=10)
    avg_t = models.FloatField(blank=True, null=True)
    
    def __unicode__(self):
        return self.last_name + ', ' + self.first_name
    
    def _get_concatname(self):
        return self.last_name + self.first_name
    
    def get_absolute_url(self):
        return '/mathlete/%i' % self.pk

    def _get_avg_t_score(self):
        return np.average([x.t_score for x in self.testpaper_set.all() if x.t_score is not None])

    def _get_school(self):
        return self.testpaper_set.all().order_by('-test__competition__date')[0].school
    
    def get_years_active(self):
        return sorted(list(set([t.test.competition.date.year for t in self.testpaper_set.all()])))
    
    def get_years_active_str(self):
        yrs = self.get_years_active()
        if len(yrs) == 0:
            return ""
        preform = [[yrs.pop(0)]]
        for yr in yrs:
            if yr == preform[-1][-1]+1:
                if len(preform[-1]) == 1:
                    preform[-1].append(yr)
                else:
                    preform[-1][1] = yr
            else:
                preform.append([yr])
        def form(x):
            if len(x)==1: return str(x[0])
            else: return ("%i &mdash; %i" % (x[0], x[1]))

        strs = [form(x) for x in preform]
        return ', '.join(strs)

    def _get_full_name(self):
        return self.first_name + " " + self.last_name

    def _get_description(self):
        return "%s represented %s in %s. Throughout the span of %i competitions, %s maintained an average t-score of %.2f." % \
            (self._get_full_name(), self.school, self.get_years_active_str(),
                self.testpaper_set.count(), self.first_name, self._get_avg_t_score())

    title = property(_get_full_name)
    description = property(_get_description)
    school = property(_get_school)
    concatname = property(_get_concatname)

    def extra_save(self, *args, **kwargs):
        self.avg_t = self._get_avg_t_score(*args, **kwargs)
        super(Mathlete, self).save(*args, **kwargs)


class School(models.Model):
    name = models.CharField(max_length = 60)
    region = models.IntegerField(default=0)
    id_num = models.IntegerField(blank=True, null=True)
    num_mathletes = models.IntegerField(null=True, blank=True)
    
    def get_absolute_url(self):
        return '/schools/%i/' % self.id_num

    def _id_num(self):
        try:
            return int(self.testpaper_set.all()[0].mathlete.mao_id[:4])
        except:
            return None

    def _num_mathletes(self):
        tps = self.testpaper_set.all()
        mathletes = set([tp.mathlete for tp in tps])
        return len(mathletes)

    def extra_save(self, *args, **kwargs):
        self.id_num = self._id_num(*args, **kwargs)
        self.num_mathletes = self._num_mathletes(*args, **kwargs)
        super(School, self).save(*args, **kwargs)

    def _get_description(self):
        if "school" in self.name.lower():
            return self.name + " has a MAO club of " + str(self.num_mathletes) + " mathletes."
        else:
            return self.name + " is a school with a MAO club of " + str(self.num_mathletes) + " mathletes."

    title = property(lambda x: x.name)
    description = property(_get_description)
    def __unicode__(self):
        return self.name
    
class Competition(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=60)
    category = models.CharField(max_length = 30)
    
    def get_absolute_url(self):
        return '/competitions/%d/%s/%s/' % (self.date.year, 
            get_month_abbr(get_name_month(int(self.date.month))), self.category.lower())
    
    def __unicode__(self):
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
                'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
        if self.category in ['Regional', 'Invite']:
            return str(self.date.year) + ' ' + months[self.date.month-1] + ' ' + self.category
        else:
            return str(self.date.year) + self.name
        
class Test(models.Model):
    competition = models.ForeignKey(Competition)
    division = models.CharField(max_length = 30)
    average = models.FloatField(blank=True, null=True)
    std = models.FloatField(blank=True, null=True)
    placing = models.FloatField(blank=True, null=True)
    
    def _get_average(self):
        scores = [paper.score for paper in self.testpaper_set.all()]
        if len(scores) > 0:
            return np.mean(scores)
        else:
            return None
        
    def _get_std(self):
        scores = [paper.score for paper in self.testpaper_set.all()]
        if len(scores) > 0:
            return np.std(scores)
        else:
            return None
    
    def _get_placing(self):
        if self.testpaper_set.count() <= 25:
            try:
                return min([paper.score for paper in self.testpaper_set.all()])
            except:
                return None
        else:
            return self.testpaper_set.order_by('-score')[24].score
    
    def get_absolute_url(self):
        return '/competitions/%d/%s/%s/%s/' % (self.competition.date.year, 
            get_month_abbr(get_name_month(int(self.competition.date.month))), 
            self.competition.category.lower(), get_division_abbr(self.division))
    
    def __unicode__(self):
        division_abbr = {'Calculus': 'Calc', 'Precalculus': 'Precal', 'Statistics': 'Stats',
                        'Algebra 2': 'Alg 2', 'Geometry': 'Geo'}
        return str(self.competition) + ': ' + division_abbr.get(self.division,self.division) + ' Indiv'

    def save(self, *args, **kwargs):
        self.average = self._get_average()
        self.std = self._get_std()
        self.placing = self._get_placing()
        super(Test, self).save(*args, **kwargs)

class TopicTest(Test):
    topic = models.CharField(max_length=30)
    
class Question(models.Model):
    test = models.ForeignKey(Test)
    number = models.IntegerField()
    answer = models.CharField(max_length=5)
    num_correct = models.IntegerField(blank=True, null=True)
    num_blank = models.IntegerField(blank=True, null=True)
    num_wrong = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return '%s: Question #%i' % (self.test, self.number)

    def save(self, *args, **kwargs):
        self.num_correct = len(self.questionanswer_set.filter(points=4))
        self.num_blank = len(self.questionanswer_set.filter(points=0))
        self.num_wrong = len(self.questionanswer_set.filter(points=-1))
        super(Question, self).save(*args, **kwargs)


class TestPaper(models.Model):
    mathlete = models.ForeignKey(Mathlete)
    school = models.ForeignKey(School)
    test = models.ForeignKey(Test)
    place = models.IntegerField(blank=True)
    score = models.IntegerField(blank=True)
    right = models.IntegerField(blank=True)
    blank = models.IntegerField(blank=True)
    wrong = models.IntegerField(blank=True)
    first_wrong = models.IntegerField(blank=True, null=True)
    t_score = models.FloatField(blank=True, null=True)
    s_score = models.FloatField(blank=True, null=True)
    
    def __unicode__(self):
        return str(self.mathlete)

    def _get_score(self):
        #return np.sum([qa.points for qa in QuestionAnswer.objects.filter(paper=self)])
        return np.sum([qa.points for qa in self.questionanswer_set.all()])
    
    def _first_wrong(self):
        for i in range(1,31):
            try:
                if not self.questionanswer_set.get(question__number=i).is_right():
                    return i
            except:
                pass
        return None

    def _get_t_score(self):
        try:
            return 50.0 + 10.0*(self.score - self.test.average)/(self.test.std)
        except:
            return None

    def _get_s_score(self):
        twenty_fifth = self.test.testpaper_set.order_by('place')[24].score
        tenth = self.test.testpaper_set.order_by('place')[9].score

        numerator = self.score - twenty_fifth
        denominator = tenth - twenty_fifth
        if denominator < 1: denominator = 1

        return 5.0*numerator/denominator + 70

    
    def save(self, *args, **kwargs):
        self.score = np.sum([qa.points for qa in self.questionanswer_set.all()])
        self.right = len(self.questionanswer_set.filter(points=4))
        self.blank = len(self.questionanswer_set.filter(points=0))
        self.wrong = len(self.questionanswer_set.filter(points=-1))
        self.first_wrong = self._first_wrong(*args, **kwargs)
        super(TestPaper, self).save(*args, **kwargs)

    def save_post_test(self, *args, **kwargs):
        self.s_score = self._get_s_score(*args, **kwargs)
        self.t_score = self._get_t_score(*args, **kwargs)
        super(TestPaper, self).save(*args, **kwargs)

    class Meta:
        ordering = ['place']


class QuestionAnswer(models.Model):
    paper = models.ForeignKey(TestPaper)
    question = models.ForeignKey(Question)
    givenanswer = models.CharField(max_length=1)
    points = models.IntegerField(blank=True, null=True)
    
    def _get_points(self):
        if self.question.answer == 'ABCDE':
            return 4
        elif self.givenanswer == 'X' or self.givenanswer == '':
            return 0
        elif self.question.answer.upper().find(self.givenanswer) != -1:
            return 4
        else:
            return -1
      
    def save(self, *args, **kwargs):
        # if len(self.question.answer) >= 1:
        #     self.points = self._get_points()
        super(QuestionAnswer, self).save(*args, **kwargs)
    
    def is_right(self):
        if self.points == 4:
            return True
        return False
    
    def is_blank(self):
        if self.points == 0:
            return True
        return False
    
    def is_wrong(self):
        if self.points == -1:
            return True;
        return False

class BowlTest(models.Model):
    competition = models.ForeignKey(Competition)
    division = models.CharField(max_length = 30)
    average = models.FloatField(blank=True, null=True)
    std = models.FloatField(blank=True, null=True)
    
    def _get_average(self):
        scores = [team.total_score for team in self.team_set.all()]
        if len(scores) > 0:
            return np.mean(scores)
        else:
            return None
        
    def _get_std(self):
        scores = [team.total_score for team in self.team_set.all()]
        if len(scores) > 0:
            return np.std(scores)
        else:
            return None
    
    def get_absolute_url(self):
        return '/competitions/%d/%s/%s/%s/bowl' % (self.competition.date.year, 
            get_month_abbr(get_name_month(int(self.competition.date.month))), 
            self.competition.category.lower(), get_division_abbr(self.division))
    
    def __unicode__(self):
        division_abbr = {'Calculus': 'Calc', 'Precalculus': 'Precal', 'Statistics': 'Stats',
                        'Algebra 2': 'Alg 2', 'Geometry': 'Geo'}
        return str(self.competition) + ': ' + division_abbr.get(self.division,self.division) + ' Team'

    def save(self, *args, **kwargs):
        self.average = self._get_average()
        self.std = self._get_std()
        super(BowlTest, self).save(*args, **kwargs)

class Team(models.Model):
    school = models.ForeignKey(School)
    number = models.IntegerField()
    indivs = models.ManyToManyField(TestPaper)
    test = models.ForeignKey(BowlTest)
    score = models.IntegerField()
    place = models.IntegerField()
    total_score = models.IntegerField(null=True, blank=True)
    t_score = models.FloatField(blank=True, null=True)

    def __unicode__(self):
        division_abbr = {'Calculus': 'Calc', 'Precalculus': 'Precal', 'Statistics': 'Stats',
                        'Algebra 2': 'Alg 2', 'Geometry': 'Geo'}
        return "%s's %s %s Team %i" (self.school, self.competition, 
            division_abbr.get(self.division,self.division),
            self.number)

    def _get_total_score(self):
        if self.indivs.all().exists():
            return self.score + sum([indiv.score for indiv in self.indivs.all()])
        else:
            return self.score

    def _get_mathletes(self):
        return [indiv.mathlete for indiv in self.indivs.all()]

    def _get_t_score(self):
        try:
            return 50.0 + 10.0*(self.total_score - self.test.average)/(self.test.std)
        except:
            return None

    def pre_save(self, *args, **kwargs):
        super(Team, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.total_score = self._get_total_score()
        super(Team, self).save(*args, **kwargs)

    def save_post_test(self, *args, **kwargs):
        self.t_score = self._get_t_score()
        super(Team, self).save(*args, **kwargs)

    mathletes = property(_get_mathletes)

    
class MathleteImpression(models.Model):
    mathlete = models.ForeignKey(Mathlete)
    user = models.ForeignKey(User)
    datetime = models.DateTimeField(auto_now_add=True)

    
