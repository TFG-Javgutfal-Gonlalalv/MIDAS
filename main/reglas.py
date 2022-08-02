import main.models
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
    nlp = spacy.load("es_core_news_md")
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

    # Regla 3 - Listado por cercanía
    # for phrase in phrases:

    # Regla 2 detector preposiciones
    for phrase in phrases:
        attributes_return, classes_update, attributes_update = \
            detector_lista_atributos_frase(nlp(phrase), classes, attributes, attributes_list)
        classes_final = classes_update
        attributes = attributes_update

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


def detector_lista_atributos_frase(phrase, classes, attributes, attributes_list):
    index_y = 0
    words = []
    atributos_return = []
    classes_return = []
    if "," not in phrase.text and "y" in phrase.text:

        for token in phrase:
            if token.text == "y":
                index_y = token.i
                break

        words.append(phrase[index_y - 1].lemma_)
        words.append(phrase[index_y + 1].lemma_)

    elif "," in phrase.text and "y" in phrase.text:

        index_y = 0
        words = []
        for token in phrase:
            if token.text == "y":
                index_y = token.i
                break

        words.append(phrase[index_y - 1].lemma_)
        words.append(phrase[index_y + 1].lemma_)

        index_y -= 2
        while index_y > 0:
            if phrase[index_y].text == ",":
                words.append(phrase[index_y - 1].lemma_)
                index_y -= 2
            else:
                break

    if len(words) > 0:
        tam = len(list(set(words).intersection(set(attributes_list))))
        if len(list(set(words).intersection(set(attributes_list)))) > 0:
            for clase in classes:
                if clase.name in words:
                    clase.update_percent(-100 * tam / len(words))
                if clase.percent > 0:
                    classes_return.append(clase)
            for attribute in attributes:
                if attribute.name in words:
                    atributos_return.append(attribute)
    return atributos_return, classes_return, attributes


def clases_atributos_preposiciones(phrase, preps, classes, attributes, attributes_list):
    for prep in preps:
        # print("phrase: ", phrase, " preposicion: ", prep)
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
        # print("clase_objetivo: ",clase_objetivo, "after: ", after)
        if clase_objetivo is not None:
            for attribute in attributes:

                if attribute.name in before.text and attribute.name not in list(map(lambda x: x.name, classes)):
                    attribute_found = True
                    if attribute.name in attributes_list:
                        clase_objetivo.add_update_attribute(attribute, 50)
                    else:
                        clase_objetivo.add_update_attribute(attribute, 10)
        if clase_objetivo is not None and attribute_found:
            # print("phrase: ",phrase, " preposicion: ", prep)
            break
    return classes, attributes


def relations_detections(classes, doc):
    phrases = doc.text.split(".")
    nlp = spacy.load("es_core_news_md")
    relations = []

    for phrase in phrases:
        first_class = None
        verb = None
        second_class = None
        third_class = None
        composicion = False
        second_class_id = None
        phrase_nlp = nlp(phrase)

        for token in phrase_nlp:
            # print(token.pos_, token.dep_, token.lemma_)
            if token.pos_ == "NOUN" and token.dep_ == "nsubj" and first_class == None and token.lemma_ in classes:
                first_class = classes[classes.index(token.lemma_)]
            if (token.pos_ == "VERB" and (
                    token.dep_ == "ROOT" or token.dep_ == "acl")) and token.lemma_ != "querer" and token.lemma_ != "desear":
                verb = token.lemma_
                if verb == "contener":
                    composicion = True
            if (token.pos_ == "NOUN" and (
                    token.dep_ == "obj" or token.dep_ == "nsubj") and token.lemma_ in classes and second_class is None):
                if first_class is not None and first_class.name != token.lemma_:
                    second_class = classes[classes.index(token.lemma_)]
                    second_class_id = token.i
                    break

        if first_class is not None and verb is not None and second_class is not None:

            #Regla 2 AND
            if second_class_id+1 < len(phrase_nlp) and phrase_nlp[second_class_id + 1].text == "y":
                t = phrase_nlp[second_class_id + 2]
                print("frase: ",phrase, "  t: ", t, " pos: ", t.pos_, " dep: ", t.dep_)
                if (t.pos_ == "NOUN" and (
                        t.dep_ == "obj" or t.dep_ == "nsubj" or t.dep_ == "conj") and t.lemma_ in classes
                        and second_class.name != t.lemma_ and first_class.name != t.lemma_):
                    third_class = classes[classes.index(t.lemma_)]

            if third_class is None:
                if composicion:
                    relations.append(Relation(first_class, second_class, verb, phrase, "1..*"))
                else:
                    relations.append(Relation(first_class, second_class, verb, phrase, "None"))
            else:
                if composicion:
                    relations.append(Relation(first_class, second_class, verb, phrase, "1..*"))
                    relations.append(Relation(first_class, third_class, verb, phrase, "1..*"))
                else:
                    relations.append(Relation(first_class, second_class, verb, phrase, "None"))
                    relations.append(Relation(first_class, third_class, verb, phrase, "None"))

    # print(relations)
    return relations
