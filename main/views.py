import datetime
import json
import difflib
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.template import RequestContext
from main.nlpcd import ejecucion, ejecucion_sin_solucion
from main.models import Class, Attribute, Relation, Run, FrequentAttributes, UserExtras
from main.converter import convertir_run_codigo_sql
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout  # add this
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm  # add this

from django.http import HttpResponse
import os
import openai
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

def docs(request):
    return render(request=request, template_name="main/docs.html")


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


def gpt3(requisitos, run, intento,request):
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
...\n\n \
Clases:\n'\

    texto = requisitos + pregunta
    # print(texto)
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=texto,
        temperature=0.7,
        max_tokens=3000,
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

    lista_response =["Clases:"]
    lista_response.extend(response.choices[0].text.split("\n"))
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
                                             type="String")
                    attribute_bd.save()
            elif en_relaciones and lista_response[i] != "" and lista_response[i] != "\n":
                # print(lista_response[i])
                relacion_multiplicidad = lista_response[i].split(":")
                relacion = relacion_multiplicidad[0].split("-")
                multiplicidad = relacion_multiplicidad[1].split(", ")
                class_fk1 = Class.objects.get(name=str.strip(relacion[0]), run_fk=run)
                class_fk2 = Class.objects.get(name=str.strip(relacion[1]), run_fk=run)
                multiplicidad_1 = str.strip(multiplicidad[0])
                multiplicidad_2 = str.strip(multiplicidad[1])
                relation_bd = Relation(class_fk_1= class_fk1,
                                       multiplicity_1=multiplicidad_1,
                                       class_fk_2= class_fk2,
                                       multiplicity_2=multiplicidad_2, run_fk=run,

                                       phrase= ""+Class.objects.get(name=str.strip(relacion[0]), run_fk=run).name
                                               + '_' + str.strip(multiplicidad[0]) + '---' \
                              + Class.objects.get(name=str.strip(relacion[1]), run_fk=run).name + '_' + str.strip(multiplicidad[1]))

                relation_bd.save()
    except:

        if intento > 3:
            userExtras = UserExtras.objects.get(user_fk=request.user)
            userExtras.peticiones += 1
            userExtras.save()

            run = ejecucion_sin_solucion(requisitos, request.user)

            return run_details(request, run.id)
        else:
            gpt3(requisitos, run,intento+1)
        print("error")


def homepage(request):
    return render(request, "main/index.html")


@login_required(login_url='/login')
def dashboard(request):
    actual_user = request.user

    runs = Run.objects.filter(user_fk=actual_user, run_fk=None).filter(deleted=False)
    context = {"runs": runs}

    return render(request, "main/dashboard.html", context)


@login_required(login_url='/login')
def diagrama(request):
    if request.method == 'POST':
        if request.POST["texto"]:
            documento = request.POST["texto"]
            run = ejecucion_sin_solucion(documento, request.user)

            return run_details(request, run.id)

    return render(request, "main/form.html")


@login_required(login_url='/login')
def diagrama_gpt3(request):
    if request.method == 'POST':
        if request.POST["texto"]:
            if UserExtras.objects.get(user_fk=request.user).peticiones < 1:
                return render(request, "main/form_gpt3.html", {"key": os.getenv("STRIPE_PUBLISHABLE_KEY"), "user": request.user,
                                                   "peticiones": UserExtras.objects.get(user_fk=request.user).peticiones})
            documento = request.POST["texto"]
            run = Run(text=documento, run_datetime=datetime.datetime.now(), type="GPT-3", user_fk=request.user)
            run.save()
            gpt3(documento, run, 0, request)

            userExtras = UserExtras.objects.get(user_fk=request.user)
            userExtras.peticiones -= 1
            userExtras.save()

            classes = Class.objects.filter(run_fk=run)
            attributes = Attribute.objects.filter(run_fk=run)
            relations = Relation.objects.filter(run_fk=run)

            context = {"requirements": documento, "classes": classes, "attributes": attributes, "relations": relations}

            return run_details(request, run.id)

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

        if run.run_fk is not None:
            runs = Run.objects.filter(user_fk=request.user, run_fk=None).filter(deleted=False)

            context = {"runs": runs}
            return render(request, "main/dashboard.html", context)

        classes = [{"name": c.name, "score": c.score} for c in Class.objects.filter(run_fk=run)]
        attributes = [{"name": a.name, "score": a.score, "type": a.type, "class": a.class_fk.name} for a in
                      Attribute.objects.filter(run_fk=run)]
        relations = [{"class_1": r.class_fk_1.name, "class_2": r.class_fk_2.name, "phrase": r.phrase, "score": r.score}
                     for
                     r in Relation.objects.filter(run_fk=run)]

        context = {"run_id": run_id, "requirements": run.text, "classes": classes, "attributes": attributes, "relations": relations, "requirements": run.text}
        return render(request, "main/run_datails.html", context)
    except BaseException as err:
        print(err)
        runs = Run.objects.filter(user_fk=request.user, run_fk=None).filter(deleted=False)

        context = {"runs": runs}
        return render(request, "main/dashboard.html", context)


