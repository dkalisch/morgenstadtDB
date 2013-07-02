from MorgenstadtDB.database.forms import *
from MorgenstadtDB.database.models import interview_vars, impact_factor_vars
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.utils.datetime_safe import datetime
from django.forms.forms import Form

@login_required
def home_view(request):
    city_list = cities.objects.all()
    return render_to_response('home.html', {'city_list':city_list, 'request':request, }, RequestContext(request))

@login_required
def city_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id)
    notInEditView = True
    
    sector_list = sectors.objects.all()
    bestpractice_list = best_practices.objects.filter(city_id=city_instance.id)
    interview_list = interviews.objects.filter(city_id=city_instance.id)
    
    return render_to_response('city.html', {'city': city_instance, 'sector_list':sector_list, 'bestpractice_list':bestpractice_list, 'interview_list':interview_list, 'notInEditView':notInEditView, }, RequestContext(request))

@login_required
def city_var_view(request, **kwargs):
    city_id = kwargs.get('city_id')
    city_instance = get_object_or_404(cities, id=city_id)
    city_var_def_list = city_vars_def.objects.filter(isGlobal=True)
    ModelFormSet = modelformset_factory(city_vars, CityVarInputForm, extra=0)
    VarDefFormSet = modelformset_factory(city_vars_def, CityVarDefInputForm, extra=0)
    sector_list = sectors.objects.all()
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

        
    # create a sector_var object for every global sector_var_def, if it doesn't exist
    for city_var_def in city_var_def_list:
        city_vars.objects.get_or_create(city_vars_def_id=city_var_def, city_id=city_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now()})
    
    # get all sector_vars that belong to the current sector and template
    city_var_list = city_vars.objects.filter(city_id=city_instance)
    
    # if site is submitted normally
    if request.method == 'POST':
        formset = ModelFormSet(request.POST, request.FILES, prefix="var")
        vardefformset = VarDefFormSet(request.POST, request.FILES, prefix="vardef")
        comment_formset = CommentFormSet(request.POST, prefix="comment")

        print comment_formset.errors
        
        # normal save and continue procedure:
        if formset.is_valid() and vardefformset.is_valid() and comment_formset.is_valid():
            # custom saveFormset method
            saveCityVarFormset(formset, request)
            saveVarDefFormset(vardefformset, request, city_instance, city_instance)
            #save the comment formset
            saveCommentFormset(comment_formset, request, "")  
            
            return redirect('/city/' + city_id + '/vars/')
        return render_to_response('city_var.html', {'formset':formset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'city_var_list':city_var_list, 'city':city_instance, 'city':city_instance, }, RequestContext(request))
    
    formset = ModelFormSet(queryset=city_var_list, prefix="var")
    vardefformset = VarDefFormSet(queryset=city_var_def_list, prefix="vardef")
    comment_list = comments_fields.objects.all()
    comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
    return render_to_response('city_var.html', {'formset':formset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'city_var_list':city_var_list, 'city':city_instance, 'city':city_instance, }, RequestContext(request))


@login_required
def interview_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id) 
    interview_list = interviews.objects.filter(city_id=city_instance.id)
    sector_list = sectors.objects.all()

    return render_to_response('interview.html', {'interview_list':interview_list, 'sector_list':sector_list, 'city':city_instance, }, RequestContext(request))
    
    
@login_required
def interview_add_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id)
    interview_id = kwargs.get('interview_id')
    interview_list = interviews.objects.filter(city_id=city_instance.id)
    sector_list = sectors.objects.all()
    notInEditView = True
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    #get all persons from soziomatrices/interviews
    person_list = getPersonList()
    #get all institutions from interviews
    institution_list = getInstitutionList()
    
    # add empty interview_instance
    interview_instance = interviews()
    interview_instance.city_id = city_instance
    
    # if an interview_partner is defined, we want to render a filled form:
    if interview_id:
        interview_instance = get_object_or_404(interviews, id=interview_id)
        notInEditView = False
        
    # if the method is post, we want to save an instance
    if request.method == 'POST':
        form = InterviewInputForm(request.POST, request.FILES, instance=interview_instance)    
        comment_formset = CommentFormSet(request.POST, prefix="comment")
        
        print comment_formset.errors
        if form.is_valid() and comment_formset.is_valid():
            instance = form.save(commit=False)
            #format the authors to save their id's in a text-field
            authors = ""
            for c in instance.authors_present:
                authors += "|" + str(c.pk) + "|"
            
            instance.authors_present = authors
            
            # only change insert-information on first creation!
            if notInEditView:
                instance.insert_by = request.user.get_profile()
                instance.insert_time = datetime.now()
                instance.city_id = cities.objects.get(id=city_id)
            # if object updated, set update-information
            else:
                instance.update_by = request.user.get_profile()
                instance.update_time = datetime.now()
            
            #file upload
            instance.txtData = form.cleaned_data['txtData']
            instance.audioData = form.cleaned_data['audioData']
            
            #save interview
            instance.save()
            
            #save the comment formset
            saveCommentFormset(comment_formset, request, instance)
            
            #redirect
            return redirect('/city/' + city_id + '/interview/' + str(instance.id) + '/interviewVar/')
        
        # render page with errors:
        return render_to_response('interview_add.html', {'form': form, 'comment_formset':comment_formset, 'sector_list':sector_list, 'person_list':person_list, 'institution_list':institution_list, 'interview_list':interview_list, 'city':city_instance, 'interview':interview_instance, }, RequestContext(request))
         
         
    # if no interview_partner is defined, we want to render an empty form:
    else:
        comment_list = comments_fields.objects.all()
        comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
        
        form = InterviewInputForm(instance=interview_instance)
    return render_to_response('interview_add.html', {'form': form, 'comment_formset':comment_formset, 'sector_list':sector_list, 'person_list':person_list, 'institution_list':institution_list, 'interview_list':interview_list, 'city':city_instance, 'interview':interview_instance, }, RequestContext(request))

