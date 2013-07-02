from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       #------ LOGIN/LOGOUT
                       url(r'^accounts/login/$',  'django.contrib.auth.views.login',name='login_view'),
                       url(r'^accounts/logout/$', 'MorgenstadtDB.database.views.logout_view', name='logout_view'),
                       
                       #------ CHANGE PASSWORD
                       url(r'^accounts/password/$', 'MorgenstadtDB.database.views.password_view', name='password_view'),
                       
                       #------ HOME
                       url(r'^$', 'MorgenstadtDB.database.views.home_view', name='home'),
                       
                       
                       #------ CITY
                       url(r'^city/(?P<city_id>\w+)/$', 'MorgenstadtDB.database.views.city_view', name='city'),
                       
                       #EDIT city vars
                       url(r'^city/(?P<city_id>\w+)/vars/$', 'MorgenstadtDB.database.views.city_var_view', name='city_var'),
                       
                       
                       #------- BESTPRACTICES
                       
                       #OVERVIEW bestpractices
                       url(r'^city/(?P<city_id>\w+)/bestpractice/$', 'MorgenstadtDB.database.views.bestpractice_view', name='bestpractice'),

                       #ADD new bestpractice
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/$', 'MorgenstadtDB.database.views.bestpractice_add_view', name='bestpractice_add'),
                       
                       #EDIT bestpractice
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/$', 'MorgenstadtDB.database.views.bestpractice_add_view', name='bestpractice_add'),
                       
                       
                       #-------BESTPRACTICE LEVELS
                                             
                       #-------BESTPRACTICE DESCRIPTION LEVEL
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/bestpracticeDescription/$', 'MorgenstadtDB.database.views.bestpractice_description_view', name='bestpractice_description'),
                       
                       #-------BESTPRACTICE DETAIL LEVEL
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/bestpracticeDetail/$', 'MorgenstadtDB.database.views.bestpractice_detail_view', name='bestpractice_detail'),

                       #-------BESTPRACTICE IMPACT LEVEL
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/bestpracticeImpact/$', 'MorgenstadtDB.database.views.bestpractice_impact_view', name='bestpractice_impact'),
                       
                       #-------IMPACTFACTORS
                       
                       #OVERVIEW impactfactors
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/impactfactor/$', 'MorgenstadtDB.database.views.impactfactor_view', name='impactfactor'),
                       
                       #ADD NEW impactfactor
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/impactfactor/add/$', 'MorgenstadtDB.database.views.impactfactor_add_view', name='impactfactor_add'),
                       
                       #EDIT impactfactor
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/impactfactor/add/(?P<impactfactor_id>[\w_\s]+)/$', 'MorgenstadtDB.database.views.impactfactor_add_view', name='impactfactor_add'),
                       
                       #IMPACT FACTOR INFO
                       url(r'^city/(?P<city_id>\w+)/bestpractice/add/(?P<bestpractice_id>[\w_\s]+)/impactfactor/add/(?P<impactfactor_id>[\w_\s]+)/info/$', 'MorgenstadtDB.database.views.impactfactor_info_view', name='impactfactor_info'),

                       
                       #-------INTERVIEWS
                       
                       #OVERVIEW interviews
                       url(r'^city/(?P<city_id>\w+)/interview/$', 'MorgenstadtDB.database.views.interview_view', name='interview'),
                      
                       #ADD NEW interview            
                       url(r'^city/(?P<city_id>\w+)/interview/add/$', 'MorgenstadtDB.database.views.interview_add_view', name='interview_add'),
                       
                       #EDIT interview          
                       url(r'^city/(?P<city_id>\w+)/interview/add/(?P<interview_id>[\w_\s]+)/$', 'MorgenstadtDB.database.views.interview_add_view', name='interview_add'),
                      
                      
                      #-----------SOZIOMATRIX
                      
                      #ADD NEW rating to Soziomatrix
                      url(r'^city/(?P<city_id>\w+)/interview/add/(?P<interview_id>[\w_\s]+)/soziomatrix/add/$', 'MorgenstadtDB.database.views.soziomatrix_add_view', name='soziomatrix_add'),
                      
                      #--------INTERVIEW VARIABLES
                      
                       #OVERVIEW interview variables
                       url(r'^city/(?P<city_id>\w+)/interview/(?P<interview_id>[\w_\s]+)/interviewVar/$', 'MorgenstadtDB.database.views.interview_var_view', name='interview_var'),
                       
                       #ADD NEW interview variable
                       url(r'^city/(?P<city_id>\w+)/interview/(?P<interview_id>[\w_\s]+)/interviewVar/add/$', 'MorgenstadtDB.database.views.interview_var_add_view', name='interview_var_add'),

                       #EDIT interview variable
                       url(r'^city/(?P<city_id>\w+)/interview/(?P<interview_id>[\w_\s]+)/interviewVar/(?P<interview_var_id>[\w_\s]+)/$', 'MorgenstadtDB.database.views.interview_var_add_view', name='interview_var_add'),


                       #--------SECTORS
                       
                       #EDIT sector variables
                       url(r'^city/(?P<city_id>\w+)/sector/(?P<sector_id>[\w_\s]+)/$', 'MorgenstadtDB.database.views.sector_add_view', name='sector_add'),
                       
                       
                       #--------ADMIN
                       url(r'^admin/', include(admin.site.urls)),
                       
                       
                       #--------MEDIA/UPLOADS
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 

urlpatterns+=url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
