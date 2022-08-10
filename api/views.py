import json

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer

from main.converter import convertir_run_codigo_sql
from main.models import Run

@api_view(['GET'])
def getRuns(request):
    permission_classes = [IsAuthenticated]

    data = list(Run.objects.filter(user_fk=request.user).values_list("id", flat=True))

    return HttpResponse(json.dumps(data, indent=4, sort_keys=True), content_type="application/json")

@api_view(['GET'])
def getRunInSQL(request, run_id):
    permission_classes = [IsAuthenticated]
    run = Run.objects.get(id=run_id)

    return HttpResponse(convertir_run_codigo_sql(run), content_type="application/json")


@api_view(['POST'])
def login(request):
    username = request.POST.get("username")
    password = request.POST.get("password")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response("Usuario inválido")

    pwd_valid = check_password(password, user.password)

    if not pwd_valid:
        return Response("Contraseña inválida")

    token, _ = Token.objects.get_or_create(user=user)

    return Response(token.key)
