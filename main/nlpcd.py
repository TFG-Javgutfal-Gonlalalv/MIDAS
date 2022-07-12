import datetime

import spacy

from main.models import Class, Attribute, Run, User
from main.reglas import class_detection_rules
from main.utils import get_success_rate_classes, get_success_rate_attributes, show_success_rate_chart, update_log


def ejecucion(docIn,num):
    nlp = spacy.load("es_core_news_lg")
    user = User.objects.get(name="test")
    doc = nlp(docIn)

    run = Run(text=docIn,run_datetime=datetime.datetime.now(), user_fk=user)
    run.save()


    classes = class_detection_rules(doc, run)

    print("\n")
    for clase in classes:
        print(clase.__str__())

    print("\n")
    class_rate = get_success_rate_classes(num, classes)
    attribute_rate = get_success_rate_attributes(num, classes)
    relationship_rate = 0.0

    general_rate = (class_rate + attribute_rate + relationship_rate) / 3

    print('El porcentaje de acierto en clases es del ', class_rate)
    print('El porcentaje de acierto en atributos es del ', attribute_rate)

    print('El porcentaje de acierto global es del ', general_rate)

    update_log('main/logs/success_rate_historial_log.txt',
               {'class_rate': class_rate,
                'attribute_rate': attribute_rate,
                'relationship_rate': relationship_rate,
                'general_rate': general_rate})

    #show_success_rate_chart(class_rate, attribute_rate, relationship_rate, general_rate)

    return run