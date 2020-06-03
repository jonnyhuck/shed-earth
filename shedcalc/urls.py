from django.conf.urls import url
from . import views

app_name = 'shedcalc'

urlpatterns = [

	# eg: /shedcalc/
    url(r'^$', views.index, name='index'),

    # eg: /shedcalc/results/
    url(r'^results/$', views.calc, name='results'),

	# this gets the image chart of the samples
    url(r'^samples.png$', views.samples_chart, name='samples')
]
