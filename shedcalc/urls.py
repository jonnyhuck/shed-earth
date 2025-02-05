# from django.conf.urls import url
from django.urls import include, re_path
from . import views

app_name = 'shedcalc'

urlpatterns = [

	# eg: /shedcalc/
    re_path(r'^$', views.index, name='index'),

    # eg: /shedcalc/results/
    re_path(r'^results/$', views.calc, name='results'),

	# this gets the image chart of the samples
    # url(r'^samples.png$', views.samples_chart, name='samples')
]
