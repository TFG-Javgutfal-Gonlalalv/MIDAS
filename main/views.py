import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.nlpcd import ejecucion, ejecucion_sin_solucion
from main.models import Class, Attribute, Relation, Run, FrequentAttributes, UserExtras
from main.converter import convertir_run_codigo_sql
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout  # add this
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm  # add this

import os
import openai
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")


def logout_request(request):
    logout(request)
    return render(request=request, template_name="main/index.html",
                  context={"logout": "Se ha cerrado sesión correctamente"})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            userExtras = UserExtras(user_fk=user, money=0)
            userExtras.save()
            return redirect("dashboard")

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


def gpt3(requisitos, run):
    pregunta = '\n\nDevuelve clases, atributos y relaciones de los requisitos anteriores cumpliendo sin excepción el siguiente formato:\n\n\
Clases:\n\
Clase1: atributo1, atributo2...\n\
Clase2: atributo1, atributo2...\n\
Clase3: atributo1, atributo2...\n\
...\n\
\n\
Relaciones: \n\
Clase1-Clase2: multiplicidad_Clase1, multiplicidad_Clase2...\n\
Clase1-Clase2:  multiplicidad_Clase1, multiplicidad_Clase2...\n\
Clase1-Clase2: multiplicidad_Clase1, multiplicidad_Clase2...\n\
...\n'

    texto = requisitos + pregunta
    # print(texto)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=texto,
        temperature=0.7,
        max_tokens=512,
        top_p=0.1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(response.choices[0].text)

    response_prueba = "Clases:\n\
        Biblioteca: nombre, localización, tamaño.\n\
        Libro: título, autor, fecha.\n\
        Revista: marca, semana.\n\
        Estudiante: nombre, apellido, nif.\n\
        Profesor: nombre, apellido, cargo, especialidad.\n\
        Bibliotecario: nombre, dni.\n\n\
        \
        Relaciones:\n\
        Biblioteca-Libro: 1, *\n\
        Biblioteca-Revista: 1, *\n\
        Bibliotecario-Biblioteca: 1, 1\n\
        Estudiante-Libro: *, 1\n\
        Profesor-Revista: *, 1"

    lista_response = response.choices[0].text.split("\n")
    en_clases = False
    en_relaciones = False
    try:
        for i in range(0, len(lista_response)):
            if "Clases:" in lista_response[i]:
                en_clases = True
            elif "Relaciones:" in lista_response[i]:
                en_relaciones = True
                en_clases = False
            elif en_clases and lista_response[i] != "" and lista_response[i] != "\n":
                clase_atributos = lista_response[i].split(":")
                clase_bd = Class(name=str.strip(clase_atributos[0]), score=0, run_fk=run)
                clase_bd.save()
                # print("clase: ",str.strip(clase_atributos[0]))
                atributos = clase_atributos[1].split(",")
                for atributo in atributos:
                    attribute_bd = Attribute(name=str.strip(atributo), score=0, run_fk=run, class_fk=clase_bd,
                                             type="varchar(50)")
                    attribute_bd.save()
            elif en_relaciones and lista_response[i] != "" and lista_response[i] != "\n":
                # print(lista_response[i])
                relacion_multiplicidad = lista_response[i].split(":")
                relacion = relacion_multiplicidad[0].split("-")
                multiplicidad = relacion_multiplicidad[1].split(", ")
                relation_bd = Relation(class_fk_1=Class.objects.get(name=str.strip(relacion[0]), run_fk=run),
                                       multiplicity_1=str.strip(multiplicidad[0]),
                                       class_fk_2=Class.objects.get(name=str.strip(relacion[1]), run_fk=run),
                                       multiplicity_2=str.strip(multiplicidad[1]), run_fk=run)

                relation_bd.save()
    except:
        # gpt3(requisitos, run)
        print("error")


def homepage(request):
    return render(request, "main/index.html")


@login_required(login_url='/login')
def dashboard(request):
    actual_user = request.user

    runs = Run.objects.filter(user_fk__username=actual_user).filter(deleted=False)

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
            return render(request, "main/diagrama.html", context)

    return render(request, "main/form.html")


@login_required(login_url='/login')
def diagrama_gpt3(request):
    if request.method == 'POST':
        if request.POST["texto"]:
            documento = request.POST["texto"]
            run = Run(text=documento, run_datetime=datetime.datetime.now(), user_fk=request.user)
            run.save()
            gpt3(documento, run)

            classes = Class.objects.filter(run_fk=run)
            attributes = Attribute.objects.filter(run_fk=run)
            relations = Relation.objects.filter(run_fk=run)

            context = {"requirements": documento, "classes": classes, "attributes": attributes, "relations": relations}

            return render(request, "main/diagrama.html", context)

    return render(request, "main/form_gpt3.html", {"key": os.getenv("STRIPE_PUBLISHABLE_KEY"), "user": request.user,
                                                   "peticiones": UserExtras.objects.get(user_fk=request.user).peticiones})


@login_required(login_url='/login')
def payment(request):
    if request.method == "POST":
        userExtras = UserExtras.objects.get(user_fk=request.user)
        userExtras.peticiones += 10
        userExtras.save()
        print("pagado")
    return render(request, "main/form_gpt3.html",
                  {"key": os.getenv("STRIPE_PUBLISHABLE_KEY"), "user": request.user, "peticiones": userExtras.peticiones})


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
def run_details(request, run_id):

    try:
        run = Run.objects.filter(user_fk=request.user).get(id=run_id)

        classes = [{"name": c.name, "score": c.score} for c in Class.objects.filter(run_fk=run)]
        attributes = [{"name": a.name, "score": a.score, "type": a.type, "class": a.class_fk.name} for a in
                      Attribute.objects.filter(run_fk=run)]
        relations = [{"class_1": r.class_fk_1.name, "class_2": r.class_fk_2.name, "phrase": r.phrase, "score": r.score}
                     for
                     r in Relation.objects.filter(run_fk=run)]

        context = {"requirements": run.text, "classes": classes, "attributes": attributes, "relations": relations}
        return render(request, "main/run_datails.html", context)
    except:
        runs = Run.objects.filter(user_fk__username=request.user).filter(deleted=False)

        context = {"runs": runs}
        return render(request, "main/dashboard.html", context)


@login_required(login_url='/login')
def delete_run(request, run_id):
    try:
        run = Run.objects.filter(user_fk=request.user).get(id=run_id)

        run.deleted = True

        run.save()

        runs = Run.objects.filter(user_fk__username=request.user).filter(deleted=False)
        context = {"runs": runs}
        return render(request, "main/dashboard.html", context)
    except:
        return render(request, "main/dashboard.html", context)
