from django.contrib import admin
from django.urls import include,path
from django.conf.urls import url 
from .views import HomeViewScale, get_data_scale, ChartDataScale, HomeViewSleep, get_data_sleep, ChartDataSleep, HomeViewWatch, get_data_watch, ChartDataWatch, HomeViewSummary, get_data_summary, ChartDataSummary


urlpatterns = [
	url(r'^$', HomeViewSummary.as_view(), name='summary'),
    url(r'^api/data/$', get_data_summary, name='summary-api-data'),
    url(r'^api/summary/data/$', ChartDataSummary.as_view(), name='summary-chart-data'), 
       	
    url(r'^scale/', HomeViewScale.as_view(), name='scale-home'),
    url(r'^api/data/$', get_data_scale, name='scale-api-data'),
    url(r'^api/scale/data/$', ChartDataScale.as_view(), name='scale-chart-data'),

    url(r'^sleep/', HomeViewSleep.as_view(), name='sleep-home'),
    url(r'^api/data/$', get_data_sleep, name='sleep-api-data'),
    url(r'^api/sleep/data/$', ChartDataSleep.as_view(), name='sleep-chart-data'),

    url(r'^watch/', HomeViewWatch.as_view(), name='watch-home'),
    url(r'^api/data/$', get_data_watch, name='watch-api-data'),
    url(r'^api/watch/data/$', ChartDataWatch.as_view(), name='watch-chart-data'),

    url(r'^admin/', admin.site.urls),

]
