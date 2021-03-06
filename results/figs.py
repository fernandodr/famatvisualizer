# from models import *
# import matplotlib.pyplot as plt
# import seaborn as sns
# import mpld3
# from results.utils import *
# from mpld3 import plugins
# import datetime

# divs = ['Calculus', 'Statistics', 'Precalculus', 'Algebra 2', 'Geometry']

# def div_to_col(div):
#     current_pal = sns.color_palette()

#     if div.startswith('Calculus'):
#         return current_pal[0]
#     elif div=='Statistics':
#         return current_pal[1]
#     elif div=='Precalculus' or div=='Alpha':
#         return current_pal[2]
#     elif div=='Algebra 2' or div=='Theta':
#         return current_pal[3]
#     elif div=='Geometry':
#         return current_pal[4]
#     else:
#         return current_pal[5]

# def set_style():
#     sns.set_style('white')
#     plt.rcParams['axes.titlesize'] = 18
#     plt.rcParams['axes.labelsize'] = 14
#     plt.rcParams['figure.figsize']=(9,5.5)

def test_detail_report(test):
    return ""
#     # get the necessary data
#     num_questions = test.question_set.count()
#     num_people = test.testpaper_set.count()
#     rights, blanks, wrongs = [], [], []
#     for question in test.question_set.order_by('number'):
#         rights.append(100.0*question.num_correct/num_people)
#         blanks.append(100.0*question.num_blank/num_people)
#         wrongs.append(100.0*question.num_wrong/num_people)
#     print rights
#     print wrongs
#     print blanks
#     rights_and_blanks = [x+y for x,y in zip(rights, blanks)]

#     width = 0.7
#     ind = np.arange(1,num_questions+1)-width/2.
    
#     set_style()

#     fig, ax = plt.subplots(figsize=[10,22])
#     plt.ylim([0.5,num_questions+width])
#     plt.xlim([0,100])
#     p1 = plt.barh(ind, rights, width, color=sns.color_palette()[1], edgecolor='none', label='Right')
#     p2 = plt.barh(ind, blanks, width, color=sns.color_palette()[5], edgecolor='none', left=rights, label='Blank')
#     p3 = plt.barh(ind, wrongs, width, color=sns.color_palette()[2], edgecolor='none', left=rights_and_blanks,label='Wrong')
#     plt.ylabel('Questions')
#     plt.yticks(ind + width/2., ["Q"+str(i) for i in range(1,31)])
#     ax.xaxis.tick_top()
#     ax.invert_yaxis()
#     plt.xticks(np.arange(0, 101, 10))
#     plt.tight_layout()
#     fig_html = mpld3.fig_to_d3(fig)
#     plt.close()
#     return fig_html.replace("\n","\r").replace("var figwidth = 9.0 * 22","var figwidth = $(window).width()*.9;").replace("var figheight = 6.0 * 80","var figheight = $(window).height()*.9;")

def participation_over_time():
    return ""
#     set_style()
#     dates_r, names_r, num_mathletes_r, names_r = [], [], [], []
#     dates_i, names_i, num_mathletes_i = [], [], []

#     for c in Competition.objects.filter(category='Regional').order_by('date'):
#         dates_r.append(c.date)
#         n = len(TestPaper.objects.filter(test__competition=c))
#         names_r.append("%s\n(%i people)" % (str(c), n))
#         num_mathletes_r.append(n)

#     for c in Competition.objects.filter(category='Invite').order_by('date'):
#         dates_i.append(c.date)
#         n = len(TestPaper.objects.filter(test__competition=c))
#         names_i.append("%s\n(%i people)" % (str(c), n))
#         num_mathletes_i.append(n)

#     fig, ax = plt.subplots()
#     points_r = ax.plot(dates_r, num_mathletes_r, 'o-', label='Regionals')
#     points_i = ax.plot(dates_i, num_mathletes_i, 'o-', label='Invites')
#     plt.legend()

#     ax.set_xlabel('Date of Competition')
#     ax.set_ylabel('Total Number in Attendance')
#     ax.set_title('MAO Attendance Over Time')
#     ax.set_xlim((datetime.date(2013,1,1), datetime.date(2016,4,1)))

#     tooltip = plugins.PointHTMLTooltip(points_r[0], 
#         names_r,
#         voffset=10,
#         hoffset=10)
#     tooltip1 = plugins.PointHTMLTooltip(points_i[0], 
#         names_i,
#         voffset=10,
#         hoffset=10)

#     plugins.connect(fig, tooltip)
#     plugins.connect(fig, tooltip1)
#     fig_html = mpld3.fig_to_html(fig)
#     fig_html = fig_html.replace('None', '')
#     plt.close()
#     return fig_html