@login_required
def interview_var_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id) 
    interview_id = kwargs.get('interview_id')
    interview_instance = get_object_or_404(interviews, id=interview_id)
    interview_var_list = interview_vars.objects.filter(interview_id=interview_instance.id)
    sector_list = sectors.objects.all()

    if request.method == 'POST':
        return redirect('/city/' + city_id + '/interview/')


    return render_to_response('interview_var.html', {'interview_var_list':interview_var_list, 'sector_list':sector_list, 'city':city_instance, 'interview':interview_instance, }, RequestContext(request))

@login_required
def interview_var_add_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id)
    interview_id = kwargs.get('interview_id')
    interview_instance = get_object_or_404(interviews, id=interview_id)
    interview_var_id = kwargs.get('interview_var_id');
    interview_var_list = interview_vars.objects.filter(interview_id=interview_instance.id)
    sector_list = sectors.objects.all()
    notInEditView = True
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    # add empty bestpractice_var_instance
    interview_var_instance = interview_vars()
    
    # if an interview_var is defined, get instance
    if interview_var_id:
        interview_var_instance = get_object_or_404(interview_vars, id=interview_var_id)
        notInEditView = False
    
    if request.method == 'POST':
        form = InterviewVarInputForm(request.POST, request.FILES, instance=interview_var_instance)    
        comment_formset = CommentFormSet(request.POST, prefix="comment")

        print comment_formset.errors
        
        if form.is_valid() and comment_formset.is_valid():
            instance = form.save(commit=False)
            
            # only change insert-information on first creation!
            if notInEditView:
                instance.insert_by = request.user.get_profile()
                instance.insert_time = datetime.now()
                instance.city_id = cities.objects.get(id=city_id)
                instance.interview_id = interview_instance
            # if object updated, set update-information
            else:
                instance.update_by = request.user.get_profile()
                instance.update_time = datetime.now()
            
            instance.save()
            
            #save the comment formset
            saveCommentFormset(comment_formset, request, instance)
            
            return redirect('/city/' + city_id + '/interview/' + interview_id + '/interviewVar/')
    else:
        form = InterviewVarInputForm(instance=interview_var_instance)  
        comment_list = comments_fields.objects.all()
        comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')

    return render_to_response('interview_var_add.html', {'form': form, 'comment_formset':comment_formset, 'sector_list':sector_list, 'interview_var_list':interview_var_list, 'city':city_instance, 'interview':interview_instance, 'interview_var':interview_var_instance, 'id_var_list':['sector_id', 'best_practice_id', 'factor_id']}, RequestContext(request))

@login_required
def soziomatrix_add_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id)
    interview_id = kwargs.get('interview_id')
    interview_instance = get_object_or_404(interviews, id=interview_id)
    soziomatrix_id = kwargs.get('soziomatrix_id');
    soziomatrix_list = soziomatrix.objects.filter(interview_id=interview_id)
    sector_list = sectors.objects.all()
    notInEditView = True
    SoziomatrixFormSet = modelformset_factory(soziomatrix, SoziomatrixInputForm, extra=0)

    #get all persons from interviews/soziomatrices for typeahead
    person_list = getPersonList()
            
        
    # add empty impactfactor_instance
    soziomatrix_instance = soziomatrix()
    
    # if an impactfactor_name is defined,
    # get instance and don't display existing impactfactors
    if soziomatrix_id:
        soziomatrix_instance = get_object_or_404(soziomatrix, id=soziomatrix_id)
        notInEditView = False

    if request.method == 'POST':
        #---START display add_var stuff----#
        soziomatrixformset = SoziomatrixFormSet(request.POST, prefix='soziomatrix')

        # normal save and continue procedure:
        if soziomatrixformset.is_valid():
            # custom saveFormset method
            saveSoziomatrixFormset(soziomatrixformset, request, interview_instance)

            return redirect('/city/' + city_id + '/interview/add/' + interview_id + '/soziomatrix/add/')
        else:
            return render_to_response('soziomatrix_add.html', {'soziomatrixformset': soziomatrixformset, 'person_list':person_list, 'sector_list':sector_list, 'interview':interview_instance, 'soziomatrix':soziomatrix_instance, 'soziomatrix_list':soziomatrix_list, 'city':city_instance, 'notInEditView':notInEditView, }, RequestContext(request))
    else:
        soziomatrixformset = SoziomatrixFormSet(queryset=soziomatrix_list, prefix='soziomatrix')
    
    return render_to_response('soziomatrix_add.html', {'soziomatrixformset':soziomatrixformset, 'person_list':person_list, 'sector_list':sector_list, 'city':city_instance, 'interview':interview_instance, 'notInEditView':notInEditView, 'soziomatrix':soziomatrix_instance, 'soziomatrix_list':soziomatrix_list, }, RequestContext(request))

@login_required
def bestpractice_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id) 
    bestpractice_list = best_practices.objects.filter(city_id=city_instance.id)
    sector_list = sectors.objects.all()

    return render_to_response('bestpractice.html', {'bestpractice_list':bestpractice_list, 'sector_list':sector_list, 'city':city_instance, }, RequestContext(request))

