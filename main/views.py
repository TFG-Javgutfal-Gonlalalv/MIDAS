from django.shortcuts import render
import spacy
from main.reglas import class_detection_rules
from main.utils import get_success_rate_classes, get_success_rate_attributes, update_log
# Create your views here.

def get_general(request):
    nlp = spacy.load("es_core_news_lg")

    num = 3
    documento = open("main/docs/doc" + str(num), "r", encoding="utf-8").read()

    doc = nlp(documento)
    classes = class_detection_rules(doc)

    print("\n")

    solucion = ""
    for clase in classes:
        solucion += (clase.__str__())
        solucion += "\n\n"

    print("\n")
    class_rate = get_success_rate_classes(num, classes)
    attribute_rate = get_success_rate_attributes(num, classes)
    relationship_rate = 0.0

    general_rate = (class_rate + attribute_rate + relationship_rate) / 3

    print('El porcentaje de acierto en clases es del ', class_rate)
    print('El porcentaje de acierto en atributos es del ', attribute_rate)

    print('El porcentaje de acierto global es del ', general_rate)

    update_log('main/logs/success_rate_historial_log.txt',
               {'doc': 'doc' + str(num),
                'class_rate': class_rate,
                'attribute_rate': attribute_rate,
                'relationship_rate': relationship_rate,
                'general_rate': general_rate})

    #show_success_rate_chart(class_rate, attribute_rate, relationship_rate, general_rate)

    context = {"requirements": documento, "solutions": solucion,"class_rate": class_rate,"attribute_rate": attribute_rate, "relationship_rate": relationship_rate, "general_rate": general_rate}
    return render(request, "main/main.html", context)

