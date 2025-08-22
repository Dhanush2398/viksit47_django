
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .models import Question, Option
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, "index.html")

def exams(request):
    return render(request, "exams.html")

def blogs(request):
    return render(request, "blogs.html")

def contact(request):
    return render(request, "contact.html")

def mock(request):
    return render(request, 'mock.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html') 

@login_required(login_url='login')  
def mock(request):
    return render(request, "mock.html")

def logout_view(request):
    logout(request)
    return redirect('home') 


def register_view(request):
    if request.user.is_authenticated:  
        return redirect('home')

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')  
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home') 

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')

def mock(request):
    questions = Question.objects.prefetch_related("options").all()
    return render(request, "mock.html", {"questions": questions})

def submit_mock(request):
    if request.method == "POST":
        questions = Question.objects.prefetch_related("options").all()
        total = questions.count()
        attempted = 0
        correct = 0

        for q in questions:
            selected_option_id = request.POST.get(f"q{q.id}")
            if selected_option_id:  
                attempted += 1
                option = Option.objects.get(id=selected_option_id)
                if option.is_correct:
                    correct += 1

        context = {
            "total": total,
            "attempted": attempted,
            "correct": correct,
        }
        return render(request, "result.html", context)

    return redirect("mock")  


def result(request):
   
    score = request.session.get("score", 0)
    total = request.session.get("total", 0)

    return render(request, "result.html", {
        "score": score,
        "total": total
    })
