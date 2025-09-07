from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
import requests, shortuuid
from .models import  Mock, Question, Option, MockResult,StudyMaterial, Author, StudyMaterialItem,CourseSubscription
from .forms import RegisterForm


auth_api = 'https://api-preprod.phonepe.com/apis/pg-sandbox'
pg_api = 'https://api-preprod.phonepe.com/apis/pg-sandbox'

client_id = "TESTVVUAT_2502041721357207510164"
client_secret = "ZTcxNDQyZjUtZjQ3Mi00MjJmLTgzOWYtMWZmZWQ2ZjdkMzVi"
client_version = "1"
redirect_url = "http://127.0.0.1:8000"



def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def gallery(request):
    return render(request, "gallery.html")

def exams(request):
    mocks = Mock.objects.all().order_by('-id')
    return render(request, "exams.html", {"mocks": mocks})

def studymaterials_view(request):
    return render(request, "studymaterials.html")

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please log in.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("home")
@login_required
def profile(request):
    results = MockResult.objects.filter(user=request.user).order_by("-created_at")
    subscriptions = CourseSubscription.objects.filter(
        user=request.user, 
        is_paid=True, 
        end_date__gte=date.today()
    ).order_by("-end_date") 

    return render(request, "profile.html", {
        "user": request.user,       
        "results": results,        
        "purchased_courses": subscriptions, 
        "today": date.today(),     
    })

@login_required
def cuet_view(request):
    if not has_active_subscription(request.user, course_slug='cuet_ug_icar'):
        messages.info(request, "You need to purchase the CUET UG Agriculture – ICAR course to access this content.")
        return redirect('buy_course_payment', course_slug='cuet_ug_icar')

    mocks = Mock.objects.filter(course='cuet_ug_icar').order_by('-id')
    study_materials = StudyMaterial.objects.filter(course='cuet_ug_icar').order_by('-id')
    authors = Author.objects.all()
    return render(request, "cuet_ug.html", {"mocks": mocks, "study_materials": study_materials, "authors": authors})

@login_required
def agriculture_quota_view(request):
    if not has_active_subscription(request.user, course_slug='agri_quota'):
        messages.info(request, "You need to purchase the Agriculture Quota Practical Exam course to access this content.")
        return redirect('buy_course_payment', course_slug='agri_quota')

    mocks = Mock.objects.filter(course='agri_quota').order_by('-id')
    study_materials = StudyMaterial.objects.filter(course='agri_quota').order_by('-id')
    authors = Author.objects.all()
    return render(request, "agriculture_quota.html", {"mocks": mocks, "study_materials": study_materials, "authors": authors})

@login_required
def mock(request, mock_id):
    exam = get_object_or_404(Mock, id=mock_id)
    questions = Question.objects.filter(mock=exam).prefetch_related("options")
    return render(request, "mock.html", {"exam": exam, "questions": questions})

@login_required
def submit_mock(request, mock_id):
    exam = get_object_or_404(Mock, id=mock_id)
    if request.method == "POST":
        questions = Question.objects.prefetch_related("options").filter(mock=exam)
        total = questions.count()
        attempted = correct = 0
        answers = []

        for q in questions:
            selected_option_id = request.POST.get(f"q{q.id}")
            selected_option = None
            correct_option = q.options.filter(is_correct=True).first()
            if selected_option_id:
                attempted += 1
                selected_option = Option.objects.get(id=selected_option_id)
                if selected_option.is_correct:
                    correct += 1
            answers.append({
                "question": q,
                "selected_option": selected_option,
                "correct_option": correct_option,
            })

        MockResult.objects.create(
            user=request.user,
            mock=exam,
            total=total,
            attempted=attempted,
            correct=correct
        )

        return render(request, "result.html", {
            "total": total,
            "attempted": attempted,
            "correct": correct,
            "mock": exam,
            "answers": answers,
        })
    return redirect("mock", mock_id=exam.id)

