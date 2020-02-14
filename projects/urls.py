from django.urls import path
from . import views

app_name = "projects"
urlpatterns =[
    path('', views.projects_index, name="projects_index")
]