from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Mock, Question, Option, MockResult



def home(request):
    mocks = Mock.objects.all().order_by('-id')
    return render(request, "index.html", {"mocks": mocks})


def exams(request):
    mocks = Mock.objects.all().order_by('-id')
    return render(request, "exams.html", {"mocks": mocks})


def blogs(request):
    return render(request, "blogs.html")


def contact(request):
    return render(request, "contact.html")



def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("home")



@login_required(login_url="login")
def mock_redirect(request):
    mock = Mock.objects.first()
    if mock:
        return redirect("mock", mock_id=mock.id)
    return redirect("home")


@login_required(login_url="login")
def mock(request, mock_id):
    exam = get_object_or_404(Mock, id=mock_id)
    questions = Question.objects.filter(mock=exam).prefetch_related("options")
    return render(request, "mock.html", {
        "exam": exam,
        "questions": questions
    })


@login_required(login_url="login")
def submit_mock(request, mock_id):
    exam = get_object_or_404(Mock, id=mock_id)

    if request.method == "POST":
        questions = Question.objects.prefetch_related("options").filter(mock=exam)

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

        MockResult.objects.create(
            user=request.user,
            mock=exam,
            total=total,
            attempted=attempted,
            correct=correct
        )

        context = {
            "total": total,
            "attempted": attempted,
            "correct": correct,
            "mock": exam,
            "questions": questions
        }
        return render(request, "result.html", context)

    return redirect("mock", mock_id=exam.id)



@login_required
def profile_view(request):
    return render(request, "profile.html", {"user": request.user})

@login_required(login_url="login")
def profile(request):
    results = MockResult.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "profile.html", {"results": results})

def equipments_view(request):
    return render(request, "equipments.html")