@login_required
def studymaterial_detail(request, pk):
    study_material_items = StudyMaterialItem.objects.filter(study_material=pk)
    study_material_title = StudyMaterial.objects.get(pk=pk)
    return render(request, "studymaterial_detail.html", {"study_material": study_material_items, "study_material_title": study_material_title})


@login_required
def buy_course_payment(request, course_slug):
    if course_slug == "agri_quota":
        price_online = 2000
        price_offline = 2500
    else:
        price_online = 2000
        price_offline = 0
    return render(request, "payment.html", {
        "course_slug": course_slug,
        "price_online": price_online,
        "price_offline": price_offline
    })

@login_required
def subscribe_1year(request, course_slug):
    if request.method == "POST":
        mode = request.POST.get("mode", "online")

        if course_slug == "agri_quota":
            price_online = 2000
            price_offline = 2500
        else:
            price_online = 2000
            price_offline = 2000  
        amount = price_online if mode == "online" else price_offline

        uid = shortuuid.uuid()
        subscription = CourseSubscription.objects.create(
            user=request.user,
            course_slug=course_slug,
            end_date=date.today() + timedelta(days=365),
            uu_id=uid,
            amount=amount,
            is_paid=False,
        )

        token_resp = requests.post(auth_api + "/v1/oauth/token", data={
            "client_id": client_id,
            "client_secret": client_secret,
            "client_version": client_version,
            "grant_type": "client_credentials"
        }, headers={"Content-Type": "application/x-www-form-urlencoded"})

        access_token = token_resp.json()['access_token']

        body = {
            "merchantOrderId": uid,
            "amount": amount * 100,
            "paymentFlow": {
                "type": "PG_CHECKOUT",
                "merchantUrls": {
                    "redirectUrl": f"{redirect_url}/subscription-return/{uid}?mode={mode}"
                }
            }
        }

        response = requests.post(pg_api + "/checkout/v2/pay",
                                 json=body,
                                 headers={
                                     "Content-Type": "application/json",
                                     "Authorization": f"O-Bearer {access_token}"
                                 })

        payurl = response.json()['redirectUrl']
        return render(request, "pay.html", {"outputurl": payurl, "amount": amount, "course_slug": course_slug})

    return redirect('buy_course_payment', course_slug=course_slug)

@login_required
def subscription_return(request, uid):
    token_resp = requests.post(auth_api + "/v1/oauth/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "client_version": client_version,
        "grant_type": "client_credentials"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})

    access_token = token_resp.json()['access_token']

    response = requests.get(f"{pg_api}/checkout/v2/order/{uid}/status",
                            headers={"Content-Type": "application/json",
                                     "Authorization": f"O-Bearer {access_token}"})
    data = response.json()

    subscription = get_object_or_404(CourseSubscription, uu_id=uid)

    if data.get("state") == "COMPLETED":
        subscription.is_paid = True
        subscription.transaction_id = data.get("orderId")
        subscription.save()
        messages.success(request, "Payment successful! You now have access to the course.")

        if subscription.course_slug == "agri_quota":
            return redirect("agriculturequota")
        elif subscription.course_slug == "cuet_ug_icar":
            return redirect("cuet")
        else:
            return redirect("home")
    else:
        messages.error(request, "Payment failed or pending. Try again.")
        return redirect("buy_course_payment", course_slug=subscription.course_slug)
    
def has_active_subscription(user, course_slug=None):

    qs = CourseSubscription.objects.filter(user=user, is_paid=True, end_date__gte=date.today())
    if course_slug:
        qs = qs.filter(course_slug=course_slug)
    return qs.exists()

def home(request):
    if request.user.is_authenticated:
        purchased_courses = CourseSubscription.objects.filter(
            user=request.user,
            is_paid=True,
            end_date__gte=date.today()
        ).values_list("course_slug", flat=True)
    else:
        purchased_courses = []

    return render(request, "index.html", {
        "purchased_courses": purchased_courses,
    })
