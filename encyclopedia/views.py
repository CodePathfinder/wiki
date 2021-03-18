from django.forms.widgets import Textarea
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django import forms
import random

from . import util


class NewEntryForm(forms.Form):
    title = forms.CharField(label='Title', widget=forms.TextInput)
    entry_text = forms.CharField(label='Text', widget=forms.Textarea)

    title.widget.attrs.update({'class': 'form-control'})
    entry_text.widget.attrs.update({'class': 'form-control', 'rows': 10})


def index(request):
    if request.method == "POST":
        query = request.POST['q'].lower()
        titles = util.list_entries()
        lowercase_titles = []
        for i in range(len(titles)):
            lowercase_titles.append(titles[i].lower())
        if query in lowercase_titles:
            return HttpResponseRedirect(reverse('entry', kwargs={'title': query }))
        else:
            shortlist_entries = []
            for title in titles:
                if query in title.lower():
                    shortlist_entries.append(title)

            if shortlist_entries:
                return render(request, "encyclopedia/index.html", { 
                    "titles": shortlist_entries,
                    "message": "Search results" 
                })
            else:
                return render(request, "encyclopedia/index.html", { 
                    "titles": util.list_entries(),
                    "message": "All pages" 
                })
    else:            
        return render(request, "encyclopedia/index.html", {
            "titles": util.list_entries(),
            "message": "All pages"
        })


def empty_title(request):
    return HttpResponseRedirect(reverse('index'))


def entry(request, title):
    entry = util.get_entry(title)
    if entry:    
        return render(request, "encyclopedia/entry.html", {
        "entry": util.markdown_to_html(entry), "title": title })
    else:
        return render(request, "encyclopedia/entry.html", {
        'message': 'The requested page was not found.'})


def new_page(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data["title"]
            titles = util.list_entries()
            
            lowercase_titles = []
            for i in range(len(titles)):
                lowercase_titles.append(titles[i].lower())
            
            if new_title.lower() in lowercase_titles:
                return render(request, "encyclopedia/new_page.html", { 
                "form": form, "message": "Error: entry with this title already exists"
            })
            else:
                entry_text = form.cleaned_data["entry_text"]
                util.save_entry(new_title, entry_text)
                return render(request, "encyclopedia/new_page.html", {
                    'form': NewEntryForm(), 'message': "New entry is saved successfully!"
                })            
        else:
            return render(request, "encyclopedia/new_page.html", { 
                "form": form, "message": "Validation error"
            })
    else:
        return render(request, "encyclopedia/new_page.html", {
            'form': NewEntryForm()
        })


def edit_page(request, title):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry_text = form.cleaned_data["entry_text"]
            util.save_entry(title, entry_text)
            return HttpResponseRedirect(reverse('entry', kwargs={'title': title }))
    else:
        context = { 
            'title': title, 
            'entry_text': util.get_entry(title) 
        }
        return render(request, "encyclopedia/edit_page.html", { 
            'form': NewEntryForm(context),
            'title': title
        })


def random_page(request):
    return HttpResponseRedirect(reverse('entry', kwargs={'title': random.choice(util.list_entries()) }))