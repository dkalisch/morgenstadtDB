from django.contrib.auth.models import User
from django.db import models

#author class extends the User
class author(models.Model):
    author_name = models.CharField(max_length=50)
    information = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=30, blank=True, null=True)
    adress = models.TextField(blank=True, null=True)
    picture = models.FileField(upload_to='interview_data/%Y_%m_%d', blank=True, null=True)
    sector_id = models.TextField(blank=True, null=True)
    city_id = models.TextField(blank=True, null=True)
    
    #ForeignKeys
    user = models.ForeignKey(User, unique=True)
    
    def __unicode__(self):
        return unicode(self.author_name)
    
    """class Meta:
        permissions = (
            ("isAuthor", "The user is an author, not a partner."),
        )"""
        
class country(models.Model):
    cc_iso = models.CharField(max_length=2, primary_key=True)
    tld = models.CharField(max_length=3)
    country_name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return unicode(self.country_name)
    
    class Meta():
        verbose_name_plural= "countries"
        
class sub_region(models.Model):
    sub_region_code=models.CharField(max_length=2, primary_key=True)
    sub_region_name=models.CharField(max_length=20)
    
    def __unicode__(self):
        return unicode(self.sub_region_name)
    
    class Meta():
        verbose_name= "sub region"
    
class region(models.Model):
    region_code = models.IntegerField(primary_key=True)
    region_name = models.CharField(max_length=10)
    
    def __unicode__(self):
        return unicode(self.region_name)
        
class cities(models.Model):
    city_name = models.CharField(max_length=50, verbose_name="Name") 
    city_lat = models.FloatField(blank=True, null=True)
    city_long = models.FloatField(blank=True, null=True)
    elevation = models.IntegerField(blank=True, null=True)
    adm1_code = models.IntegerField(blank=True, null=True)
    metropolitan_area = models.IntegerField(blank=True, null=True)
    full_name = models.CharField(max_length=50, blank=True, null=True) 
    diff_UTC = models.CharField(max_length=5, blank=True, null=True)
    insert_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    cc_iso = models.ForeignKey(country, blank=True, null=True)
    region_code = models.ForeignKey(region, blank=True, null=True)
    sub_region_code = models.ForeignKey(sub_region, blank=True, null=True)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.city_name)

    class Meta():
        verbose_name= "city"
        verbose_name_plural= "cities"
        
class city_vars_def(models.Model):
    var_name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.IntegerField(blank=True, null=True)
    isGlobal = models.BooleanField(default=True)
    encoding = models.CharField(max_length = 20)
    insert_time = models.DateTimeField()
    
    #ForeignKeys
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.var_name)
    
    class Meta():
        verbose_name= "city variable definition"
        
class city_vars(models.Model):
    value=models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='city_var_data/%Y_%m_%d', blank=True, null=True)
    year = models.CharField(max_length=4)
    source = models.TextField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    city_id=models.ForeignKey(cities)
    city_vars_def_id = models.ForeignKey(city_vars_def)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')    
    
    def __unicode__(self):
        return unicode(self.city_vars_def_id.var_name)+" in "+unicode(self.city_id.city_name)

    class Meta():
        verbose_name= "city variable"
        ordering = ['city_vars_def_id__insert_time']
    
class sectors(models.Model):
    sector_name = models.CharField(max_length=50)
    sector_desc = models.TextField()
    insert_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.sector_name)
    
    def get_id_as_string(self):
        return "|"+str(self.id)+"|"
    
    class Meta():
        verbose_name= "sector"
    
class sector_vars_def(models.Model):
    var_name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.IntegerField(blank=True, null=True)
    isGlobal = models.BooleanField(default=True)
    encoding = models.CharField(max_length=20)
    insert_time = models.DateTimeField()

    #ForeignKeys
    insert_by = models.ForeignKey(author, related_name='+')
    sector_id = models.ForeignKey(sectors)   
    
    def __unicode__(self):
        return unicode(self.var_name)+": "+unicode(self.description)
    
    class Meta():
        verbose_name= "sector variable definition"
    
class sector_vars(models.Model):
    value= models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='sector_var_data/%Y_%m_%d', blank=True, null=True)
    year = models.CharField(max_length=4)
    source = models.TextField()
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)

    #ForeignKeys
    sector_vars_def_id = models.ForeignKey(sector_vars_def)
    city_id = models.ForeignKey(cities)
    sector_id = models.ForeignKey(sectors)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')   
    

    def __unicode__(self):
        return unicode(self.sector_vars_def_id.var_name)+" in "+unicode(self.sector_id.sector_name)

    class Meta():
        verbose_name= "sector variable"
        ordering = ['sector_vars_def_id__insert_time']
    
class best_practices(models.Model):
    bp_name = models.CharField(max_length=50)
    bp_desc = models.TextField(blank=True, null=True)
    sectors= models.TextField()
    planning_phase = models.BooleanField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    idea_date = models.DateField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    city_id = models.ForeignKey(cities)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by= models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.bp_name)
    
    class Meta():
        verbose_name= "best practice"
    
