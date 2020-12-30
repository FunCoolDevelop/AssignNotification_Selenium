from django.shortcuts import render, get_object_or_404
from .models import Assign, College, Student, Course, Quiz, TeamPro

def index(request) :
    students = Student.objects.all()
    return render(request, 'index.html',{"students":students})

def crawlSingle(request,stid) :
    sid = int(stid)
    return render(request, 'crawlPage.html')

def crawlAll(request) :
    return render(request, 'crawlPage.html')