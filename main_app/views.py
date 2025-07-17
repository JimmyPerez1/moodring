import requests
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from .models import MoodEntry
import os
from moodring.api import generate_affirmation


MOOD_COLORS = {
        "Happy": "#FFF3B0",        # Soft Yellow
    "Sad": "#A0C4FF",          # Light Blue
    "Angry": "#FFADAD",        # Soft Red
    "Anxious": "#FFE1A8",      # Soft Orange
    "Calm": "#C7F9CC",         # Pale Green
    "Tired": "#D0C7FF",        # Light Lavender
    "Excited": "#FFC6FF",      # Soft Pink
    "Frustrated": "#CABBE9",   # Soft Purple
    "Grateful": "#B5F2D4",     # Light Teal
    "Other": "#E0E0E0",        # Light Gray fallback
}

class Home(LoginView):
    template_name = "home.html"

class MoodCreate(CreateView):
    model = MoodEntry
    fields = ['mood', 'intensity', 'journal_text']
    
    def form_valid(self, form):
        form.instance.user = self.request.user

        mood = form.cleaned_data['mood']
        journal_text = form.cleaned_data['journal_text']
        api_key = os.getenv("GEMINI_API_KEY")

        affirmation = generate_affirmation(api_key, mood, journal_text)
        
        form.instance.affirmation = affirmation

        return super().form_valid(form)


class MoodUpdate(UpdateView):
    model = MoodEntry
    fields = ['journal_text']
    success_url = '/moods/'

class MoodDelete(DeleteView):
    model = MoodEntry
    success_url = '/moods/'

def moods_index(request):
    moods = MoodEntry.objects.filter(user=request.user).order_by('-created_at')
    
    mood_summary = (
        MoodEntry.objects
        .filter(user=request.user)
        .values('mood')
        .annotate(count=Count('mood'))
        .order_by('-count')
    )

    labels = [entry['mood'] for entry in mood_summary]
    data = [entry['count'] for entry in mood_summary]
    colors = [MOOD_COLORS.get(label, "#E0E0E0") for label in labels]

    return render(request, 'moods/index.html', {
    'moods': moods,
    'mood_labels': labels,
    'mood_data': data,
    'mood_colors': colors,
})

def about(request):
    return render(request, "about.html")


def signup(request):
    error_message = ""
    if request.method == "POST":
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in
            login(request, user)
            return redirect("moods")
        else:
            error_message = "Invalid sign up - try again"
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "signup.html", context)


def mood_detail(request, pk):
    mood = MoodEntry.objects.get(id=pk)
    affirmation = request.session.pop('affirmation', None)
    return render(request, 'moods/detail.html', {
        'mood': mood,
        'affirmation': affirmation
    })
def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['affirmation'] = self.request.session.pop('affirmation', None)
        return context  
        # return render(request, 'moods/detail.html', {'mood': mood})