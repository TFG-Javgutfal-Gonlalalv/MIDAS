from utils import get_key_words
from clases import Class, Attribute

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
    technicalities = get_key_words("key_words/tecnicismos.txt")
    attributes_list = get_key_words("key_words/atributos.txt")
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
