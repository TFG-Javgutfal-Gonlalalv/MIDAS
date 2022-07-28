from main.utils import get_key_words
from main.clases import Class, Attribute, Relation
from main.models import Technicality, FrequentAttributes
import spacy


def lista_locs(doc):
    lista = []
    for ent in doc.ents:
        if ent.label_ is not None:
            if ent.label_ == "LOC" or ent.label_ == "ORG":
                lista.append(ent.text)
    return lista


def class_detection_rules(doc):

    lista_preposiciones = ["a", "ante","bajo", "con","contra", "de", "desde", "en", "entre", "hacia", "hasta", "para", "por","según", "sin", "so","sobre", "tras"]

    nouns = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.pos_ == "NOUN"]


    words = nouns.copy()
    words_final = nouns.copy()
    technicalities = list(Technicality.objects.values_list("name", flat=True))
    attributes_list = list(FrequentAttributes.objects.values_list("name", flat=True))
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

    for phrase in phrases:
        if "Como" in phrase and ("quiero" in phrase or "deseo" in phrase):
            final = "quiero"
            if "deseo" in phrase:
                final = "deseo"

            for clase in classes:
                if clase.name in phrase[0:phrase.index(final)]:
                    clase.update_percent(20)
    #detector atributos y clase tras ":"

    for phrase in phrases:
        clase_objetivo = None
        if ":" in phrase:
            for clase in classes:
                if clase.name in phrase[0:phrase.index(":")]:
                    clase.update_percent(20)
                    clase_objetivo = clase

                    if clase_objetivo is not None:
                        for attribute in attributes:
                            if attribute.name in phrase[phrase.index(":"):len(phrase)]:
                                clase_objetivo.add_update_attribute(attribute,20)
                                list_classes = [x for x in classes if x.name == attribute.name]
                                if len(list_classes) > 0:
                                    el = list_classes[0]
                                    el.update_percent(-50)
    #detector preposiciones
    for phrase in phrases:

        for token in phrase:
            if token.text.lower() in lista_preposiciones:
                if lista_preposiciones in phrase:
                    before = phrase[0:phrase.index(token.text)]
                    after = phrase[phrase.index(token.text):len(phrase)]
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
                            cantidad = phrase.count(clase.name)
                            if  cantidad == 1:
                                if abs(phrase.index(clase.name) - pos_atributo) < min_pos:
                                    min_pos = abs(phrase.index(clase.name) - pos_atributo)
                                    clase_objetivo = clase
                            else:
                                indice = phrase.index(clase.name)
                                for i in range(1,cantidad):
                                    if abs(indice - pos_atributo) < min_pos:
                                        min_pos = abs(indice - pos_atributo)
                                        clase_objetivo = clase
                                    indice = phrase.index(clase.name, indice +1)

                    if clase_objetivo is not None:
                        clase_objetivo.add_update_attribute(attribute,20)

    classes_final = []
    for clase in classes:

        if clase.percent >= 0:
            classes_final.append(clase)
    relations_final = relations_detections(classes_final,doc)
    return classes_final, relations_final

def relations_detections (classes, doc):

    phrases = doc.text.split(".")
    nlp = spacy.load("es_core_news_lg")
    relations = []

    for phrase in phrases:
        first_class = None
        verb = None
        second_class =None

        for token in nlp(phrase):
            #print(token.pos_, token.dep_, token.lemma_)
            if (token.pos_ == "NOUN" and token.dep_ == "nsubj" and first_class == None and token.lemma_ in classes):
                first_class = classes[classes.index(token.lemma_)]
            if (token.pos_ == "VERB" and (token.dep_ == "ROOT" or token.dep_ == "acl")) and token.lemma_ != "querer" and token.lemma_ != "desear":
                verb = token.lemma_
            if (token.pos_ == "NOUN" and (token.dep_ == "obj" or token.dep_ == "nsubj") and token.lemma_ in classes and second_class == None):
                if first_class != None and first_class.name != token.lemma_:
                    second_class = classes[classes.index(token.lemma_)]

        if (first_class != None and verb != None and second_class != None):
            relations.append(Relation(first_class,second_class, verb, phrase))

    #print(relations)
    return relations