from django.conf.urls import url
from . import views

app_name = 'shedcalc'

urlpatterns = [

	# eg: /shedcalc/
    url(r'^$', views.index, name='index'),

    # eg: /shedcalc/results/
    url(r'^results/$', views.calc, name='results'),
    
    # this gets the image
    url(r'^chart.png$', views.chart, name='chart')
]