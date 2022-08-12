import json
import datetime

from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.renderers import JSONRenderer, HTMLFormRenderer
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from main.converter import convertir_run_codigo_sql
from main.models import Run, UserExtras
from main.views import gpt3
from main.nlpcd import ejecucion_sin_solucion
from main.utils import runToJson


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRuns(request):
    data = list(Run.objects.filter(user_fk=request.user).values_list("id", flat=True))

    return HttpResponse(json.dumps(data, indent=4, sort_keys=True), content_type="application/json")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRunInSQL(request, run_id):
    try:
        run = Run.objects.filter(user_fk=request.user).get(id=run_id)
        return HttpResponse(convertir_run_codigo_sql(run), content_type="application/json")

    except:
        return Response("No existe esa run o no pertenece al usuario logeado")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRun(request, run_id):
    if request.method == 'GET':
        try:
            return runToJson(request, run_id)

        except BaseException as err:
            print(err)
            return Response("No existe esa run o no pertenece al usuario logeado")


@api_view(['DELETE'])
@permission_classes(IsAuthenticated)
def deleteRun(request, run_id):
    if request.method == "DELETE":
        try:
            run = Run.objects.filter(user_fk=request.user).get(id=run_id)
            if run.deleted == True:
                return Response("Run " + str(run_id) + " ya ha sido eliminada previamente")
            run.deleted = True
            run.save()

            return Response("Run " + str(run_id) + " ha sido eliminada")

        except BaseException as err:
            print(err)
            return Response("No se ha podido eliminar la run")


class TextPlainAutoSchema(SwaggerAutoSchema):
    def get_consumes(self):
        return ["text/plain"]


@swagger_auto_schema(method='POST', auto_schema=TextPlainAutoSchema,
                     request_body=openapi.Schema('requisitos', "Indique aquí los requisitos", type=openapi.TYPE_STRING)
    ,
                     )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, HTMLFormRenderer])
def nlp(request):
    if request.method == "POST":
        try:
            if request.body:
                #print(request.body.decode('utf-8', 'ignore'))
                documento = request.body.decode('utf-8', 'ignore')
                run = ejecucion_sin_solucion(documento, request.user)

                return runToJson(request,run.id)

        except BaseException as err:
            print(err)
            return Response("No se ha podido ejecutar correctamente el algoritmo nlp")

@swagger_auto_schema(method='POST', auto_schema=TextPlainAutoSchema,
                     request_body=openapi.Schema('requisitos', "Indique aquí los requisitos", type=openapi.TYPE_STRING)
    ,
                     )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, HTMLFormRenderer])
def ejecutar_gpt3(request):
    if request.method == "POST":
        try:
            if request.body:
                if UserExtras.objects.get(user_fk=request.user).peticiones < 1:
                    return Response("Adquiera más peticiones en la web")
                documento = request.body.decode('utf-8', 'ignore')
                run = Run(text=documento, run_datetime=datetime.datetime.now(), user_fk=request.user)
                run.save()
                gpt3(documento, run)

                userExtras = UserExtras.objects.get(user_fk=request.user)
                userExtras.peticiones -= 1
                userExtras.save()

                return runToJson(request,run.id)

        except BaseException as err:
            print(err)
            return Response("No se ha podido ejecutar correctamente el algoritmo gpt3")

@swagger_auto_schema(method='post', request_body=openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'username': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='string'),
    }
))
@api_view(['POST'])
def login(request):
    json_data = json.loads(request.body)

    username = json_data["username"]
    password = json_data["password"]

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response("Usuario inválido")

    pwd_valid = check_password(password, user.password)

    if not pwd_valid:
        return Response("Contraseña inválida")

    token, _ = Token.objects.get_or_create(user=user)

    return Response("Token " + token.key)
