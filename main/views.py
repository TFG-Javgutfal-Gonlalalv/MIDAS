from django.shortcuts import render
import spacy
#from reglas import class_detection_rules
#from utils import get_success_rate_classes, get_success_rate_attributes, show_success_rate_chart, update_log
# Create your views here.

#from utils import get_key_words
#from clases import Class, Attribute

import difflib
#import matplotlib.pyplot as plt
import datetime

class Class:
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.percent = 0

    def add_update_attribute(self, attribute, percent):
        if attribute.name not in str(self.attributes.keys()):
            self.attributes[attribute] = percent
        else:
            self.attributes[attribute] += percent

    def update_percent(self, percent):
        self.percent += percent

    def __str__(self):
        attributes = []
        for i in self.attributes:
            attributes.append(i.name)
        return self.name + "(" + str(self.percent) + ")" + ": " + str(attributes)

    def __eq__(self, name):
        return self.name == name

    def __hash__(self):
        return hash(self.name)


class Attribute:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, name):
        return self.name == name

    def __hash__(self):
        return hash(self.name)

def get_key_words(file: str) -> set:
    f = open(file, 'r', encoding='utf-8')
    key_words = f.read().split("\n")
    return key_words


def show_success_rate_chart(class_rate: float, attribute_rate: float, relationship_rate: float, general_rate: float):
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 0.8, 0.8])
    items = ['Class', 'Attributes', 'Relationships', 'General']
    values = [class_rate * 100, attribute_rate * 100, relationship_rate * 100, general_rate * 100]
    ax.bar(items, values)
    plt.show()


def update_log(file: str, data: dict):
    """
    Función para actualizar los logs de la aplicación, se recomienda introducir en el primer valor del data el valor
    del documento probado, para mejor legibilidad en el futuro

    :param file: Log a acutalizar
    :param data: Diccionario con los datos que se desea imprimir
    """
    f = open(file, 'a', encoding='utf-8')
    f.write(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + ' -> ')

    for key in data.keys():
        f.write(str(key) + ': ' + str(data.get(key)) + ' | ')

    f.write('\n')


def get_success_rate_classes(doc_num: int, classes: list) -> float:
    f = open('main/solution_tests/sol_doc' + str(doc_num) + '.txt', 'r', encoding='utf-8')
    solution_test = f.read().split("\n")

    class_sol = [line.split(':')[0] for line in solution_test]
    class_names = [c.name for c in classes]

    sm = difflib.SequenceMatcher(None, sorted(class_sol), sorted(class_names))
    return sm.ratio()


def get_success_rate_attributes(doc_num: int, classes: list) -> float:
    f = open('main/solution_tests/sol_doc' + str(doc_num) + '.txt', 'r', encoding='utf-8')
    solution_test = f.read().split("\n")

    # Obtenemos los atributos correctos del test de la solución
    attributes_sol = set()
    for line in solution_test:
        attributes = line.split(':')[1].replace('[', '').replace(']', '').split(',')
        if '' not in attributes:
            attributes_sol.update(attributes)

    # Obtenemos los atributos obtenidos tras el análisis de los requisitos
    attribute_names = set()
    for c in classes:
        for a in set(c.attributes.keys()):
            attribute_names.add(a.name)

    sm = difflib.SequenceMatcher(None, sorted(attributes_sol), sorted(attribute_names))
    return sm.ratio()


def lista_locs(doc):
    lista = []
    for ent in doc.ents:
        if ent.label_ is not None:
            if ent.label_ == "LOC" or ent.label_ == "ORG":
                lista.append(ent.text)
    return lista


def class_detection_rules(doc):
    nouns = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.pos_ == "NOUN" ]

    words = nouns.copy()
    words_final = nouns.copy()
    technicalities = get_key_words("main/key_words/tecnicismos.txt")
    attributes_list = get_key_words("main/key_words/atributos.txt")
    classes = []
    attributes = []
    for word in words:
        value = nouns.count(word)

        clase = Class(word)
        attribute = Attribute(word)

        # Rule 1: Infrequent words
        if value == 1 and float(value / len(words)) < 0.02:
            clase.update_percent(-10)
        else:
            clase.update_percent(+10)

        # Rule 2: Technicalities
        if word.lower() in technicalities:
            clase.update_percent(-100)
        else:
            clase.update_percent(+10)

        # Rule 3: Attributes

        if word.lower() in attributes_list:
            clase.update_percent(-100)
        else:
            clase.update_percent(+10)

        # Rule 4: Si la palabra es una localización u organización ignorarla
        if word in lista_locs(doc):
            clase.update_percent(-100)
        else:
            clase.update_percent(+10)

        if clase.percent >= 0:
            classes.append(clase)
            classes = list(set(classes))

        attributes.append(Attribute(word))
        attributes = list(set(attributes))
    phrases = doc.text.split(".")

    #detector atributos y clase tras ":"

    for phrase in phrases:
        clase_objetivo = None
        if ":" in phrase:
            for clase in classes:
                if clase.name in phrase[0:phrase.index(":")]:
                    clase.update_percent(20)
                    clase_objetivo = clase

            for attribute in attributes:
                if attribute.name in phrase[phrase.index(":"):len(phrase)]:
                    clase_objetivo.add_update_attribute(attribute,20)
                    list_classes = [x for x in classes if x.name == attribute.name]
                    if len(list_classes) > 0:
                        el = list_classes[0]
                        el.update_percent(-50)

    classes_final = []
    for clase in classes:

        if clase.percent >= 0:
            classes_final.append(clase)

    for phrase in phrases:
        if "de cada" in phrase:
            before = phrase[0:phrase.index("de cada")]
            after = phrase[phrase.index("de cada"):len(phrase)]
            clase_objetivo = None

            for clase in classes:
                if clase.name in after:
                    clase_objetivo = clase
                    clase_objetivo.update_percent(10)
            for attribute in attributes:

                if attribute.name in before:
                    if attribute.name in attributes_list:
                        clase_objetivo.add_update_attribute(attribute,50)
                    else:
                        clase_objetivo.add_update_attribute(attribute,20)

    for phrase in phrases:
        for attribute in attributes:
                if attribute.name in phrase and attribute.name in attributes_list:
                    pos_atributo = phrase.index(attribute.name)
                    min_pos = 100000
                    clase_objetivo = None
                    #print(attribute.name, " --- ", pos_atributo)
                    for clase in classes:
                        if clase.name in phrase:
                            #print(clase.name, " - ",  phrase.index(clase.name))
                            if abs(phrase.index(clase.name) - pos_atributo) < min_pos:
                                min_pos = abs(phrase.index(clase.name) - pos_atributo)
                                clase_objetivo = clase

                    if clase_objetivo is not None:
                        clase_objetivo.add_update_attribute(attribute,20)


    return classes_final


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

