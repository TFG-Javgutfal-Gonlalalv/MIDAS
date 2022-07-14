import datetime

import spacy

from main.clases import Class, Attribute
from main.models import Class, Attribute, Run, User
from main.reglas import class_detection_rules
from main.utils import get_success_rate_classes, get_success_rate_attributes, creation_clasess_attributes_relations, \
    update_log


def ejecucion(docIn, num):
    nlp = spacy.load("es_core_news_lg")
    user = User.objects.get(name="test")
    doc = nlp(docIn)

    run = Run(text=docIn, run_datetime=datetime.datetime.now(), user_fk=user)
    run.save()

    classes, relations = class_detection_rules(doc)

    class_rate = get_success_rate_classes(num, classes)
    attribute_rate = get_success_rate_attributes(num, classes)
    relationship_rate = 0.0

    general_rate = (class_rate + attribute_rate + relationship_rate) / 3
    creation_clasess_attributes_relations(classes, relations, run)

    update_log('main/logs/success_rate_historial_log.txt',
               {'class_rate': class_rate,
                'attribute_rate': attribute_rate,
                'relationship_rate': relationship_rate,
                'general_rate': general_rate})

    # show_success_rate_chart(class_rate, attribute_rate, relationship_rate, general_rate)

    return run, class_rate,attribute_rate, relationship_rate, general_rate
