import difflib
import datetime
import json
import os

from django.http import HttpResponse

from main.clases import Class
from main.models import Class, Attribute, Relation, FrequentAttributes, Run


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


def creation_clasess_attributes_relations(clasess, relations, run):
    for clase in clasess:

        clase_bd = Class(name=clase.name, score=clase.percent, run_fk=run)
        clase_bd.save()

        for attribute in clase.attributes.items():
            type = "String"
            if attribute[0].name in list(FrequentAttributes.objects.values_list("name", flat=True)):
                index = list(FrequentAttributes.objects.values_list("name", flat=True)).index(attribute[0].name)
                type = list(FrequentAttributes.objects.values_list("name", "type"))[index][1]
            attribute_bd = Attribute(name=attribute[0].name, score=attribute[1], run_fk=run, class_fk=clase_bd,
                                     type=type)
            attribute_bd.save()

    for relation in relations:
        if relation.multiplicity == "1..*":
            relation_bd = Relation(class_fk_1=Class.objects.get(name=relation.class1.name, run_fk=run),
                                   multiplicity_1="1",
                                   class_fk_2=Class.objects.get(name=relation.class2.name, run_fk=run),
                                   multiplicity_2="*", verb=relation.verb,
                                   phrase=relation.phrase, run_fk=run)
        else:
            relation_bd = Relation(class_fk_1=Class.objects.get(name=relation.class1.name, run_fk=run),
                                   class_fk_2=Class.objects.get(name=relation.class2.name, run_fk=run),
                                   verb=relation.verb,
                                   phrase=relation.phrase, run_fk=run)

        relation_bd.save()


def runToJson(request, run_id):
    run = Run.objects.filter(user_fk=request.user).get(id=run_id)
    classes = run.class_set.all()
    jsonData = '{"clases": ['
    for clase in classes:
        atributos = list(clase.attribute_set.values_list("name", flat=True))
        atributos = str(atributos)
        atributos = atributos.replace("'", '"')
        print(atributos)
        jsonData += '{ "' + clase.name + '":' + atributos

        jsonData += '},'
    jsonData = jsonData[:-1]
    jsonData += "],"
    relaciones = run.relation_set.all()
    jsonData += '"relaciones": ['
    for relacion in relaciones:
        jsonData += ' "' + relacion.class_fk_1.name + ' - ' + relacion.class_fk_2.name + '",'
    jsonData = jsonData[:-1]
    url = os.getenv("APP_HEROKU_URL") or "127.0.0.1:8000"
    jsonData += '], "url": "' + url + '/run/' + str(run.id) + '"}'
    print(jsonData)
    jsonToPython = json.loads(jsonData)
    return HttpResponse(json.dumps(jsonToPython), content_type="application/json")