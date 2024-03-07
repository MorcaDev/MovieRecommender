from django.urls import path, include
from Engine.views import *

urlpatterns = [
    path('', index, name = "index"),
]
