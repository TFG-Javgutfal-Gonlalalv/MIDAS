from django.shortcuts import render
import spacy
from main.nlpcd import ejecucion
from main.models import Class
from main.utils import get_success_rate_classes, get_success_rate_attributes, update_log
# Create your views here.

def get_general(request):
    num = 3
    documento = open("main/docs/doc" + str(num), "r", encoding="utf-8").read()
    run = ejecucion(documento,num)

    classes = Class.objects.filter(run_fk=run)
    class_rate = get_success_rate_classes(num, classes)
    attribute_rate = get_success_rate_attributes(num, classes)
    relationship_rate = 0.0

    general_rate = (class_rate + attribute_rate + relationship_rate) / 3
    for clase in classes:
        print(clase)

    context = {"requirements": documento, "solutions": classes.values_list(),"class_rate": class_rate,"attribute_rate": attribute_rate, "relationship_rate": relationship_rate, "general_rate": general_rate}
    return render(request, "main/main.html", context)