def update_run(request):
    run_id = request.POST['run_id']
    cells = json.loads(request.POST['cells'])
    links = json.loads(request.POST['links'])


    actual_run = Run.objects.get(id=run_id)
    if not actual_run.correcion_manual and actual_run.run_fk is None:
        new_run = Run(text=actual_run.text, user_fk=request.user, run_datetime=datetime.datetime.now(), correcion_manual=True)
        new_run.save()
        actual_run.run_fk = new_run
        actual_run.save()

    else:
        first_run = Run.objects.get(run_fk=run_id)
        new_run = Run(text=actual_run.text, user_fk=request.user, run_datetime=datetime.datetime.now(),
                      correcion_manual=True)
        new_run.save()
        first_run.run_fk = new_run
        first_run.save()

    for cell in cells:
        run_class = Class(name=cell['name'], score=1, run_fk=new_run)
        run_class.save()
        for atribute in cell['attributes']:
            run_attribute = Attribute(name=atribute["name"], type=atribute["type"], run_fk=new_run, class_fk=run_class, score=1)
            run_attribute.save()
    for link in links:
        if "---" not in link["label"]:

            run_relation = Relation(run_fk=new_run, class_fk_1=Class.objects.get(name=link["class_1"], run_fk=new_run)
                        , class_fk_2=Class.objects.get(name=link["class_2"], run_fk=new_run), phrase=link["label"], multiplicity_1=1, multiplicity_2=1)
        else:
            clases = link["label"].split("---")

            run_relation = Relation(run_fk=new_run, class_fk_1=Class.objects.get(name=link["class_1"], run_fk=new_run)
                                    , class_fk_2=Class.objects.get(name=link["class_2"], run_fk=new_run), phrase=link["label"],
                                    multiplicity_1=clases[0].split("_")[1], multiplicity_2=clases[0].split("_")[1])
        run_relation.save()

    delete_run(request, actual_run.id)

    return dashboard(request)


@login_required(login_url='/login')
def delete_run(request, run_id):
    try:
        run = Run.objects.filter(user_fk=request.user).get(id=run_id)

        run.deleted = True

        run.save()

        run_initial = Run.objects.get(user_fk=request.user,run_fk=run_id)
        if run_initial is not None:
            run_initial.run_fk = None
            run_initial.save()

        return dashboard(request)
    except:
        return dashboard(request)

@login_required(login_url='/login')
def venue_text(request, run_id):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename='+str(run_id)+'.sql'

    run = Run.objects.get(user_fk=request.user, id=run_id)

    text = [convertir_run_codigo_sql(run)]
    response.writelines(text)
    return response

@login_required(login_url='/login')
def results(request, run_id):

    run_modificada = Run.objects.get(user_fk=request.user, id=run_id)
    run_inicial = Run.objects.get(user_fk=request.user, run_fk=run_id)


    classes_rate = difflib.SequenceMatcher(None, sorted([c.name.lower()  for c in run_inicial.class_set.all()]), sorted([c.name.lower()  for c in run_modificada.class_set.all()]))
    attribute_rate = difflib.SequenceMatcher(None, sorted([a.name.lower() for a in run_inicial.attribute_set.all()]), sorted([a.name.lower()  for a in run_modificada.attribute_set.all()]))
    relation_rate =  difflib.SequenceMatcher(None, sorted([a.class_fk_1.name.lower()+"-"+a.class_fk_2.name.lower() for a in run_inicial.relation_set.all()]), sorted([a.class_fk_1.name.lower()+"-"+a.class_fk_2.name.lower() for a in run_modificada.relation_set.all()]))

    response = HttpResponse(content_type='text/plain')

    text = [classes_rate.ratio()," ",attribute_rate.ratio(), " ",relation_rate.ratio()]
    response.writelines(text)
    return response