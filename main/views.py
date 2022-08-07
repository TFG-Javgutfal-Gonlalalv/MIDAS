import datetime

from django.contrib.auth.decorators import login_required

from main.nlpcd import ejecucion, ejecucion_sin_solucion
from main.models import Class, Attribute, Relation, Run, FrequentAttributes
from main.converter import convertir_run_codigo_sql
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout  # add this
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm  # add this

import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")


def logout_request(request):
    logout(request)
    return render(request=request, template_name="main/index.html", context={"logout": "Se ha cerrado sesión correctamente"})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("homepage")

        return render(request=request, template_name="main/register.html", context={"register_form": form})
    form = NewUserForm()
    return render(request=request, template_name="main/register.html", context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        context = {}
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect("dashboard")
            else:
                messages.error(request, "Invalid username or password.")
                return render(request=request, template_name="main/login.html",
                              context={"errorUserPassword": "Invalid username or password."})
        else:
            messages.error(request, "Invalid username or password.")
            return render(request=request, template_name="main/login.html",
                          context={"errorUserPassword": "Invalid username or password."})
    form = AuthenticationForm()
    return render(request=request, template_name="main/login.html", context={"login_form": form})


def gpt3(requisitos):

    pregunta = '\n\nDevuelve clases, atributos y relaciones de los requisitos anteriores cumpliendo sin excepción el siguiente formato:\
\
Clase1: atributo1, atributo2...\
Clase2: atributo1, atributo2...\
Clase3: atributo1, atributo2...\
\
Relación1: Clase1, multiplicidad_Clase1, Clase2, multiplicidad_Clase2...\
Relación2: Clase1, multiplicidad_Clase1, Clase2, multiplicidad_Clase2...\
Relación3: Clase1, multiplicidad_Clase1, Clase2, multiplicidad_Clase2...\n\n'

    texto = requisitos + pregunta
    #print(texto)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=texto,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(response.choices[0].text)

    if True:
        response2 = openai.Completion.create(
            engine="text-davinci-002",
            prompt=texto + response.choices[0].text,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        print(response2.choices[0].text)
    with open('main/docs/gpt3', 'w') as f:
        f.write(response.choices[0].text)
        f.write(response2.choices[0].text)


def homepage(request):
    return render(request, "main/index.html")


@login_required(login_url='/login')
def dashboard(request):
    actual_user = request.user

    runs = Run.objects.filter(user_fk__username=actual_user)

    context = {"runs": runs}

    return render(request, "main/dashboard.html", context)


@login_required(login_url='/login')
def diagrama(request):
    if request.method == 'POST':
        if request.POST["texto"]:
            documento = request.POST["texto"]
            run = ejecucion_sin_solucion(documento, request.user)

            classes = Class.objects.filter(run_fk=run)
            attributes = Attribute.objects.filter(run_fk=run)
            relations = Relation.objects.filter(run_fk=run)

            context = {"requirements": documento, "classes": classes, "attributes": attributes, "relations": relations}
            #gpt3(documento)

            return render(request, "main/diagrama.html", context)

    return render(request, "main/form.html")


@login_required(login_url='/login')
def diagrama_gpt3(request):
    if request.method == 'POST':
        if request.POST["texto"]:
            documento = request.POST["texto"]
            run = Run(text=documento, run_datetime=datetime.datetime.now(), user_fk=user)
            run.save()
            gpt3(documento, request.user)

            classes = Class.objects.filter(run_fk=run)
            attributes = Attribute.objects.filter(run_fk=run)
            relations = Relation.objects.filter(run_fk=run)

            context = {"requirements": documento, "classes": classes, "attributes": attributes, "relations": relations}
            #gpt3(documento)

            return render(request, "main/diagrama.html", context)

    return render(request, "main/form_gpt3.html")

@login_required(login_url='/login')
def get_general(request):
    num = 1
    documento = open("main/docs/doc" + str(num), "r", encoding="utf-8").read()
    run, class_rate, attribute_rate, relationship_rate, general_rate = ejecucion(documento, num, request.user)

    classes = Class.objects.filter(run_fk=run)

    context = {"requirements": documento, "solutions": classes.values_list(), "class_rate": class_rate,
               "attribute_rate": attribute_rate, "relationship_rate": relationship_rate,
               "general_rate": general_rate}
    return render(request, "main/main.html", context)


@login_required(login_url='/login')
def converter(request):
    run = Run.objects.get(user_fk=request.user)

    convertir_run_codigo_sql(run)
    return render(request, "main/index.html")


@login_required(login_url='/login')
def run_details(request):
    run = Run.objects.all()[0]

    classes = [{"name": c.name, "score": c.score} for c in Class.objects.filter(run_fk=run)]
    attributes = [{"name": a.name, "score": a.score, "type": a.type, "class": a.class_fk.name} for a in Attribute.objects.filter(run_fk=run)]
    relations = [{"class_1": r.class_fk_1.name, "class_2": r.class_fk_2.name, "phrase": r.phrase, "score": r.score} for r in Relation.objects.filter(run_fk=run)]

    context = {"requirements": run.text, "classes": classes, "attributes": attributes, "relations": relations}
    return render(request, "main/run_datails.html", context)
