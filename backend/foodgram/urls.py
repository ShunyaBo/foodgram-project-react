from django.contrib import admin
from django.urls import include, path


admin.site.site_header = 'Foodgram administration'
admin.site.site_title = 'FG'
admin.site.index_title = 'Welcome, friend!'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api', include('api.urls', namespace='api')),
]

# handler404 = 'core.views.page_not_found'
