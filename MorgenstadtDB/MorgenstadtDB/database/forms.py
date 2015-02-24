'''
Created on 19.12.2012

@author: hauck
'''

from MorgenstadtDB.database.models import sectors, sector_vars, x_fact_fact, \
    bp_vars, city_vars_def, bp_vars_def, bp_milestones, best_practices, bp_criteria, \
    bp_criteria_data, bp_actors, impact_factors, x_fact_bp, x_fact_sect, cities, \
    city_vars, soziomatrix, interviews, dropdown_item, author, sector_vars_def, \
    impact_factor_vars_def, impact_factor_categories, comments_fields
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.models import ModelForm
from operator import itemgetter


class CityInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CityInputForm, self).__init__(*args, **kwargs)
        self.fields['city_lat'] = forms.FloatField(required=False)
        self.fields['city_lat'].label = "City Latitude"

        self.fields['city_long'] = forms.FloatField(required=False)
        self.fields['city_long'].label = "City Longitude"

        self.fields['elevation'] = forms.IntegerField(required=False)
        self.fields['elevation'].label = "Elevation"

        self.fields['adm1_code'] = forms.IntegerField(required=False)
        self.fields['adm1_code'].label = "ADM1 Code"

        self.fields['metropolitan_area'] = forms.IntegerField(required=False)
        self.fields['metropolitan_area'].label = "Metropolitan Area"

        self.fields['full_name'] = forms.CharField(max_length=50, required=False)
        self.fields['full_name'].label = "Full Name"

        self.fields['diff_UTC'] = forms.CharField(max_length=50, required=False)
        self.fields['diff_UTC'].label = "Difference to UTC"

        class Meta():
            model=cities
            fields = ('full_name', 'adm1_code', 'elevation', 'metropolitan_area', 'city_lat', 'city_long', 'diff_UTC', )
    

class InterviewInputForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        super(InterviewInputForm, self).__init__(*args, **kwargs)
        QUERYSET = author.objects.filter(city_id__icontains = '|'+str(self.instance.city_id.id)+'|')
        
        self.fields['person'] = forms.CharField(max_length=50)
        self.fields['person'].label = "Interviewed Person"
        self.fields['person'].widget.attrs['class'] = 'person_typeahead'
        self.fields['person'].widget.attrs['autocomplete'] = 'off'

        self.fields['institution'] = forms.CharField(max_length=50, required=False)
        self.fields['institution'].label = "Institution the Person works for (optional)"
        self.fields['institution'].widget.attrs['class'] = 'institution_typeahead'
        self.fields['institution'].widget.attrs['autocomplete'] = 'off'
        
        self.fields['position'] = forms.CharField(max_length=50, required=False)
        self.fields['position'].label = "Position the Person has in the Institution (optional)"
        
        self.fields['interview_date']=forms.DateField(widget=SelectDateWidget(years=range(2020, 1940, -1)))
        self.fields['interview_date'].label= "The date of the Interview"
        
        self.fields['authors_present'] = forms.ModelMultipleChoiceField(queryset=QUERYSET)
        self.fields['authors_present'].label = "The following Authors were present at the Interview (for multiple selection hold down ctrl)"
        
        self.fields['txtData']=forms.FileField(required=False)
        self.fields['txtData'].label = "Upload a text-file (optional)"

        self.fields['audioData']=forms.FileField(required=False)
        self.fields['audioData'].label = "Upload an audio-file (optional)"
        
        class Meta():
            model=interviews
            fields = ('person', 'institution', 'position', 'interview_date', 'authors_present', 'txtData', 'audioData', )
    
class InterviewVarInputForm(ModelForm):    
    key = forms.CharField(max_length=50)
    key.label = "Key of the Interview Variable"
    
    value = forms.CharField(widget=forms.Textarea, required=False)
    value.label = "Value of the Interview Variable (optional)"
    
    file = forms.FileField(widget=forms.ClearableFileInput, required=False)
    file.label="Upload data (optional)"
    
    sector_id = forms.ModelChoiceField(queryset=sectors.objects.all(), required=False)
    sector_id.label = "The information in this variable concerns the following Sector (optional)"
    
    best_practice_id = forms.ModelChoiceField(queryset=best_practices.objects.all(), required=False)
    best_practice_id.label = "The information in this variable concerns the following Best Practice (optional)"

    factor_id = forms.ModelChoiceField(queryset=impact_factors.objects.all(), required=False)
    factor_id.label = "The information in this variable concerns the following Impact Factor (optional)"
    