class bp_vars_def(models.Model):
    var_name = models.CharField(max_length=200)
    description = models.TextField()    
    category = models.IntegerField(blank=True, null=True)
    isGlobal = models.BooleanField(default=True)
    encoding = models.CharField(max_length=20)
    insert_time = models.DateTimeField()

    #ForeignKeys
    insert_by = models.ForeignKey(author, related_name='+')   
    
    def __unicode__(self):
        return unicode(self.var_name)+": "+unicode(self.description)
    
    class Meta():
        verbose_name= "best practice variable definition"
    
class bp_vars(models.Model):
    value = models.TextField(blank=True)
    file = models.FileField(upload_to='bp_var_data/%Y_%m_%d', blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    bp_vars_def_id = models.ForeignKey(bp_vars_def)
    best_practice_id = models.ForeignKey(best_practices)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.bp_vars_def_id.var_name)+" in "+unicode(self.best_practice_id.bp_name)
    
    class Meta():
        verbose_name= "best practice variable"
        ordering = ['bp_vars_def_id__insert_time']
        
class bp_actors(models.Model):
    actor_name = models.CharField(max_length=50, blank=True, null=True)
    actor_desc = models.TextField(blank=True, null=True)
    classification = models.CharField(max_length=50, blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    CLASSIFICATION_CHOICES = {
            "1": 'Initiator',
            "2": 'Beschliessendes Gremium',
            "3": 'Durchfuehrer',
            "4": 'Finanzierer',
            "5": 'Nutzer',
            "6": 'Weiterer Akteur',
            }
    
    #ForeignKeys
    best_practice_id = models.ForeignKey(best_practices)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        if self.actor_name:
            return unicode(self.actor_name)
        return "unnamed"
    
    class Meta():
        verbose_name= "best practice actor"
        
class bp_milestones(models.Model):
    milestone_desc = models.TextField()
    milestone_date = models.DateField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    best_practice_id = models.ForeignKey(best_practices)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
        
    def __unicode__(self):
        return unicode(self.milestone_date)+": "+unicode(self.milestone_desc)
    
    class Meta():
        verbose_name= "best practice milestone"
    
class bp_criteria(models.Model):
    bp_criteria_name = models.CharField(max_length=50)
    unit = models.TextField(blank=True, null=True)
    value_source = models.TextField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    best_practice_id = models.ForeignKey(best_practices)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')

    def __unicode__(self):
        name = unicode(self.bp_criteria_name)
        
        if not name:
            name="Undefined BP_Criterion"

        return name+" in "+self.best_practice_id.bp_name
    
    class Meta():
        verbose_name= "best practice criterion"
        verbose_name_plural= "best practice criteria"

class bp_criteria_data(models.Model):
    criteria_value = models.TextField(blank=True, null=True)
    criteria_date = models.DateField(blank=True, null=True)
    criteria_count = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    bp_criteria_id = models.ForeignKey(bp_criteria)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')

    def __unicode__(self):
        return unicode(self.bp_criteria_id.bp_criteria_name)+': '+unicode(self.criteria_value)
    
    class Meta():
        verbose_name= "best practice criteria data"
        verbose_name_plural= "best practice criteria data" 
    
class impact_factor_categories(models.Model):
    category_name = models.CharField(max_length=50)
    category_desc = models.TextField(blank=True, null=True)    
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.category_name)
    
    class Meta():
        verbose_name= "impact factor category"
        verbose_name_plural= "impact factor categories"
    
class impact_factors(models.Model):
    impact_factor_name = models.CharField(max_length=50)
    impact_factor_desc = models.TextField(blank=True, null=True)
    classification = models.CharField(max_length=50)
    t_plan= models.DateField(blank=True, null=True)
    t_implementation = models.DateField(blank=True, null=True)
    t_impact = models.DateField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    impact_factor_category_id = models.ForeignKey(impact_factor_categories, blank=True, null=True)
    city_id = models.ForeignKey(cities, blank=True, null=True)
    best_practice_id = models.TextField(blank=True, null=True)
    sector_id = models.ForeignKey(sectors, blank=True, null=True)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.impact_factor_name)
    
    class Meta():
        verbose_name= "impact factor"
        
class impact_factor_vars_def(models.Model):
    var_name = models.CharField(max_length=200)
    description = models.TextField()
    isGlobal = models.BooleanField(default=True)
    encoding = models.CharField(max_length=20)
    category = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField()

    #ForeignKeys
    insert_by = models.ForeignKey(author, related_name='+')   
    
    def __unicode__(self):
        return unicode(self.var_name)+": "+unicode(self.description)
    
    class Meta():
        verbose_name= "impact factor variable definition"
    
class impact_factor_vars(models.Model):
    value= models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='impact_factor_var_data/%Y_%m_%d', blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    impact_factor_vars_def_id = models.ForeignKey(impact_factor_vars_def)
    impact_factors_id = models.ForeignKey(impact_factors)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.impact_factor_vars_def_id.var_name)+" in "+unicode(self.impact_factors_id.impact_factor_name)
    
    class Meta():
        verbose_name= "impact factor variable"
        ordering = ['impact_factor_vars_def_id__insert_time']
        
