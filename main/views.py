from main.nlpcd import ejecucion, ejecucion_sin_solucion
from main.models import Class, Attribute, Relation, Run, FrequentAttributes
from main.converter import convertir_run_codigo_sql
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate  # add this
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm  # add this


# Create your views here.
def homepage(request):
    return render(request, "main/index.html")


def diagrama(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.POST["texto"]:
                documento = request.POST["texto"]
                run = ejecucion_sin_solucion(documento, request.user)

                classes = Class.objects.filter(run_fk=run)
                attributes = Attribute.objects.filter(run_fk=run)
                relations = Relation.objects.filter(run_fk=run)

                context = {"requirements": documento, "classes": classes,"attributes": attributes, "relations": relations}


                return render(request, "main/diagrama.html",context)

        return render(request, "main/form.html")
    return redirect("/login")


def get_general(request):
    num = 1
    if request.user.is_authenticated:
        documento = open("main/docs/doc" + str(num), "r", encoding="utf-8").read()
        run, class_rate, attribute_rate, relationship_rate, general_rate = ejecucion(documento, num, request.user)

        classes = Class.objects.filter(run_fk=run)

        context = {"requirements": documento, "solutions": classes.values_list(), "class_rate": class_rate,
                   "attribute_rate": attribute_rate, "relationship_rate": relationship_rate,
                   "general_rate": general_rate}
        return render(request, "main/main.html", context)
    else:
        return redirect("/login")


def register_request(request):
    if request.method == "POST":
        print("hola")
        form = NewUserForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("homepage")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="main/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("homepage")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="main/login.html", context={"login_form": form})

def converter(request):
    if request.user.is_authenticated:
        run = Run.objects.get(user_fk=request.user)

        convertir_run_codigo_sql(run)
        return render(request, "main/index.html")

    return redirect("/login")