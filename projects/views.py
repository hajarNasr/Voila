from django.shortcuts import render

def projects_index(request):
    return render(request, "projects/projects-index.html", {})