class SoziomatrixInputForm(ModelForm):    
    def __init__(self, *args, **kwargs):
        super(SoziomatrixInputForm, self).__init__(*args, **kwargs)
        person_rated = forms.CharField(required=True)
        value = forms.FloatField(required=True)
        importance = forms.FloatField(required=True)
        
        #set css-class and css-autocomplete for use of typeahead
        self.fields['person_rated'].widget.attrs['class'] = 'typeahead'
        self.fields['person_rated'].widget.attrs['autocomplete'] = 'off'
        
    class Meta():
        model=soziomatrix
        fields = ('person_rated', 'value', 'importance', )
    
class BestpracticeInputForm(ModelForm):  
    bp_name = forms.CharField(max_length=50)
    bp_name.label = "Name of the Best Practice"
    
    bp_desc = forms.CharField(widget=forms.Textarea, required=False)
    bp_desc.label = "Description of the Best Practice (optional)"
    
    sectors= forms.ModelMultipleChoiceField(queryset=sectors.objects.all())
    sectors.label = "To which Sectors does the Best Practice belong? (for multiple selection hold down ctrl)"
    
    planning_phase = forms.BooleanField(required=False)
    planning_phase.label = "Best Practice is in the planning phase"
    planning_phase.help_text = "Check this box, if the Best Practice is currently being planned."
    
    start_date = forms.DateField(widget=SelectDateWidget(years=range(2020, 1940, -1)), required=False)
    start_date.label = "Best Practice was started at (optional)"
    
    idea_date = forms.DateField(widget=SelectDateWidget(years=range(2020, 1900, -1)), required=False)
    idea_date.label = "Idea for the Best Practice was developed at (optional)"

    def __init__(self, *args, **kwargs):
        super(BestpracticeInputForm, self).__init__(*args, **kwargs)
        self.fields['sectors'].initial=[s for s in sectors.objects.all() if "|"+str(s.pk)+"|" in self.instance.sectors]
    
class BestpracticeVarInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BestpracticeVarInputForm, self).__init__(*args, **kwargs)
        
        #display the variable according to its encoding
        if self.instance.bp_vars_def_id.encoding == "Text":
            self.fields['value']= forms.CharField(widget=forms.Textarea, required=False)
        elif self.instance.bp_vars_def_id.encoding == "File":
            self.fields['file']= forms.FileField(widget=forms.ClearableFileInput, required=False)
        elif self.instance.bp_vars_def_id.encoding == "Number":
            self.fields['value']= forms.CharField(required=False)
        else:
            #for a dropdown, encoding contains the dropdown_id, instead of Text/File/Number
            try:
                dd_id=int(self.instance.bp_vars_def_id.encoding)
                #get all the dropdown_items with the given dropdown_id
                dd_items=dropdown_item.objects.filter(dropdown_id=dd_id)
            
                #create a choices dictionary, mapping value to displayable name
                DD_LIST = []
                for item in dd_items:
                    DD_LIST.append((item.value, item.name))
            except:
                DD_LIST=[]
            
            #sort the dropdown_list by item.value
            DD_LIST = sorted(DD_LIST, key=itemgetter(0))
            
            self.fields['value']=forms.ChoiceField(choices=DD_LIST, required=False)
        
        #delete the field that is not needed
        if not self.instance.bp_vars_def_id.encoding == "File":
            #set the label
            self.fields['value'].label=self.instance.bp_vars_def_id.var_name
            #set the descriptive help_text
            self.fields['value'].help_text=self.instance.bp_vars_def_id.description
            del self.fields['file']
        else:
            #set the label
            self.fields['file'].label=self.instance.bp_vars_def_id.var_name
            #set the descriptive help_text
            self.fields['file'].help_text=self.instance.bp_vars_def_id.description
            del self.fields['value']
            

        
    class Meta():
        model=bp_vars
        fields=('value', 'file', )
        
class BestpracticeVarDefInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BestpracticeVarDefInputForm, self).__init__(*args, **kwargs)
        
        self.fields['var_name']= forms.CharField(required=False)
        self.fields['encoding']=forms.ChoiceField(choices=(('Text', 'Text'), ('File', 'File'), ('Number', 'Number'),), required=True)
        self.fields['category']=forms.CharField(widget=forms.HiddenInput)
        
        self.fields['var_name'].label = "Name of the new Variable"
        
    class Meta():
        model=bp_vars_def
        fields=('var_name', 'encoding', 'category', )
        
class SectorVarDefInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SectorVarDefInputForm, self).__init__(*args, **kwargs)

        self.fields['var_name']= forms.CharField(required=False)
        self.fields['encoding']=forms.ChoiceField(choices=(('Text', 'Text'), ('File', 'File'), ('Number', 'Number'),), required=True)
        self.fields['category']=forms.CharField(widget=forms.HiddenInput)
        
        self.fields['var_name'].label = "Name of the new Variable"

    class Meta():
        model=sector_vars_def
        fields=('var_name', 'encoding', 'category', )
        
class CityVarDefInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CityVarDefInputForm, self).__init__(*args, **kwargs)

        self.fields['var_name']= forms.CharField(required=False)
        self.fields['encoding']=forms.ChoiceField(choices=(('Text', 'Text'), ('File', 'File'), ('Number', 'Number'),), required=True)
        self.fields['category']=forms.CharField(widget=forms.HiddenInput)
        
        self.fields['var_name'].label = "Name of the new Variable"

    class Meta():
        model=city_vars_def
        fields=('var_name', 'encoding', 'category', )
        
class ImpactFactorVarDefInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImpactFactorVarDefInputForm, self).__init__(*args, **kwargs)

        self.fields['var_name']= forms.CharField(required=False)
        self.fields['encoding']=forms.ChoiceField(choices=(('Text', 'Text'), ('File', 'File'), ('Number', 'Number'),), required=True)
        self.fields['category']=forms.CharField(widget=forms.HiddenInput)
        
        self.fields['var_name'].label = "Name of the new Variable"
        
    class Meta():
        model=impact_factor_vars_def
        fields=('var_name', 'encoding', 'category', )
        
class BestpracticeActorsInputForm(ModelForm):
    def __init__(self, *args, **kwargs):    
        super(BestpracticeActorsInputForm, self).__init__(*args, **kwargs)
        CLASSIFICATION_CHOICES = (
            (1, 'Initiator'),
            (2, 'Beschliessendes Gremium'),
            (3, 'Durchfuehrer'),
            (4, 'Finanzierer'),
            (5, 'Nutzer'),
            (6, 'Weiterer Akteur'),
            )

        super(BestpracticeActorsInputForm, self).__init__(*args, **kwargs)
        self.fields['classification'] = forms.ChoiceField(choices=CLASSIFICATION_CHOICES, required=False)
        self.fields['classification'].label = "Classification of the Actor"
        
        self.fields['actor_name'] = forms.CharField(required=False)
        self.fields['actor_name'].label = "Name of the Actor"
        self.fields['actor_name'].widget.attrs['class'] = 'typeahead'
        self.fields['actor_name'].widget.attrs['autocomplete'] = 'off'

        
    class Meta():
        model=bp_actors
        fields = ('actor_name', 'classification', )
        
class BestpracticeMilestonesInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BestpracticeMilestonesInputForm, self).__init__(*args, **kwargs)
        self.fields['milestone_date'] = forms.DateField(widget=SelectDateWidget(years=range(2020, 1940, -1)), required=False)
        self.fields['milestone_date'].label = "Milestone Date"
        
        self.fields['milestone_desc'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['milestone_desc'].label = "Description of the Milestone"
        
    class Meta():
        model=bp_milestones
        fields = ('milestone_date', 'milestone_desc', )
        
class BestpracticeCriteriaInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BestpracticeCriteriaInputForm, self).__init__(*args, **kwargs)
        self.fields['bp_criteria_name'] = forms.CharField(required=False)
        self.fields['bp_criteria_name'].label = "Name of the Best Practice Criterion"
        
        self.fields['unit'] = forms.CharField(required=False)
        self.fields['unit'].label = "Unit of the Criterion"
        
        self.fields['value_source'] = forms.CharField(widget=forms.Textarea,required=False)
        self.fields['value_source'].label = "Source of the value"
    
    class Meta():
        model=bp_criteria
        fields=('bp_criteria_name', 'unit', 'value_source', )
        
class BestpracticeCriteriaDataInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BestpracticeCriteriaDataInputForm, self).__init__(*args, **kwargs)
        self.fields['criteria_date'] = forms.DateField(widget=SelectDateWidget(years=range(2020, 1940, -1)), required=False)
        self.fields['criteria_date'].label = "Date of the Criterion"
        
        self.fields['criteria_value'] = forms.CharField(required=False)
        self.fields['criteria_value'].label = "Value of the Criterion"
        
        self.fields['number'] = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta():
        model=bp_criteria_data
        fields=('criteria_date', 'criteria_value', )
        
class ImpactFactorCategoryInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImpactFactorCategoryInputForm, self).__init__(*args, **kwargs)
        self.fields['category_name'] = forms.CharField(max_length=50)
        self.fields['category_name'].label = "Name of the Category"
        
        self.fields['category_desc'] = forms.CharField(widget=forms.Textarea, required=False) 
        self.fields['category_desc'].label = "Description of the Category"
        
    class Meta():
        model=impact_factor_categories
        fields = ('category_name', 'category_desc', )

class ImpactFactorInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImpactFactorInputForm, self).__init__(*args, **kwargs)
        IMPACT_FACTOR_CHOICES = (
        (1, 'Technologie'),
        (2, 'Regulierung'),
        (3, 'Akteur'),
        (4, 'Finanzierung'),
        (5, 'Struktur'),
        (6, 'Prozess'),
        )
        
        SECTOR_CHOICES = sectors.objects.all()
    
        self.fields['impact_factor_name'] = forms.CharField(max_length=50)
        self.fields['impact_factor_name'].label = "Name of the Impact Factor"
        
        self.fields['impact_factor_desc'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['impact_factor_desc'].label = "Description of the Impact Factor (optional)"

        self.fields['impact_factor_category_id'] = forms.ModelChoiceField(queryset=impact_factor_categories.objects.all())
        self.fields['impact_factor_category_id'].label = "Category of the Impact Factor"
        
        self.fields['classification'] = forms.ChoiceField(choices=IMPACT_FACTOR_CHOICES)
        self.fields['classification'].label = "Classification of the Impact Factor"
        
        self.fields['t_plan'] = forms.DateField(widget=SelectDateWidget(years=range(2015, 1940, -1)), required=False)
        self.fields['t_plan'].label = "t plan (optional)"
        
        self.fields['t_implementation'] = forms.DateField(widget=SelectDateWidget(years=range(2015, 1940, -1)), required=False)
        self.fields['t_implementation'].label = "t implementation (optional)"
        
        self.fields['t_impact'] = forms.DateField(widget=SelectDateWidget(years=range(2015, 1940, -1)), required=False)
        self.fields['t_impact'].label = "t impact (optional)"
        
        self.fields['sector_id'] = forms.ModelChoiceField(queryset=SECTOR_CHOICES)
        self.fields['sector_id'].label = "The Impact Factor belongs to the following Sector"
    
    class Meta():
        model=impact_factors
        fields = ('impact_factor_name', 'impact_factor_desc', 'impact_factor_category_id', 'classification', 't_plan', 't_implementation', 't_impact', 'sector_id', )

class ImpactfactorVarInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ImpactfactorVarInputForm, self).__init__(*args, **kwargs)

        if self.instance.impact_factor_vars_def_id.encoding == "Text":
            self.fields['value']= forms.CharField(widget=forms.Textarea, required=False)
        elif self.instance.impact_factor_vars_def_id.encoding == "File":
            self.fields['file']= forms.FileField(widget=forms.ClearableFileInput, required=False)
        elif self.instance.impact_factor_vars_def_id.encoding == "Number":
            self.fields['value']= forms.CharField(required=False)
        else:
            #for a dropdown, encoding contains the dropdown_id, instead of Text/File/Number
            try:
                dd_id=int(self.instance.impact_factor_vars_def_id.encoding)
            
                #get all the dropdown_items with the given dropdown_id
                dd_items=dropdown_item.objects.filter(dropdown_id=dd_id)
            
                #create a choices dictionary, mapping value to displayable name
                DD_LIST = []
                for item in dd_items:
                    DD_LIST.append((item.value, item.name))
            
            except:
                DD_LIST=[]

            self.fields['value']=forms.ChoiceField(choices=DD_LIST, required=False)        
        
        
        if not self.instance.impact_factor_vars_def_id.encoding == "File":
            self.fields['value'].label=self.instance.impact_factor_vars_def_id.var_name
            self.fields['value'].help_text=self.instance.impact_factor_vars_def_id.description
            del self.fields['file']
        else:
            self.fields['file'].label=self.instance.impact_factor_vars_def_id.var_name
            self.fields['file'].help_text=self.instance.impact_factor_vars_def_id.description
            del self.fields['value']

    class Meta():
        model=bp_vars
        fields=('value', 'file',)
        
class XFactBpInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(XFactBpInputForm, self).__init__(*args, **kwargs)
        CHOICES = ([(1, 'Has Impact'), (2, 'No Impact'), ])
        self.fields['impact']=forms.ChoiceField(choices=CHOICES)
        self.fields['impact'].label = "Impact on "+self.instance.best_practice_id.bp_name+"?"
        self.fields['impact'].help_text = "Choose whether the Impact Factor \""+self.instance.impact_factor_id.impact_factor_name+"\" has impact on the Best Practice \""+self.instance.best_practice_id.bp_name+"\"."
        
    class Meta():
        model=x_fact_bp
        fields=('impact',)

class XFactSectInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(XFactSectInputForm, self).__init__(*args, **kwargs)
        self.fields['impact']=forms.ChoiceField(choices=((0, 'No Impact'), (1, 'Weak Impact'), (2, 'Intermediate Impact'), (3, 'Strong Impact')))
        self.fields['impact'].label = "Impact on "+self.instance.sector_id.sector_name+":"
        self.fields['impact'].help_text = "Choose how strong the impact of the Impact Factor \""+self.instance.impact_factor_id.impact_factor_name+"\" is on the Sector \""+self.instance.sector_id.sector_name+"\"."
        
    class Meta():
        model=x_fact_sect
        fields=('impact',)
        
class RelationshipImpactFactorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(RelationshipImpactFactorForm, self).__init__(*args, **kwargs)
        IMPACT_CHOICES = ((0, "0 = No Impact"),(1, "+1 = Positive Impact"),(-1, "-1 = Negative Impact"))
        label='Impact of '+str(self.instance.impact_factor_id1)+" on "+str(self.instance.impact_factor_id2)
        
        self.fields['impact'] = forms.ChoiceField(choices=IMPACT_CHOICES)
        self.fields['impact'].label=label
        self.fields['impact'].help_text = "Choose whether the Impact Factor \""+self.instance.impact_factor_id1.impact_factor_name+"\" has a positive, negative or no impact on the Impact Factor \""+self.instance.impact_factor_id2.impact_factor_name+"\"."

    class Meta():
        model=x_fact_fact

class SectorVarInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SectorVarInputForm, self).__init__(*args, **kwargs)

        if self.instance.sector_vars_def_id.encoding == "Text":
            self.fields['value']= forms.CharField(widget=forms.Textarea, required=False)
        elif self.instance.sector_vars_def_id.encoding == "File":
            self.fields['file']= forms.FileField(widget=forms.ClearableFileInput, required=False)
        elif self.instance.sector_vars_def_id.encoding == "Number":
            self.fields['value']= forms.CharField(required=False)
        else:
            #for a dropdown, encoding contains the dropdown_id, instead of Text/File/Number
            try:
                dd_id=int(self.instance.sector_vars_def_id.encoding)
            
                #get all the dropdown_items with the given dropdown_id
                dd_items=dropdown_item.objects.filter(dropdown_id=dd_id)
            
                #create a choices dictionary, mapping value to displayable name
                DD_LIST = []
                for item in dd_items:
                    DD_LIST.append((item.value, item.name))
            
            except:
                DD_LIST=[]

            self.fields['value']=forms.ChoiceField(choices=DD_LIST, required=False)
        
        if not self.instance.sector_vars_def_id.encoding == "File":
            self.fields['value'].label=self.instance.sector_vars_def_id.var_name
            self.fields['value'].help_text=self.instance.sector_vars_def_id.description
            del self.fields['file']
        else:
            self.fields['file'].label=self.instance.sector_vars_def_id.var_name
            self.fields['file'].help_text=self.instance.sector_vars_def_id.description
            del self.fields['value']

    class Meta():
        model=sector_vars
        fields=('value', 'file')

class CityVarInputForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CityVarInputForm, self).__init__(*args, **kwargs)
        
        try:
            self.instance.city_vars_def_id
        except:
            self.fields['value']= forms.CharField(widget=forms.Textarea, required=False)
            del self.fields['file']
            return
        
        if self.instance.city_vars_def_id.encoding == "Text":
            self.fields['value']= forms.CharField(widget=forms.Textarea, required=False)
        elif self.instance.city_vars_def_id.encoding == "File":
            self.fields['file']= forms.FileField(widget=forms.ClearableFileInput, required=False)
        elif self.instance.city_vars_def_id.encoding == "Number":
            self.fields['value']= forms.CharField(required=False)
        else:
            #for a dropdown, encoding contains the dropdown_id, instead of Text/File/Number
            try:
                dd_id=int(self.instance.city_vars_def_id.encoding)
            
                #get all the dropdown_items with the given dropdown_id
                dd_items=dropdown_item.objects.filter(dropdown_id=dd_id)
            
                #create a choices dictionary, mapping value to displayable name
                DD_LIST = []
                for item in dd_items:
                    DD_LIST.append((item.value, item.name))
            
            except:
                DD_LIST=[]

            self.fields['value']=forms.ChoiceField(choices=DD_LIST, required=False)
            
        if not self.instance.city_vars_def_id.encoding == "File":
            self.fields['value'].label=self.instance.city_vars_def_id.var_name
            self.fields['value'].help_text=self.instance.city_vars_def_id.description
            del self.fields['file']
        else:
            self.fields['file'].label=self.instance.city_vars_def_id.var_name
            self.fields['file'].help_text=self.instance.city_vars_def_id.description
            del self.fields['value']

    class Meta():
        model=city_vars
        fields=('value', 'file',)
        
class CommentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['source'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['source'].label = "Source of the information"

        self.fields['comment'] = forms.CharField(widget=forms.Textarea, required=False)
        self.fields['comment'].label = "Comment on the information"
        
        self.fields['table_field'] = forms.CharField(widget=forms.HiddenInput, required=False)
        self.fields['table_id'] = forms.CharField(widget=forms.HiddenInput, required=False)
        self.fields['table_name'] = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta():
        model=comments_fields
        fields=('source', 'comment', 'table_name', 'table_id', 'table_field', )
    

class PasswordForm(forms.Form):
    oldPassword = forms.CharField(max_length=40, widget=forms.PasswordInput())
    newPassword1 = forms.CharField(max_length=40, widget=forms.PasswordInput())
    newPassword2 = forms.CharField(max_length=40, widget=forms.PasswordInput())
    
    oldPassword.label = "Type in your old Password"
    newPassword1.label = "Type in your new Password"
    newPassword2.label = "Retype your new Password"
    