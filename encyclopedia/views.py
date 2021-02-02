from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import markdown2
import random
from django.core.files.storage import default_storage
from . import util

class SearchForm(forms.Form):
    # Define all the fields form will have
    query = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Wiki','style': 'width:100%'}))

class NewPageForm(forms.Form):
    # Define all the field form will have 
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Enter title', 'id': 'new-entry-title'}))
    data = forms.CharField(widget=forms.Textarea(attrs={'id': 'new-entry'}))

class EditPageForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'id': 'edit-entry-title'}))
    data = forms.CharField(widget=forms.Textarea(attrs={'id': 'edit-entry'}))



''' 
This view returns a template encyclopedia/index.html, providing the template with a list of all of the entries in the encyclopedia (obtained by calling util.list_entries, which we saw defined in util.py)
'''

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })

'''
This view will return a given entry page where TITLE is the title of the encyclopedia entry 
1. Return error page if titlepage.html is not found
2. Return page if title.html found - the title of the page should include the name of the entry
'''

def entry(request, title): 
    entry = util.get_entry(title)
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "title": title,
            "form": SearchForm()
            })       
    else:
        return render(request, "encyclopedia/entry.html", {
            "title":title,
            "entry": markdown2.markdown(entry),
            "form": SearchForm()
        })

'''
Search for a query user has typed into search box for entry
1. If query matches an entry, return to entry's page 
2. If query does not match entry name, return search page with list of entries that have query as a substring
3. Clicking on any of the entry names on search page will redirect to entry's page
'''

def search(request):
    # Check if method is POST
    if request.method == "POST":
        # List of entries that match query
        entries_found = []
        # All entries
        entries_all = util.list_entries()
        # Get query from search
        form = SearchForm(request.POST)
        # Check form is valid (server-side)
        if form.is_valid():
            # Isolate the query, search entries
            query = form.cleaned_data["query"]
            # Check if entries match query
            for entry in entries_all: 
                if query.lower() == entry.lower():
                    title = entry
                    entry = util.get_entry(title)
                    return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))
                # Check for partial match
                if query.lower() in entry.lower():
                    entries_found.append(entry)
            # Return list of partial matches
            return render(request, "encyclopedia/search.html", {
                "results": entries_found,
                "query": query, 
                "form": SearchForm()
            })
    # Default 
    return render(request, "encyclopedia/search.html", {
        "results": "",
        "query": "",
        "form": SearchForm()
    })

''' 
Create New Entry/page
Enter title for page 
In textarea, user to be able to enter markdown content for the page 
Save page - if entry already exists (title) present with error message 
Otherwise saved to disk 
'''

def create(request):
    if request.method == "POST":
        # Take in data the user submitted and save it as new_entry
        new_entry = NewPageForm(request.POST)
        if new_entry.is_valid():
            # Isolate the data from new_entry
            title = new_entry.cleaned_data["title"]    
            data = new_entry.cleaned_data["data"]
            # Check if entry exists already
            entries_all = util.list_entries()
            for entry in entries_all:
                if entry.lower() == title.lower():
                    return render(request, "encyclopedia/create.html", {
                        "form": SearchForm(),
                        "newPageForm": NewPageForm(),
                        "error": "This entry already exists"
                    })
            # Added markdown for content of entry
            new_entry_title = "# " + title
            # A new line is appended to seperate title from content
            new_entry_data = "\n" + data
            # Combine the title and data to store as content
            new_entry_content = new_entry_title + new_entry_data
            # Save the new entry with the title
            util.save_entry(title, new_entry_content)
            entry = util.get_entry(title)
            # Take user to new page
            return render(request, "encyclopedia/entry.html", {
                "title":title,
                "entry": markdown2.markdown(entry),
                "form": SearchForm()
            })
    
    return render(request,"encyclopedia/create.html", {
       "form": SearchForm(),
       "newPageForm": NewPageForm() 
    })

''' 
Edit Page 
Edit existing markdown content of the page 
Redirect to entry page once user has saved on click of button 
'''

def edit(request, title):
    if request.method == "POST":
        # Get the data already stored for the entry
        entry = util.get_entry(title)
        # Display the content in the textarea, creating an initial form
        edit_form = EditPageForm(initial={'title': title, 'data': entry})
        # Return page with the forms filled in with entry
        return render(request, "encyclopedia/edit.html", {
            "form": SearchForm(),
            "editPageForm": edit_form,
            "entry": entry,
            "title": title,
        })

'''
Submit edit
'''

def submitEdit(request, title):
    if request.method == "POST":
        # Extract information from form
        edit_entry = EditPageForm(request.POST)
        if edit_entry.is_valid():
            # Extract 'data' from form
            content = edit_entry.cleaned_data["data"]
            # Extract 'title' from form
            title_edit = edit_entry.cleaned_data["title"]
            # If the title is edited, delete old file
            if title_edit != title:
                filename = f"entries/{title}.md"
                if default_storage.exists(filename):
                    default_storage.delete(filename)
            # Save new entry
            util.save_entry(title_edit, content)
            # Get the new entry 
            entry = util.get_entry(title_edit)
            msg_success = "Successfully updated!"
        # Return the edited entry
        return render(request, "encyclopedia/entry.html", {
            "title": title_edit,
            "entry": markdown2.markdown(entry),
            "form": SearchForm(),
            "msg_success": msg_success
        })

def randomEntry(request):
   # Get list of all entries
    entries = util.list_entries()
    # Get the title of a randomly selected entry
    title = random.choice(entries)
    # Get the content of the selected entry
    entry = util.get_entry(title)
    # Return the redirect page for the entry
    return HttpResponseRedirect(reverse("encyclopedia:entry", args=[title]))