from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

import secrets

import markdown
import markdown2

from . import util


class newForm(forms.Form):
    title = forms.CharField(label="Entry Title",
                            widget=forms.TextInput(attrs={'class': 'form-control col-md-6 col-lg-6'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control col-md-8 col-lg-8', 'rows': 10}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def convertHTML(entry_name):
    mark = markdown.Markdown()
    entry = util.get_entry(entry_name)
    html = mark.convert(entry) if entry else None
    return html


def entry(request, entry):
    markdown = markdown2.Markdown()
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonExisting.html", {
            "entryTitle": entry,
            "entries": util.list_entries()
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown.convert(entryPage),
            "entryTitle": entry
        })


def newEntry(request):
    return render(request, "encyclopedia/newEntry.html")


def random(request):
    random_entries = util.list_entries()
    random_entryChoice = secrets.choice(random_entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry': random_entryChoice}))


def search(request):
    if request.method == 'POST':
        input = request.POST['q']
        html = convertHTML(input)

        entries = util.list_entries()

        if input in entries:
            return render(request, "encyclopedia/entry.html", {
                "entry": html,
                "entryTitle": input,
            })
        else:
            allEntries = util.list_entries()
            recommendation = []
            for entry in allEntries:
                if input.lower() in entry.lower():
                    recommendation.append(entry)
            return render(request, "encyclopedia/search.html", {
                "recommendation": recommendation,
            })


def saveNewEntry(request):
    if request.method == 'POST':
        input_title = request.POST['title']
        input_text = request.POST['text']
        entries = util.list_entries()
        if input_title in entries:
            return render(request, "encyclopedia/existing.html", {
                "entryTitle": input_title
            })
        else:
            util.save_entry(input_title, input_text)
            html = convertHTML(input_title)
            return render(request, "encyclopedia/entry.html", {
                "entry": html,
                "entryTitle": input_title
            })


def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/nonExisting.html", {
            "entryTitle": entry
        })
    else:
        form = newForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
    return render(request, "encyclopedia/edit.html", {
        "form": form,
        "edit": form.fields["edit"].initial,
        "entryTitle": form.fields["title"].initial,
        "entry": entryPage
    })


def save_edit(request):
    if request.method == 'POST':
        input_title = request.POST['title']
        input_text = request.POST['text']
        util.save_entry(input_title, input_text)
        html = convertHTML(input_title)
        return render(request, "encyclopedia/entry.html", {
            "entry": html,
            "entryTitle": input_title
        })