def difficulty_overall():
    return ""
#     set_style()

#     dates, labels, avgs, cols = [], [], [], []
#     for test in Test.objects.all():
#         dates.append(test.competition.date)
#         avgs.append(test.average)
#         cols.append(div_to_col(test.division))
#         labels.append("%s %s (%.2f) " %(str(test.competition),
#             test.division, avgs[-1]))
#     fig, ax = plt.subplots()
#     points = plt.plot(dates, avgs, 'o')
#     ax.set_xlim((datetime.date(2013,1,1), datetime.date(2016,4,1)))
#     ax.set_xlabel('Date of Competition')
#     ax.set_ylabel('Average Score on Test')
#     ax.set_title('Test Difficulty Over Time')
#     tooltip = plugins.PointHTMLTooltip(points[0],
#         labels,
#         voffset=10,
#         hoffset=10)
#     plugins.connect(fig, tooltip)
#     fig_html = mpld3.fig_to_html(fig)
#     plt.close()
#     return fig_html

def scores_over_time(mathlete):
    return ""
#     set_style()
#     fig, ax = plt.subplots()

#     for div in divs:
#         dts, scores, labels = [], [], []
#         for tp in TestPaper.objects.filter(mathlete=mathlete, test__division=div):
#             dts.append(tp.test.competition.date)
#             scores.append(tp.t_score)
#             labels.append("%s (%.2f)" % (str(tp.test.competition), scores[-1]))
#         points = plt.plot(dts, scores, 'o', label=div)
#         tooltip = plugins.PointHTMLTooltip(points[0],
#             labels,
#             voffset=10,
#             hoffset=10)
#         plugins.connect(fig, tooltip)
#     plt.legend(loc=0)
#     fig_html = mpld3.fig_to_html(fig)
#     fig_html = fig_html.replace('None', '')
#     plt.close()
#     return fig_html

def handling_difficulty(mathlete):
    return ""
#     def weighted_avg(x, smoothing=1.):
#         diffs = np.exp(-(x-srtd_props)**2/smoothing)
#         weighing = sum(diffs)
#         return (np.dot(srtd_res, diffs) / weighing)

#     def delta(x, levels=2):
#         if levels==0:
#             return sum(x)
#         else:
#             return delta(x[1:]-x[:-1], levels=levels-1)

#     set_style()
#     fig, ax = plt.subplots()
#     for year in [2013, 2014, 2015, 2016]:
#         diff_pairs = []
#         for qa in QuestionAnswer.objects.filter(paper__mathlete=mathlete,
#                 paper__test__competition__date__year=year):
#             q = qa.question
#             pct_right = q.num_correct*1.0/(q.num_correct + q.num_blank + q.num_wrong)
#             diff_pairs.append((pct_right, int(qa.is_right)))
#         if len(diff_pairs) > 0:
#             srtd_pairs = sorted(diff_pairs, key=lambda x : x[0])
#             srtd_pairs = np.array(srtd_pairs)
#             srtd_res = srtd_pairs[:,1]
#             srtd_props = srtd_pairs[:,0]

#             xs = np.arange(0,1,.01)

#             best_s = (0,10000)
#             for s in np.arange(0.001, 0.2, 0.001):
#                 avgs = np.array([weighted_avg(x, smoothing=s) for x in xs])
#                 val = delta(avgs)
#                 if val < best_s[1]:
#                     best_s = (s, val)

#             for s in [best_s[0]]:
#                 plt.plot(xs, [weighted_avg(x, smoothing=s) for x in xs], label=str(year), linewidth=3)
#     plt.xlim([0,1])
#     plt.ylim([0,1.1])
#     plt.title('Handling Difficulty')
#     plt.xlabel('Proportion of People Got Question Right')
#     plt.ylabel('Probability of getting it right')
#     plt.plot([0,1], [0,1], c='k', label='Average')
#     plt.legend(loc=0)
#     fig_html = mpld3.fig_to_html(fig)
#     fig_html = fig_html.replace('None', '')
#     plt.close()
#     return fig_html
    

def histogram_of_scores(mathlete):
    return ""
#     set_style()

#     fig, ax = plt.subplots()

#     scores = []
#     for tp in TestPaper.objects.filter(mathlete=mathlete):
#         scores.append(tp.score)

#     plt.hist(scores)
#     ax.set_xlabel('Score')
#     ax.set_ylabel('Frequency')
#     ax.set_title('Histogram of Scores')
#     fig_html = mpld3.fig_to_html(fig)
#     fig_html = fig_html.replace('None', '')
#     plt.close()
#     return fig_html



