from main.utils import get_key_words
from main.clases import Class, Attribute, Relation
from main.models import Technicality, FrequentAttributes, Prepositions
import spacy


def lista_locs(doc):
    lista = []
    for ent in doc.ents:
        if ent.label_ is not None:
            if ent.label_ == "LOC" or ent.label_ == "ORG":
                lista.append(ent.text)
    return lista


def class_detection_rules(doc):
    nlp = spacy.load("es_core_news_lg")
    lista_preposiciones = list(Prepositions.objects.values_list("name", flat=True))

    nouns = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.pos_ == "NOUN"]

    words = nouns.copy()
    words_final = nouns.copy()
    technicalities = list(Technicality.objects.values_list("name", flat=True))
    attributes_list = list(FrequentAttributes.objects.values_list("name", flat=True))
    classes = []
    attributes = []

    # Reglas para la detección de clases
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

    # Regla 5 Como quiero para
    for phrase in phrases:
        if "Como" in phrase and ("quiero" in phrase or "deseo" in phrase):
            final = "quiero"
            if "deseo" in phrase:
                final = "deseo"

            for clase in classes:
                if clase.name in phrase[0:phrase.index(final)]:
                    clase.update_percent(20)

    # Reglas de atributos
    classes_final = []
    for clase in classes:
        if clase.percent >= 0:
            classes_final.append(clase)

    # Regla 1 detector atributos y clase tras ":"
    for phrase in phrases:
        clase_objetivo = None
        if ":" in phrase:
            for clase in classes_final:
                if clase.name in phrase[0:phrase.index(":")]:
                    clase.update_percent(20)
                    clase_objetivo = clase

                    if clase_objetivo is not None:
                        for attribute in attributes:
                            if attribute.name in phrase[phrase.index(":"):len(phrase)]:
                                clase_objetivo.add_update_attribute(attribute, 20)
                                list_classes = [x for x in classes_final if x.name == attribute.name]
                                if len(list_classes) > 0:
                                    el = list_classes[0]
                                    el.update_percent(-50)
    for clase in classes:
        if clase.percent >= 0:
            classes_final.append(clase)

    # Regla 2 detector preposiciones
    for phrase in phrases:
        list_of_prepositions_in_phrase = []
        for token in nlp(phrase):
            if token.text.lower() in lista_preposiciones:
                list_of_prepositions_in_phrase.append(token)
        if len(list_of_prepositions_in_phrase) > 0:
            classes_return, attributes_return = \
                clases_atributos_preposiciones(nlp(phrase), list_of_prepositions_in_phrase, classes_final,
                                               attributes, attributes_list)
            classes_final = classes_return
            attributes = attributes_return

    #Regla 3 - Listado por cercanía

    # Regla 4 Resto de atributos
    for phrase in phrases:
        for attribute in attributes:
            if attribute.name in phrase and attribute.name in attributes_list:
                pos_atributo = phrase.index(attribute.name)
                min_pos = 100000
                clase_objetivo = None
                # print(attribute.name, " --- ", pos_atributo)
                for clase in classes:
                    if clase.name in phrase:
                        # print(clase.name, " - ",  phrase.index(clase.name))
                        cantidad = phrase.count(clase.name)
                        if cantidad == 1:
                            if abs(phrase.index(clase.name) - pos_atributo) < min_pos:
                                min_pos = abs(phrase.index(clase.name) - pos_atributo)
                                clase_objetivo = clase
                        else:
                            indice = phrase.index(clase.name)
                            for i in range(1, cantidad):
                                if abs(indice - pos_atributo) < min_pos:
                                    min_pos = abs(indice - pos_atributo)
                                    clase_objetivo = clase
                                indice = phrase.index(clase.name, indice + 1)

                if clase_objetivo is not None:
                    clase_objetivo.add_update_attribute(attribute, 20)

    classes_final = []
    for clase in classes:
        if clase.percent >= 0:
            classes_final.append(clase)
    relations_final = relations_detections(classes_final, doc)
    return classes_final, relations_final


def detector_lista_atributos_frase(phrase,classes,attributes,attributes_list):

    if "," not in phrase and "y" in phrase:
        index_y = 0
        words = []
        for token in phrase:
            if token == "y":
                index_y = token.i
                break

        words.append(phrase[index_y - 1])
        words.append(phrase[index_y + 1])

    elif "," in phrase and "y" in phrase:

        index_y = 0
        words = []
        for token in phrase:
            if token == "y":
                index_y = token.i
                break

        words.append(phrase[index_y - 1])
        words.append(phrase[index_y + 1])

        index_y -= 2
        while index_y > 0:
            if phrase[index_y].text == ",":
                words.append(phrase[index_y-1])
                index_y -= 2

    print(words)

def clases_atributos_preposiciones(phrase, preps, classes, attributes, attributes_list):
    for prep in preps:
        print("phrase: ", phrase, " preposicion: ", prep)
        attribute_found = False
        if prep.i - 10 > 0:
            before = phrase[prep.i - 10:prep.i]
        else:
            before = phrase[0:prep.i]
        if prep.i + 5 > len(phrase):
            after = phrase[prep.i:len(phrase)]
        else:
            after = phrase[prep.i: prep.i + 5]

        clase_objetivo = None

        for clase in classes:
            if clase.name in after.text:
                clase_objetivo = clase
                clase_objetivo.update_percent(10)
        print("clase_objetivo: ",clase_objetivo, "after: ", after)
        if clase_objetivo is not None:
            for attribute in attributes:

                if attribute.name in before.text and attribute.name not in list(map(lambda x: x.name, classes)):
                    attribute_found = True
                    if attribute.name in attributes_list:
                        clase_objetivo.add_update_attribute(attribute, 50)
                    else:
                        clase_objetivo.add_update_attribute(attribute, 10)
        if clase_objetivo is not None and attribute_found:
            print("phrase: ",phrase, " preposicion: ", prep)
            break
    return classes, attributes


def relations_detections(classes, doc):
    phrases = doc.text.split(".")
    nlp = spacy.load("es_core_news_lg")
    relations = []

    for phrase in phrases:
        first_class = None
        verb = None
        second_class = None

        for token in nlp(phrase):
            # print(token.pos_, token.dep_, token.lemma_)
            if (token.pos_ == "NOUN" and token.dep_ == "nsubj" and first_class == None and token.lemma_ in classes):
                first_class = classes[classes.index(token.lemma_)]
            if (token.pos_ == "VERB" and (
                    token.dep_ == "ROOT" or token.dep_ == "acl")) and token.lemma_ != "querer" and token.lemma_ != "desear":
                verb = token.lemma_
            if (token.pos_ == "NOUN" and (
                    token.dep_ == "obj" or token.dep_ == "nsubj") and token.lemma_ in classes and second_class == None):
                if first_class != None and first_class.name != token.lemma_:
                    second_class = classes[classes.index(token.lemma_)]

        if (first_class != None and verb != None and second_class != None):
            relations.append(Relation(first_class, second_class, verb, phrase))

    # print(relations)
    return relations