class interviews(models.Model):
    person = models.CharField(max_length=50)
    institution = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    txtData=models.FileField(upload_to='interview_data/%Y_%m_%d', blank=True, null=True)
    audioData=models.FileField(upload_to='interview_data/%Y_%m_%d', blank=True, null=True)
    interview_date = models.DateField(blank=True, null=True)
    authors_present = models.TextField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    city_id = models.ForeignKey(cities)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return "Interview with "+unicode(self.person)+" from "+unicode(self.institution)+"."
    
    class Meta():
        verbose_name= "interview"
    
class interview_vars(models.Model):
    key = models.CharField(max_length=50)
    value = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='interview_data/interview_vars/%Y_%m_%d', blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    city_id = models.ForeignKey(cities, blank=True, null=True)
    sector_id = models.ForeignKey(sectors, blank=True, null=True)
    best_practice_id = models.ForeignKey(best_practices, blank=True, null=True)
    factor_id = models.ForeignKey(impact_factors, blank=True, null=True)
    interview_id = models.ForeignKey(interviews)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        return unicode(self.key)+": "+unicode(self.value)

    class Meta():
        verbose_name= "interview variable"
        
class soziomatrix(models.Model):
    person_rated =models.CharField(max_length=50, blank=True, null=True)
    value = models.FloatField(blank=True, null=True)
    importance = models.FloatField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    interview_id = models.ForeignKey(interviews)
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')

    def __unicode__(self):
        return "Person rated: "+unicode(self.person_rated)

    class Meta():
        verbose_name_plural= "soziomatrices"
        
class x_fact_fact(models.Model):
    impact = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    impact_factor_id1 = models.ForeignKey(impact_factors, related_name='+')
    impact_factor_id2 = models.ForeignKey(impact_factors, related_name='+')
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        impactfactor1=self.impact_factor_id1.impact_factor_name
        impactfactor2=self.impact_factor_id2.impact_factor_name

        return "Impact of "+unicode(impactfactor1)+" on "+unicode(impactfactor2)+": "+unicode(self.impact)

    class Meta():
        verbose_name= "x_impactFactor_impactFactor"
        verbose_name_plural= "x_impactFactor_impactFactor"

class x_fact_sect(models.Model):
    impact = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    impact_factor_id = models.ForeignKey(impact_factors, related_name='+')
    sector_id = models.ForeignKey(sectors, related_name='+')
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        impactfactor=self.impact_factor_id.impact_factor_name
        sector=self.sector_id.sector_name

        return "Impact of "+unicode(impactfactor)+" on "+unicode(sector)+": "+unicode(self.impact)

    class Meta():
        verbose_name= "x_impactFactor_sector"
        verbose_name_plural= "x_impactFactor_sector"
        
class x_fact_bp(models.Model):
    impact = models.IntegerField(blank=True, null=True)
    insert_time = models.DateTimeField()
    update_time = models.DateTimeField(blank=True, null=True)
    
    #ForeignKeys
    impact_factor_id = models.ForeignKey(impact_factors, related_name='+')
    best_practice_id = models.ForeignKey(best_practices, related_name='+')
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')   
    insert_by = models.ForeignKey(author, related_name='+')
    
    def __unicode__(self):
        impactfactor=self.impact_factor_id.impact_factor_name
        bestpractice=self.best_practice_id.bp_name

        return "Impact of "+unicode(impactfactor)+" on "+unicode(bestpractice)+": "+unicode(self.impact)

    class Meta():
        verbose_name= "x_impactFactor_bestPractice"
        verbose_name_plural= "x_impactFactor_bestPractice"

class dropdown_item(models.Model):
    dropdown_id = models.IntegerField()
    name = models.CharField(max_length=50, blank=True, null=True)
    value = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    insert_time=models.DateTimeField()
    
    #ForeignKeys
    insert_by = models.ForeignKey(author)
    
        
    def __unicode__(self):
        return "Dropdown-item \""+unicode(self.name)+"\" in Dropdown number "+unicode(self.dropdown_id)

    class Meta():
        verbose_name= "Dropdown item"
        

class comments_fields(models.Model):
    table_name = models.CharField(max_length=100)
    table_field = models.TextField()
    table_id = models.IntegerField()
    source = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    update_time=models.DateTimeField(blank=True, null=True)
    insert_time=models.DateTimeField()
    
    #ForeignKeys
    insert_by = models.ForeignKey(author, related_name='+')
    update_by = models.ForeignKey(author, blank=True, null=True, related_name='+')
    
    def __unicode__(self):
        return 'Comment on Entry-ID: "'+unicode(self.table_id)+'", in Table: "'+unicode(self.table_name)+'", Field: "'+unicode(self.table_field)+'".'

    class Meta():
        verbose_name= "Comment Field"
        verbose_name_plural = "Comments Fields"
    
class GIS(models.Model):
    key = models.CharField(max_length=50, null=True, blank=True)
    geometry = models.TextField(null=True, blank=True)
    insert_time = models.DateTimeField()
    
    #ForeignKeyss
    city_id = models.ForeignKey(cities)
    
    def __unicode__(self):
        return unicode(self.key)
        
    class Meta():
        verbose_name_plural= "GIS"
