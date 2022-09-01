import datetime

import spacy
#import es_core_news_sm
from main.models import Run
from main.reglas import class_detection_rules
from main.utils import get_success_rate_classes, get_success_rate_attributes, creation_clasess_attributes_relations, \
    update_log

NLP_MODEL = None

def ejecucion(docIn, num, user):
    nlp = spacy.load("es_core_news_md")
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

    return run, class_rate, attribute_rate, relationship_rate, general_rate


def ejecucion_sin_solucion(docIn, user):
    if globals()["NLP_MODEL"]  is None:
        globals()["NLP_MODEL"] = spacy.load("es_core_news_md")

    nlp = globals()["NLP_MODEL"]


    doc = nlp(docIn)

    run = Run(text=docIn, run_datetime=datetime.datetime.now(), user_fk=user)
    run.save()

    classes, relations = class_detection_rules(doc,nlp)

    creation_clasess_attributes_relations(classes, relations, run)

    return run
