import difflib
import matplotlib.pyplot as plt
import datetime


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
    f = open('solution_tests/sol_doc' + str(doc_num) + '.txt', 'r', encoding='utf-8')
    solution_test = f.read().split("\n")

    class_sol = [line.split(':')[0] for line in solution_test]
    class_names = [c.name for c in classes]

    sm = difflib.SequenceMatcher(None, sorted(class_sol), sorted(class_names))
    return sm.ratio()


def get_success_rate_attributes(doc_num: int, classes: list) -> float:
    f = open('solution_tests/sol_doc' + str(doc_num) + '.txt', 'r', encoding='utf-8')
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
