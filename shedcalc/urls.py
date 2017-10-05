from django.conf.urls import url
from . import views

app_name = 'shedcalc'

urlpatterns = [

	# eg: /shedcalc/
    url(r'^$', views.index, name='index'),

    # eg: /shedcalc/results/
    url(r'^results/$', views.calc, name='results'),
    
    # this gets the image for GB Calibration Curve
    url(r'^chartgb.png$', views.chartGB, name='chart'),
    
    # this gets the image for PY Calibration Curve
    url(r'^chartpy.png$', views.chartPY, name='chart'),
    
	# this gets the image chart of the samples
    url(r'^samples.png$', views.samples_chart, name='samples')
]