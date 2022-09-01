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


def class_detection_rules(doc,nlp):
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

        if word.lower() not in technicalities and word.lower() != "el":
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

    ##### Reglas de atributos #####

    classes_final = []
    for clase in classes:
        if clase.percent >= 0:
            classes_final.append(clase)

    # Regla 0 detector de listas
    for phrase in phrases:
        prep_in_list = False
        list_in_phrase = False

        if len(phrase) < 4:
            break
        list_of_prepositions_in_phrase = []
        for token in nlp(phrase):
            if token.text.lower() in lista_preposiciones:
                list_of_prepositions_in_phrase.append(token)
        attributes_return, classes_update, attributes_update, list_index, list_in_phrase = \
            detector_lista_atributos_frase(nlp(phrase), classes_final, attributes, attributes_list,
                                           list_of_prepositions_in_phrase)
        classes_final = classes_update
        attributes = attributes_update

        # Regla 1 detector preposiciones
        if len(list_of_prepositions_in_phrase) > 0:
            if not list_in_phrase:
                classes_return, attributes_update, prep_in_list = \
                    clases_atributos_preposiciones(nlp(phrase), list_of_prepositions_in_phrase, classes_final,
                                                   attributes, attributes_list)
            else:
                classes_return, prep_in_list = \
                    clases_atributos_preposiciones_list(nlp(phrase), list_of_prepositions_in_phrase, classes_final,
                                                        attributes_list, list_index, attributes_return)
            classes_final = classes_return

        # Regla 2 detector atributos y clase tras ":"

        clase_objetivo = None
        if ":" in phrase:

            for clase in classes_final:
                if clase.name in phrase[0:phrase.index(":")]:
                    clase.update_percent(20)
                    clase_objetivo = clase
                    if clase_objetivo is not None:
                        if not list_in_phrase:
                            for attribute in attributes:
                                if attribute.name in phrase[phrase.index(":"):len(phrase)]:
                                    clase_objetivo.add_update_attribute(attribute, 20)
                                    list_classes = [x for x in classes_final if x.name == attribute.name]
                                    if len(list_classes) > 0:
                                        el = list_classes[0]
                                        el.update_percent(-50)
                        else:
                            if phrase.index(attributes_return[0].name) > phrase.index(":"):
                                for attribute in attributes_return:
                                    clase_objetivo.add_update_attribute(attribute, 20)
                                    list_classes = [x for x in classes_final if x.name == attribute.name]
                                    if len(list_classes) > 0:
                                        el = list_classes[0]
                                        el.update_percent(-50)
        classes = []
        for clase in classes_final:
            if clase.percent >= 0:
                classes.append(clase)

        # Regla 3 Resto de atributos
        if not prep_in_list and ":" not in phrase:
            if not list_in_phrase:
                for attribute in attributes:
                    if attribute.name in phrase and attribute.name in attributes_list:
                        pos_atributo = phrase.index(attribute.name)
                        min_pos = 100000
                        clase_objetivo = None

                        for clase in classes:
                            if clase.name in [token.lemma_ for token in nlp(phrase)]:

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
            else:
                min_pos = 100000
                pos_atributo = phrase.index(attributes_return[0].name)
                for clase in classes:
                    if clase.name in [token.lemma_ for token in nlp(phrase)]:

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
                    for attribute in attributes_return:
                        clase_objetivo.add_update_attribute(attribute, 20)

    classes_final = []
    for clase in classes:
        if clase.percent >= 0:
            classes_final.append(clase)
    relations_final = relations_detections(classes_final, doc,nlp)
    return classes_final, relations_final