@login_required
def bestpractice_add_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id)
    bestpractice_id = kwargs.get('bestpractice_id')
    bestpractice_list = best_practices.objects.filter(city_id=city_instance.id)
    sector_list = sectors.objects.all()
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    notInEditView = True
    
    # add empty bestpractice_instance
    bestpractice_instance = best_practices()
    
    # if an bestpractice_name is defined,
    # get instance, don't display existing bps in html
    if bestpractice_id:
        bestpractice_instance = get_object_or_404(best_practices, id=bestpractice_id)
        notInEditView = False

    if request.method == 'POST':
        form = BestpracticeInputForm(request.POST, instance=bestpractice_instance)    
        comment_formset = CommentFormSet(request.POST, prefix="comment")
        
        print comment_formset.errors
        
        if form.is_valid() and comment_formset.is_valid():
            instance = form.save(commit=False)
            # only change insert-information on first creation!
            if notInEditView:
                instance.insert_by = request.user.get_profile()
                instance.insert_time = datetime.now()
                instance.city_id = cities.objects.get(id=city_id)
                
                sector = ""
                for s in instance.sectors:
                    sector += "|" + str(s.pk) + "|"
                    
                instance.sectors = sector
                instance.save()
                
                # create three bp_criteria
                for i in range(0, 3):
                    criteria = bp_criteria()
                    criteria.bp_criteria_name = ""
                    criteria.insert_time = datetime.now()
                    criteria.insert_by = request.user.get_profile()
                    criteria.best_practice_id = instance
                    
                    criteria.save()
        
            # if object updated, set update-information
            else:
                
                instance.update_by = request.user.get_profile()
                instance.update_time = datetime.now()
                sector = ""
                for s in instance.sectors:
                    sector += "|" + str(s.pk) + "|"
                    
                instance.sectors = sector
                instance.save()
            
            #save the comment formset
            saveCommentFormset(comment_formset, request, instance)
            
            return redirect('/city/' + city_id + '/bestpractice/add/' + str(instance.id) + '/bestpracticeDescription/')
    else:
        comment_list = comments_fields.objects.all()
        comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')

        form = BestpracticeInputForm(instance=bestpractice_instance)
          
    return render_to_response('bestpractice_add.html', {'form': form, 'comment_formset':comment_formset, 'sector_list':sector_list, 'bestpractice':bestpractice_instance, 'bestpractice_list':bestpractice_list, 'city':city_instance, 'notInEditView':notInEditView, }, RequestContext(request))

