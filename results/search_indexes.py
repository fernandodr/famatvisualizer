from haystack import indexes
from results.models import *


class MathleteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    mao_id = indexes.CharField(model_attr='mao_id')
    school = indexes.CharField(model_attr='school')

    def get_model(self):
        return Mathlete

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class SchoolIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    region = indexes.IntegerField(model_attr='region')
    id_num = indexes.IntegerField(model_attr='id_num')
    num_mathletes = indexes.IntegerField(model_attr='num_mathletes')

    def get_model(self):
        return School

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class CompetitionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    date = indexes.DateField(model_attr='date')
    name = indexes.CharField(model_attr='name')
    category = indexes.CharField(model_attr='category')

    def get_model(self):
        return Competition

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

class TestIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
#    competition = indexes.ForeignKey(model_attr='competition')
    division = indexes.CharField(model_attr='division')
    average = indexes.FloatField(model_attr='average')
    std = indexes.FloatField(model_attr='std')
    placing = indexes.FloatField(model_attr='placing')

    def get_model(self):
        return Test

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
















