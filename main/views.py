from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Tutorial, TutorialCategory, TutorialSeries
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import NewUserForm

# basically, if the slug (like the /.../ pt of the url) is a category or tutorial, we handle it somehow
def single_slug(request, single_slug):
    categories = [c.category_slug for c in TutorialCategory.objects.all()]
    if single_slug in categories:
        matching_series = TutorialSeries.objects.filter(tutorial_category__category_slug=single_slug) # this links to the attribute category_slug for out tutorial category that we want to have

        series_urls = {}
        
        for m in matching_series.all():
            # iterating though and checking if series obj is linked in table to tutorial obj
            part_one = Tutorial.objects.filter(tutorial_series__tutorial_series=m.tutorial_series)#.earliest("tutorial_published") # NOTE: if we had more tutorials earliest method would actually work, but unfortunately, there will be some part_ones when iterating through this that could be sorted
            # if linked, it forms a queryset that we check to see if it has len > 0
            # if so, we add it to the urls that we can link to
            if part_one.exists(): # checks to see if we have a match for a tutorial
                series_urls[m] = part_one[0].tutorial_slug
            # then we just put a link to nothing, so we can remove that for now
            #else:
            #    series_urls[m] = part_one 
            
        return render(request,
                      "main/category.html",
                      {"part_ones":series_urls})
    
    tutorials = [t.tutorial_slug for t in Tutorial.objects.all()]
    if single_slug in tutorials:
        # we want to get the tutorial in the queryset that matches the single_slug then render it
        this_tutorial = Tutorial.objects.get(tutorial_slug=single_slug)
        # so this gets us all the Tutorial objects of the same tutorial series
        tutorial_series = Tutorial.objects.filter(tutorial_series__tutorial_series=this_tutorial.tutorial_series).order_by("tutorial_published")

        # want to get the index of the tutorial we're currently on so we can show it
        this_tutorial_idx = list(tutorial_series).index(this_tutorial)
        # then we pass these things to our tutorials.html page and render it
        return render(request,
                      "main/tutorial.html",
                      {"tutorial":this_tutorial,
                       "sidebar":tutorial_series,
                       "this_tutorial_idx":this_tutorial_idx})
        
    return HttpResponse(f"{single_slug} does not correspond to anything")
    
# this is the reverted views      
def homepage(request):
    return render(request=request,
                  template_name='main/categories.html',
                  context={"categories": TutorialCategory.objects.all})

def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid(): # if it's a valid registration, save POST info
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New account created.")
            login(request,user) # login the user
            return redirect("main:homepage") # redirect to the homepage
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")


    form = NewUserForm
    return render(request,
                  "main/register.html",
                  context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")

def login_request(request):
    if request.method =="POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("main:homepage")
            else:
                messages.error(request, "Invalid username or password.")

    else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request,
                  "main/login.html",
                  {"form":form})