@login_required
def bestpractice_description_view(request, **kwargs):
    city_id = kwargs.get('city_id')
    city_instance = get_object_or_404(cities, id=city_id) 
    bestpractice_id = kwargs.get('bestpractice_id')
    bestpractice_instance = get_object_or_404(best_practices, id=bestpractice_id)
    VarFormSet = modelformset_factory(bp_vars, BestpracticeVarInputForm, extra=0)
    VarDefFormSet = modelformset_factory(bp_vars_def, BestpracticeVarDefInputForm, extra=0)
    MilestoneFormSet = modelformset_factory(bp_milestones, BestpracticeMilestonesInputForm, extra=0)
    CriteriaFormSet = modelformset_factory(bp_criteria, BestpracticeCriteriaInputForm, extra=0)
    CriteriaDataFormSet = modelformset_factory(bp_criteria_data, BestpracticeCriteriaDataInputForm, extra=0)
    bp_var_def_list = bp_vars_def.objects.filter(isGlobal=True)
    sector_list = sectors.objects.all()
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    
    # create a bp_var object for every global bp_var_def, if it doesn't exist
    for bp_var_def in bp_var_def_list:
        bp_vars.objects.get_or_create(bp_vars_def_id=bp_var_def, best_practice_id=bestpractice_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now()})
    
    #---- START get all bp_vars, milestones, criteria, criteria_data that belong to here-----
    bp_var_list = bp_vars.objects.filter(best_practice_id=bestpractice_id).filter(bp_vars_def_id__category__lte=4)
    bp_milestone_list = bp_milestones.objects.filter(best_practice_id=bestpractice_id)
    bp_criteria_list = bp_criteria.objects.filter(best_practice_id=bestpractice_id)
    bp_criteria_data_list = None
    
    if bp_criteria_list:
        bp_criteria_data_list = bp_criteria_data.objects.filter(bp_criteria_id=bp_criteria_list[0])
        for criteria in bp_criteria_list:
            bp_criteria_data_list = bp_criteria_data_list | bp_criteria_data.objects.filter(bp_criteria_id=criteria)
    #------ END get all lists ------
    
    # if site is submitted normally
    if request.method == 'POST':
        comment_formset = CommentFormSet(request.POST, prefix="comment")
        varformset = VarFormSet(request.POST, request.FILES, prefix='var')
        vardefformset = VarDefFormSet(request.POST, request.FILES, prefix="vardef")
        milestoneformset = MilestoneFormSet(request.POST, prefix='milestone')
        criteriaformset = CriteriaFormSet(request.POST, prefix='criteria')
        criteriadataformset = CriteriaDataFormSet(request.POST, prefix='criteria_data')          
        
        print comment_formset.errors
        
        if varformset.is_valid() and vardefformset.is_valid() and milestoneformset.is_valid() and criteriaformset.is_valid() and criteriadataformset.is_valid() and comment_formset.is_valid():
            # custom saveFormset method
            saveVarFormset(varformset, request, bestpractice_instance)
            saveVarDefFormset(vardefformset, request, bestpractice_instance, city_instance)
            saveMilestoneFormset(milestoneformset, request, bestpractice_instance)
            saveCriteriaFormset(criteriaformset, request, bestpractice_instance)
            saveCriteriaDataFormset(criteriadataformset, request, bestpractice_instance)            
            saveCommentFormset(comment_formset, request, "")

            # redirect
            return redirect('/city/' + city_id + '/bestpractice/add/' + bestpractice_id + '/bestpracticeDetail/')

        # render page with errors:
        return render_to_response('bestpractice_description.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'milestoneformset':milestoneformset, 'criteriaformset':criteriaformset, 'criteriadataformset':criteriadataformset, 'bp_var_list':bp_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, }, RequestContext(request))
            
    # render page, on a get request:
    criteriaformset = CriteriaFormSet(queryset=bp_criteria_list, prefix='criteria')
    criteriadataformset = CriteriaDataFormSet(queryset=bp_criteria_data_list, prefix='criteria_data')
    varformset = VarFormSet(queryset=bp_var_list, prefix='var')
    vardefformset = VarDefFormSet(queryset=bp_var_def_list, prefix="vardef")
    milestoneformset = MilestoneFormSet(queryset=bp_milestone_list, prefix='milestone')
    comment_list = comments_fields.objects.all()
    comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
    return render_to_response('bestpractice_description.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'milestoneformset':milestoneformset, 'criteriaformset':criteriaformset, 'criteriadataformset':criteriadataformset, 'bp_var_list':bp_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, }, RequestContext(request))
    
@login_required
def bestpractice_detail_view(request, **kwargs):
    city_id = kwargs.get('city_id')
    city_instance = get_object_or_404(cities, id=city_id) 
    bestpractice_id = kwargs.get('bestpractice_id')
    bestpractice_instance = get_object_or_404(best_practices, id=bestpractice_id)
    VarFormSet = modelformset_factory(bp_vars, BestpracticeVarInputForm, extra=0)
    VarDefFormSet = modelformset_factory(bp_vars_def, BestpracticeVarDefInputForm, extra=0)
    ActorFormSet = modelformset_factory(bp_actors, BestpracticeActorsInputForm, extra=0)
    bp_var_def_list = bp_vars_def.objects.filter(isGlobal=True)
    sector_list = sectors.objects.all()
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    actor_list = getActorList()
    
    # create a bp_var object for every global bp_var_def, if it doesn't exist
    for bp_var_def in bp_var_def_list:
        bp_vars.objects.get_or_create(bp_vars_def_id=bp_var_def, best_practice_id=bestpractice_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now()})
    
    # get all bp_vars that belong to the current bp and template
    bp_var_list = bp_vars.objects.filter(best_practice_id=bestpractice_id).filter(bp_vars_def_id__category__lte=8).filter(bp_vars_def_id__category__gte=5)
    # get bp_actor_list
    bp_actor_list = bp_actors.objects.filter(best_practice_id=bestpractice_instance)

    # if site is submitted with post
    if request.method == 'POST':
        varformset = VarFormSet(request.POST, request.FILES, prefix='var')
        vardefformset = VarDefFormSet(request.POST, request.FILES, prefix="vardef")
        actorformset = ActorFormSet(request.POST, prefix='actor')
        comment_formset = CommentFormSet(request.POST, prefix="comment")

        print comment_formset.errors

        if varformset.is_valid() and actorformset.is_valid() and vardefformset.is_valid() and comment_formset.is_valid():
            # custom saveFormset method
            saveActorFormset(actorformset, request, bestpractice_instance)
            saveVarFormset(varformset, request, bestpractice_instance)
            saveVarDefFormset(vardefformset, request, bestpractice_instance, city_instance)
            #save the comment formset
            saveCommentFormset(comment_formset, request, "") 
            
            # redirect to next page
            return redirect('/city/' + city_id + '/bestpractice/add/' + bestpractice_id + '/bestpracticeImpact/')
        
        # render page with errors:
        return render_to_response('bestpractice_detail.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'actor_list':actor_list, 'vardefformset':vardefformset, 'actorformset':actorformset, 'bp_var_list':bp_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, }, RequestContext(request))
    
    # render page, on a get request:
    actorformset = ActorFormSet(queryset=bp_actor_list, prefix='actor')
    varformset = VarFormSet(queryset=bp_var_list, prefix='var')
    vardefformset = VarDefFormSet(queryset=bp_var_def_list, prefix="vardef")
    comment_list = comments_fields.objects.all()
    comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
    
    return render_to_response('bestpractice_detail.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'actor_list':actor_list, 'vardefformset':vardefformset, 'actorformset':actorformset, 'bp_var_list':bp_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, }, RequestContext(request))
        
@login_required
def bestpractice_impact_view(request, **kwargs):
    city_id = kwargs.get('city_id')
    city_instance = get_object_or_404(cities, id=city_id) 
    bestpractice_id = kwargs.get('bestpractice_id')
    bestpractice_instance = get_object_or_404(best_practices, id=bestpractice_id)
    VarFormSet = modelformset_factory(bp_vars, BestpracticeVarInputForm, extra=0)
    VarDefFormSet = modelformset_factory(bp_vars_def, BestpracticeVarDefInputForm, extra=0)
    bp_var_def_list = bp_vars_def.objects.filter(isGlobal=True)
    sector_list = sectors.objects.all()
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    # create a bp_var object for every global bp_var_def, if it doesn't exist
    for bp_var_def in bp_var_def_list:
        bp_vars.objects.get_or_create(bp_vars_def_id=bp_var_def, best_practice_id=bestpractice_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now()})
    
    # get all bp_vars that belong to the current bp and template
    bp_var_list = bp_vars.objects.filter(best_practice_id=bestpractice_id).filter(bp_vars_def_id__category__lte=12).filter(bp_vars_def_id__category__gte=9)


    # if site is submitted normally
    if request.method == 'POST':
        varformset = VarFormSet(request.POST, request.FILES, prefix="var")
        vardefformset = VarDefFormSet(request.POST, request.FILES, prefix="vardef")
        comment_formset = CommentFormSet(request.POST, prefix="comment")
        
        print comment_formset.errors
        
        # normal save and continue procedure:
        if varformset.is_valid() and vardefformset.is_valid() and comment_formset.is_valid():
            # custom saveFormset method
            saveVarFormset(varformset, request, bestpractice_instance)
            saveVarDefFormset(vardefformset, request, bestpractice_instance, city_instance)
            
            #save the comment formset
            saveCommentFormset(comment_formset, request, "") 
             
            return redirect('/city/' + city_id + '/bestpractice/add/' + bestpractice_id + '/bestpracticeImpact/')
        # render page with errors:
        return render_to_response('bestpractice_impact.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'bp_var_list':bp_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, }, RequestContext(request))
    
    # render page, on a get request:
    varformset = VarFormSet(queryset=bp_var_list, prefix="var")
    vardefformset = VarDefFormSet(queryset=bp_var_def_list, prefix="vardef")
    comment_list = comments_fields.objects.all()
    comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
    return render_to_response('bestpractice_impact.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'bp_var_list':bp_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, }, RequestContext(request))

@login_required
def impactfactor_view(request, **kwargs):
    city_id = kwargs.get('city_id');
    city_instance = get_object_or_404(cities, id=city_id) 
    bestpractice_id = kwargs.get('bestpractice_id')
    bestpractice_instance = get_object_or_404(best_practices, id=bestpractice_id)
    
    #if "remove Connection" was pressed on an impact factor, MUST happen before impact_factor_lists are queried below
    if request.method=='POST' and 'delIf' in request.POST:
        #get id of impact factor
        if_id = request.POST["delIf"]
        #get impact factor
        impFac = impact_factors.objects.get(id=if_id)
        #remove id of this bp from best_practice_id of impact factor
        impFac.best_practice_id = impFac.best_practice_id.replace("|"+bestpractice_id+"|", "")
        #save the impact factor
        impFac.save()

    #get all impact factors, that belong to this bp
    impactfactor_list = impact_factors.objects.filter(best_practice_id__icontains="|"+bestpractice_id+"|")
    #get all impactfactors, that are not in the above impactfactor_list
    allother_impactfactors_list = impact_factors.objects.filter(city_id=city_instance).exclude(best_practice_id__icontains="|"+bestpractice_id+"|")
    
    #get all impactfactors that have impact on the current bp
    x_fact_bps = x_fact_bp.objects.filter(best_practice_id=bestpractice_instance).filter(impact=1)
    all_impactfactors_with_impact = []
    for xfb in x_fact_bps:
        all_impactfactors_with_impact.append(xfb.impact_factor_id)
    #--------------
    
    city_list = cities.objects.all()
    sector_list = sectors.objects.all()
    
    #if the "add existing" button is pressed
    if request.method=='POST':
        #get selected impact factors from dropdown
        impactfactors_to_add = request.POST.getlist('impactfactors')
        #if impact factors were selected in the dropdown
        if(impactfactors_to_add):
            #for every selected impactfactor, add the current BP to its best_practice_id
            for i in impactfactors_to_add:
                impactfactor = impact_factors.objects.get(pk=int(i))
                impactfactor.best_practice_id+="|"+str(bestpractice_instance.id)+"|"
                impactfactor.save()
                
    return render_to_response('impactfactor.html', {'impactfactor_list':impactfactor_list, 'all_impactfactors_with_impact':all_impactfactors_with_impact, 'allother_impactfactors_list':allother_impactfactors_list, 'sector_list':sector_list, 'city_list':city_list, 'city':city_instance, 'bestpractice':bestpractice_instance, }, RequestContext(request))

@login_required
def impactfactor_add_view(request, **kwargs):
    city_id = kwargs.get('city_id')
    city_instance = get_object_or_404(cities, id=city_id)
    bestpractice_id = kwargs.get('bestpractice_id')
    bestpractice_instance = get_object_or_404(best_practices, id=bestpractice_id)
    impactfactor_id = kwargs.get('impactfactor_id')
    impactfactor_list = impact_factors.objects.filter(city_id=city_instance.id)
    sector_list = sectors.objects.all()
    notInEditView = True
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    # add empty impactfactor_instance
    impactfactor_instance = impact_factors()
    
    # if an impactfactor_name is defined,
    # get instance and don't display existing impactfactors
    if impactfactor_id:
        impactfactor_instance = get_object_or_404(impact_factors, id=impactfactor_id)
        notInEditView = False
        
    if request.method == 'POST':
        form = ImpactFactorInputForm(request.POST, instance=impactfactor_instance)    
        category_form = ImpactFactorCategoryInputForm(request.POST)
        comment_formset = CommentFormSet(request.POST, prefix="comment")

        print comment_formset.errors
        
        if form.is_valid() and not 'categoryFormSaved' in request.POST and comment_formset.is_valid():
            instance = form.save(commit=False)

            # only change insert-information on first creation!
            if notInEditView:
                instance.insert_by = request.user.get_profile()
                instance.insert_time = datetime.now()
                instance.city_id = cities.objects.get(id=city_id)
                instance.best_practice_id = "|"+str(bestpractice_instance.id)+"|"
            # if object updated, set update-information
            else:
                instance.update_by = request.user.get_profile()
                instance.update_time = datetime.now()
            
            instance.save()
            
            #save the comment formset
            saveCommentFormset(comment_formset, request, instance)
            return redirect('/city/' + city_id + '/bestpractice/add/' + bestpractice_id + '/impactfactor/add/' + str(instance.id) + '/info/')
        
        if category_form.is_valid():
            instance = category_form.save(commit=False)

            instance.insert_by = request.user.get_profile()
            instance.insert_time = datetime.now()
            
            instance.save()
            
            category_form = ImpactFactorCategoryInputForm()
            form = ImpactFactorInputForm(instance=impactfactor_instance)
            
        return render_to_response('impactfactor_add.html', {'form': form, 'comment_formset':comment_formset, 'category_form':category_form, 'sector_list':sector_list, 'impactfactor':impactfactor_instance, 'impactfactor_list':impactfactor_list, 'city':city_instance, 'notInEditView':notInEditView, 'bestpractice':bestpractice_instance, }, RequestContext(request))
         
    form = ImpactFactorInputForm(instance=impactfactor_instance)
    category_form = ImpactFactorCategoryInputForm()
    comment_list = comments_fields.objects.all()
    comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
    
    return render_to_response('impactfactor_add.html', {'form': form, 'comment_formset':comment_formset, 'category_form':category_form, 'sector_list':sector_list, 'impactfactor':impactfactor_instance, 'impactfactor_list':impactfactor_list, 'city':city_instance, 'notInEditView':notInEditView, 'bestpractice':bestpractice_instance, }, RequestContext(request))

@login_required
def impactfactor_info_view(request, **kwargs):
    city_id = kwargs.get('city_id')
    city_instance = get_object_or_404(cities, id=city_id) 
    bestpractice_id = kwargs.get('bestpractice_id')
    bestpractice_instance = get_object_or_404(best_practices, id=bestpractice_id)
    bp_list = best_practices.objects.filter(city_id=city_id)
    impactfactor_id = kwargs.get('impactfactor_id')
    impactfactor_instance = get_object_or_404(impact_factors, id=impactfactor_id)
    impactfactor_list = impact_factors.objects.filter(city_id=city_instance.id)
    if_var_def_list = impact_factor_vars_def.objects.filter(isGlobal=True)
    sector_list = sectors.objects.all()
    
    VarFormSet = modelformset_factory(impact_factor_vars, ImpactfactorVarInputForm, extra=0)
    VarDefFormSet = modelformset_factory(impact_factor_vars_def, ImpactFactorVarDefInputForm, extra=0)
    BpFormSet = modelformset_factory(x_fact_bp, XFactBpInputForm, extra=0)
    RelFormSet = modelformset_factory(x_fact_fact, RelationshipImpactFactorForm, fields=('impact',), extra=0)
    SectorFormSet = modelformset_factory(x_fact_sect, XFactSectInputForm, extra=0)
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    # create a if_var object for every global bp_var_def, if it doesn't exist
    for if_var_def in if_var_def_list:
        impact_factor_vars.objects.get_or_create(impact_factor_vars_def_id=if_var_def, impact_factors_id=impactfactor_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now()})
    
    # create a x_fact_bp object for every other bp
    for bp in bp_list:
        if not (bp == bestpractice_instance): 
            x_fact_bp.objects.get_or_create(best_practice_id=bp, impact_factor_id=impactfactor_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now(), 'impact':2})
    
    # create a x_fact_sect object for every
    for sect in sector_list:
        x_fact_sect.objects.get_or_create(sector_id=sect, impact_factor_id=impactfactor_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now()})
    
    # get or create x_fact_fact objects
    for i in impactfactor_list:
        if not i == impactfactor_instance:
            x_fact_fact.objects.get_or_create(impact_factor_id1=impactfactor_instance, impact_factor_id2=i, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now(), 'impact':0})[0]
            x_fact_fact.objects.get_or_create(impact_factor_id1=i, impact_factor_id2=impactfactor_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now(), 'impact':0})[0]
        
    # combine the two querysets        
    x_fact_list = x_fact_fact.objects.filter(impact_factor_id1=impactfactor_instance) | x_fact_fact.objects.filter(impact_factor_id2=impactfactor_instance)
    x_fact_sect_list = x_fact_sect.objects.filter(impact_factor_id=impactfactor_instance)
    
    # get all var that belong to the current if and template
    impactfactor_var_list = impact_factor_vars.objects.filter(impact_factors_id=impactfactor_id)

    # if site is submitted normally
    if request.method == 'POST':
        varformset = VarFormSet(request.POST, request.FILES, prefix='var')
        vardefformset = VarDefFormSet(request.POST, request.FILES, prefix="vardef")
        bpformset = BpFormSet(request.POST, prefix='bp')
        relformset = RelFormSet(request.POST, prefix='rel')
        sectformset = SectorFormSet(request.POST, prefix='sector')
        comment_formset = CommentFormSet(request.POST, prefix="comment")
        
        print comment_formset.errors
        
        if varformset.is_valid() and vardefformset.is_valid() and bpformset.is_valid() and relformset.is_valid() and sectformset.is_valid() and comment_formset.is_valid():
            # custom saveFormset method
            saveIfVarFormset(varformset, request, impactfactor_instance)
            saveVarDefFormset(vardefformset, request, impactfactor_instance, city_instance)
            saveIfBpFormset(bpformset, request, impactfactor_instance)
            saveRelFormset(relformset, request)
            saveXFactSectFormset(sectformset, request)
            #save the comment formset
            saveCommentFormset(comment_formset, request, "") 
            
            return redirect('/city/' + city_id + '/bestpractice/add/' + bestpractice_id + '/impactfactor/add/' + str(impactfactor_id) + '/info/')
        return render_to_response('impactfactor_info.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'bpformset':bpformset, 'relformset':relformset, 'sectformset':sectformset, 'x_fact_list':x_fact_list, 'impactfactor_var_list':impactfactor_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, 'impactfactor':impactfactor_instance, }, RequestContext(request))
    
    sectformset = SectorFormSet(queryset=x_fact_sect_list, prefix='sector')
    relformset = RelFormSet(queryset=x_fact_list, prefix='rel')
    bpformset = BpFormSet(queryset=x_fact_bp.objects.filter(impact_factor_id=impactfactor_id), prefix='bp')
    vardefformset = VarDefFormSet(queryset=if_var_def_list, prefix="vardef")
    varformset = VarFormSet(queryset=impactfactor_var_list, prefix='var')
    comment_list = comments_fields.objects.all()
    comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
    
    return render_to_response('impactfactor_info.html', {'varformset':varformset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'bpformset':bpformset, 'relformset':relformset, 'sectformset':sectformset, 'x_fact_list':x_fact_list, 'impactfactor_var_list':impactfactor_var_list, 'city':city_instance, 'bestpractice':bestpractice_instance, 'impactfactor':impactfactor_instance, }, RequestContext(request))

@login_required
def sector_add_view(request, **kwargs):
    city_id = kwargs.get('city_id')
    city_instance = get_object_or_404(cities, id=city_id)
    sector_id = kwargs.get('sector_id')
    sector_instance = get_object_or_404(sectors, id=sector_id)
    sector_var_def_list = sector_vars_def.objects.filter(isGlobal=True).filter(sector_id=sector_instance)
    sector_list = sectors.objects.all()
    ModelFormSet = modelformset_factory(sector_vars, SectorVarInputForm, extra=0)
    VarDefFormSet = modelformset_factory(sector_vars_def, SectorVarDefInputForm, extra=0)
    CommentFormSet = modelformset_factory(comments_fields, CommentForm, extra=0)

    # create a sector_var object for every global sector_var_def, if it doesn't exist
    for sector_var_def in sector_var_def_list:
        sector_vars.objects.get_or_create(sector_vars_def_id=sector_var_def, sector_id=sector_instance, city_id=city_instance, defaults={'insert_by':request.user.get_profile(), 'insert_time':datetime.now()})
    
    # get all sector_vars that belong to the current sector and template
    sector_var_list = sector_vars.objects.filter(sector_id=sector_instance).filter(city_id=city_instance)
    
    # if site is submitted normally
    if request.method == 'POST':
        #---START display add_var stuff----#
        formset = ModelFormSet(request.POST, request.FILES, prefix="var")
        vardefformset = VarDefFormSet(request.POST, request.FILES, prefix="vardef")
        comment_formset = CommentFormSet(request.POST, prefix="comment")
        
        print comment_formset.errors
        
        # normal save and continue procedure:
        if formset.is_valid() and vardefformset.is_valid() and comment_formset.is_valid():
            # custom saveFormset method
            saveSectorVarFormset(formset, request)
            saveVarDefFormset(vardefformset, request, sector_instance, city_instance)
            #save the comment formset
            saveCommentFormset(comment_formset, request, "")
             
            return redirect('/city/' + city_id + '/sector/' + sector_id + '/')
        
        return render_to_response('sector_add.html', {'formset':formset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'sector_var_list':sector_var_list, 'city':city_instance, 'sector':sector_instance, }, RequestContext(request))
   
    formset = ModelFormSet(queryset=sector_var_list, prefix="var")
    vardefformset = VarDefFormSet(queryset=sector_var_def_list, prefix="vardef")
    comment_list = comments_fields.objects.all()
    comment_formset=CommentFormSet(queryset=comment_list, prefix='comment')
    
    return render_to_response('sector_add.html', {'formset':formset, 'comment_formset':comment_formset, 'sector_list':sector_list, 'vardefformset':vardefformset, 'sector_var_list':sector_var_list, 'city':city_instance, 'sector':sector_instance, }, RequestContext(request))

@login_required
def password_view(request):
    error = ""
    success = ""
    pForm = PasswordForm()

    if request.method == 'POST':
        if request.POST['submit'] == 'Change':
            pForm = PasswordForm(request.POST)
            if pForm.is_valid():
                oldPass = request.POST['oldPassword']
                newPass1 = request.POST['newPassword1']
                newPass2 = request.POST['newPassword2']
                if newPass1 == newPass2 and request.user.check_password(oldPass):
                    user = request.user
                    user.set_password(newPass1)
                    user.save()
                    success = "Your password was successfully changed!"
                else:
                    if not request.user.check_password(oldPass):
                        error = "The old password was incorrect."
                    else:
                        error = "The new passwords didn't match."
                    pForm = PasswordForm()

    return render_to_response('registration/change_password.html', {'pForm':pForm, 'error':error, 'success':success, }, RequestContext(request))

def logout_view(request):
    auth.logout(request)
    # Redirect to a success page.
    return render_to_response('registration/logout.html', {'request': request, }, RequestContext(request))

def getPersonList():
    person_list = []
    #add all persons from interviews to person_list
    for i in interviews.objects.all():
        if not i.person in person_list and i.person:
            person_list.append(i.person)
            
    #add all persons from soziomatrices to person_list
    for s in soziomatrix.objects.all():
        if not s.person_rated in person_list and s.person_rated:
            person_list.append(s.person_rated)
    
    return person_list

def getInstitutionList():
    institution_list = []
    #add all institutions from interviews to institution_list
    for i in interviews.objects.all():
        if not i.institution in institution_list and i.institution:
            institution_list.append(i.institution)
    
    return institution_list

def getActorList():
    actor_list = []
    #add all actors from bp_actors to actor_list
    for a in bp_actors.objects.all():
        if not a.actor_name in actor_list and a.actor_name:
            actor_list.append(a.actor_name)
    
    return actor_list
            
def saveVarFormset(formset, request, bestpractice):
    for form in formset:
        instance = form.save(commit=False)
        # if it is a bp_var: get the existing object (view above makes sure there is always a bp_var existing)
        old = bp_vars.objects.get(pk=instance.id)
        # change update_by and update_time only if object updated
        if (not old.value == instance.value) or (not old.file == instance.file):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()

def saveVarDefFormset(formset, request, obj, city):
    for form in formset:
        instance = form.save(commit=False)
        var = None
        
        #if no var_name is given, go to the next form without saving
        if not instance.var_name:
            continue
        
        # if the var_def is first created
        if (not instance.insert_time):
            instance.insert_time = datetime.now()
            instance.insert_by = request.user.get_profile()
            instance.isGlobal = False
            # create sector_var, if it is a sector_var
            if obj.__class__.__name__ == "sectors":
                instance.sector_id = obj
            instance.save()
            
            # create city_var, if it is a city_var
            if obj.__class__.__name__ == "cities":
                var = city_vars()
                var.city_vars_def_id = instance
                var.city_id = obj

            # create city_var, if it is a city_var
            if obj.__class__.__name__ == "sectors":
                var = sector_vars()
                var.city_id = city
                var.sector_vars_def_id = instance
                var.sector_id = obj

            # create city_var, if it is a city_var
            if obj.__class__.__name__ == "impact_factors":
                var = impact_factor_vars()
                var.impact_factor_vars_def_id = instance
                var.impact_factors_id = obj

            # create city_var, if it is a city_var
            if obj.__class__.__name__ == "best_practices":
                var = bp_vars()
                var.bp_vars_def_id = instance
                var.best_practice_id = obj
                
            var.insert_by = request.user.get_profile()
            var.insert_time = datetime.now()
            var.save()

def saveIfVarFormset(formset, request, impactfactor):
    for form in formset:
        instance = form.save(commit=False)
        # if it is a bp_var: get the existing object (view above makes sure there is always a bp_var existing)
        old = impact_factor_vars.objects.get(pk=instance.id)
        # change update_by and update_time only if object updated
        if (not old.value == instance.value) or (not old.file == instance.file):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()

def saveSectorVarFormset(formset, request):
    for form in formset:
        instance = form.save(commit=False)
        # if it is a sector_var: get the existing object (view above makes sure there is always a sector_var existing)
        old = sector_vars.objects.get(pk=instance.id)
        # change update_by and update_time only if object updated
        if (not old.value == instance.value) or (not old.file == instance.file):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()

def saveCityVarFormset(formset, request):
    for form in formset:
        instance = form.save(commit=False)
        try:
            old = city_vars.objects.get(pk=instance.id)
        except:
            instance.save()
            continue
        
        # change update_by and update_time only if object updated
        if (not old.value == instance.value) or (not old.file == instance.file):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()

def saveIfBpFormset(formset, request, impactfactor):
    for form in formset:
        instance = form.save(commit=False)
        # if it is a bp_var: get the existing object (view above makes sure there is always a bp_var existing)
        old = x_fact_bp.objects.get(pk=instance.id)
        # change update_by and update_time only if object updated
        if (not old.impact == instance.impact):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()
            
def saveSoziomatrixFormset(formset, request, interview):
    for form in formset:
        instance = form.save(commit=False)
        
        # if the actor isn't defined: go to next object
        if not instance.person_rated:
            continue
        
        old = soziomatrix.objects.get_or_create(pk=instance.id, defaults={'person_rated':instance.person_rated, 'importance':instance.importance, 'value':instance.value, 'insert_time':datetime.now(), 'insert_by':request.user.get_profile(), 'interview_id':interview})[0]
        
        # change update_by and update_time only if object updated
        if (not old.person_rated == instance.person_rated) or (not old.value == instance.value)or (not old.importance == instance.importance):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()
            
def saveActorFormset(formset, request, bestpractice):
    for form in formset:
        instance = form.save(commit=False)
        
        # if the actor isn't defined: go to next object
        if not instance.actor_name:
            continue
        
        old = bp_actors.objects.get_or_create(pk=instance.id, defaults={'actor_name':instance.actor_name, 'classification':instance.classification, 'insert_time':datetime.now(), 'insert_by':request.user.get_profile(), 'best_practice_id':bestpractice})[0]
        
        # change update_by and update_time only if object updated
        if (not old.classification == instance.classification) or (not old.actor_name == instance.actor_name):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()

def saveRelFormset(formset, request):
    for form in formset:
        instance = form.save(commit=False)
        old = x_fact_fact.objects.get(pk=instance.id)
        
        # change update_by and update_time only if object updated
        if (not old.impact == instance.impact):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()
            
def saveXFactSectFormset(formset, request):
    for form in formset:
        instance = form.save(commit=False)
        old = x_fact_sect.objects.get(pk=instance.id)
        
        # change update_by and update_time only if object updated
        if (not old.impact == instance.impact):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()
            
def saveMilestoneFormset(formset, request, bestpractice):
    for form in formset:
        instance = form.save(commit=False)
        
        # if the milestone isn't defined: go to next object
        if (not instance.milestone_date) and (not instance.milestone_desc):
            continue
            
        # get or create the milestone
        old = bp_milestones.objects.get_or_create(pk=instance.id, defaults={'milestone_desc':instance.milestone_desc, 'milestone_date':instance.milestone_date, 'insert_time':datetime.now(), 'insert_by':request.user.get_profile(), 'best_practice_id':bestpractice})[0]
          
        # if it was edited set update information
        if (not old.milestone_date == instance.milestone_date) or (not old.milestone_desc == instance.milestone_desc):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()

def saveCommentFormset(formset, request, parentInstance):
    for form in formset:
        instance = form.save(commit=False)
        
        # if no source or comment is defined: go to next object
        if (not instance.source) and (not instance.comment):
            continue
            
        #get the table_id. it is -1, if the object wasnt created until just now
        table_id = instance.table_id
        
        #if the table_id is -1, use the table_id of the parentInstance instead
        if(table_id==-1):
            table_id = parentInstance.id

        # get or create the milestone
        old = comments_fields.objects.get_or_create(pk=instance.id, defaults={'table_name':instance.table_name, 'table_id':table_id, 'table_field':instance.table_field, 'source':instance.source, 'comment':instance.comment, 'insert_time':datetime.now(), 'insert_by':request.user.get_profile()})[0]

        # if it was edited set update information
        if (not old.source == instance.source) or (not old.comment == instance.comment):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()

def saveCriteriaFormset(formset, request, bestpractice):
    for form in formset:
        instance = form.save(commit=False)
        
        # if the criteria isn't defined: go to next object
        if not instance.bp_criteria_name:
            continue
        
        # get or create the milestone
        old = bp_criteria.objects.get_or_create(pk=instance.id, defaults={'bp_criteria_name':instance.bp_criteria_name, 'unit':instance.unit, 'value_source':instance.value_source, 'insert_time':datetime.now(), 'insert_by':request.user.get_profile(), 'best_practice_id':bestpractice})[0]
          
        # if it was edited set update information
        if (not old.bp_criteria_name == instance.bp_criteria_name) or (not old.bp_criteria_name == instance.bp_criteria_name) or (not old.value_source == instance.value_source):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()
                            
def saveCriteriaDataFormset(formset, request, bestpractice_instance):
    for form in formset:    
        instance = form.save(commit=False)
        
        # if neither date nor value is entered, continue with the next form        
        if (not instance.criteria_date) and (not instance.criteria_value):
            continue 
        
        # if the instance already exists, we already know the bp_criterion
        if form.cleaned_data['id']:
            criterion = instance.bp_criteria_id
        # if it doesn't exist yet:
        else:
            # get the id of the parent criterion via the forms data
            criterion_id = int(form.cleaned_data['number'])
            # get the bp_criterion itself
            criterion = bp_criteria.objects.get(pk=int(criterion_id))
        
        # count all the criteria_data belonging to the bp_criterion
        criteria_data_count = len(bp_criteria_data.objects.filter(bp_criteria_id=criterion)) + 1
        
        # get criteria_data or if it doesn't exist yet: create it with default values
        old = bp_criteria_data.objects.get_or_create(pk=instance.id, bp_criteria_id=criterion, defaults={'criteria_value':instance.criteria_value, 'criteria_date':instance.criteria_date, 'insert_by':request.user.get_profile(), 'insert_time':datetime.now(), 'criteria_count':criteria_data_count})[0]
        
        # if it was edited set update information, otherwise not
        if (not old.criteria_value == instance.criteria_value) or (not old.criteria_date == instance.criteria_date):
            instance.update_time = datetime.now()
            instance.update_by = request.user.get_profile()
            instance.save()
                            