def detector_lista_atributos_frase(phrase, classes, attributes, attributes_list, list_of_prepositions):
    index_y = 0
    words = []
    atributos_return = []
    classes_return = []
    to_deleted = []
    final_index_list = 0
    list_phrase = True
    if "," not in phrase.text and "y" in phrase.text:

        for token in phrase:
            if token.text == "y":
                index_y = token.i
                break

        words.append(phrase[index_y - 1].lemma_)
        words.append(phrase[index_y + 1].lemma_)
        final_index_list = index_y + 1

    elif "," in phrase.text and "y" in phrase.text:

        index_y = 0
        words = []
        for token in phrase:
            if token.text == "y":
                index_y = token.i
                final_index_list = token.i + 1
                break

        words.append(phrase[index_y + 1].lemma_)
        if phrase[index_y + 1].lemma_ not in attributes:
            attributes.append(Attribute(phrase[index_y + 1].lemma_))
        # index_y -= 1
        last = False
        while index_y > 0:
            if "," in phrase[(index_y - 4 if index_y - 4 > 0 else 0): index_y].text:
                if phrase[index_y - 2].text == ",":
                    words.append(phrase[index_y - 1].lemma_)
                    index_y -= 2
                    last = True
                    if phrase[index_y - 1].lemma_ not in attributes:
                        attributes.append(Attribute(phrase[index_y - 1].lemma_))
                else:
                    last = False
                    actual_part = phrase[(index_y - 4 if index_y - 4 > 0 else 0): index_y]
                    index_comma = 0 if actual_part.text[0] == "," else len(actual_part.text.split(",")[0].split(" "))
                    atributo_compuesto = ""
                    for i in range(index_comma + 1, 4):
                        if actual_part[i].text not in list(map(lambda x: x.text, list_of_prepositions)):
                            atributo_compuesto += actual_part[i].text + "_"
                            if actual_part[i].text in attributes:
                                to_deleted.append(actual_part[i].text)
                    atributo_compuesto = atributo_compuesto[:-1]
                    words.append(atributo_compuesto)
                    attributes.append(Attribute(atributo_compuesto))
                    index_y -= (4 - index_comma)
            else:
                if last:
                    words.append(phrase[index_y - 1].lemma_)
                else:
                    words.append(phrase[index_y - 1].lemma_)
                break

    if len(words) > 0:
        tam = len(list(set(words).intersection(set(attributes_list))))

        if len(list(set(words).intersection(set(attributes_list)))) > 0:
            for clase in classes:
                for word in words:
                    if clase.name in word or clase.name in to_deleted:
                        clase.update_percent(-150 * tam / len(words))
                if clase.percent > 0:
                    classes_return.append(clase)
            for attribute in attributes:
                if attribute.name in words and attribute.name not in to_deleted:
                    atributos_return.append(attribute)
        else:
            list_phrase = False
    else:
        list_phrase = False


    if len(classes_return) == 0:
        classes_return = classes
    return atributos_return, classes_return, attributes, final_index_list, list_phrase


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

        if clase_objetivo is not None:
            for attribute in attributes:
                if attribute.name in before.text and attribute.name not in list(map(lambda x: x.name, classes)) and attribute.name != '"' and attribute.name != "":
                    attribute_found = True
                    if attribute.name in attributes_list:
                        clase_objetivo.add_update_attribute(attribute, 50)
                    else:
                        clase_objetivo.add_update_attribute(attribute, 10)
        if clase_objetivo is not None and attribute_found:
            break
    return classes, attributes, attribute_found


def clases_atributos_preposiciones_list(phrase, preps, classes, attributes_list, list_index,
                                        attributes_return):
    for prep in preps:

        attribute_found = False
        if list_index < prep.i:

            attribute_found = True

            if prep.i + 5 > len(phrase):
                after = phrase[prep.i:len(phrase)]
            else:
                after = phrase[prep.i: prep.i + 5]

            clase_objetivo = None

            for clase in classes:
                if clase.name in after.text:
                    clase_objetivo = clase
                    clase_objetivo.update_percent(10)

            if clase_objetivo is not None:
                for attribute in attributes_return:
                    if attribute.name in attributes_list:
                        clase_objetivo.add_update_attribute(attribute, 50)
                    else:
                        clase_objetivo.add_update_attribute(attribute, 20)
            if clase_objetivo is not None and attribute_found:
                break
    return classes, attribute_found


def relations_detections(classes, doc,nlp):
    phrases = doc.text.split(".")
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

            # Regla 2 AND
            if second_class_id + 1 < len(phrase_nlp) and phrase_nlp[second_class_id + 1].text == "y":
                t = phrase_nlp[second_class_id + 2]

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

    return relations
