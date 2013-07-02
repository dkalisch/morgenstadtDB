'''
Created on 11.12.2012

@author: hauck
'''
from MorgenstadtDB.database.models import *
from django.contrib import admin

#admin.site.register(application_level)
admin.site.register(author)
admin.site.register(bp_vars)
admin.site.register(bp_vars_def)
admin.site.register(best_practices)
admin.site.register(bp_actors)
admin.site.register(bp_criteria)
admin.site.register(bp_criteria_data)
admin.site.register(bp_milestones)
admin.site.register(cities)
admin.site.register(city_vars)
admin.site.register(city_vars_def)
admin.site.register(country)
admin.site.register(x_fact_fact)
admin.site.register(x_fact_sect)
admin.site.register(x_fact_bp)
admin.site.register(GIS)
admin.site.register(impact_factor_categories)
admin.site.register(impact_factors)
admin.site.register(impact_factor_vars)
admin.site.register(impact_factor_vars_def)
admin.site.register(interview_vars)
admin.site.register(interviews)
admin.site.register(region)
admin.site.register(sector_vars)
admin.site.register(sector_vars_def)
admin.site.register(sectors)
admin.site.register(soziomatrix)
admin.site.register(sub_region)
admin.site.register(dropdown_item)
admin.site.register(comments_fields)
