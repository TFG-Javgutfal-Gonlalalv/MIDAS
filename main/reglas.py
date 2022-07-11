from main.utils import get_key_words
from main.models import Class, Attribute, Run

def lista_locs(doc):
    lista = []
    for ent in doc.ents:
        if ent.label_ is not None:
            if ent.label_ == "LOC" or ent.label_ == "ORG":
                lista.append(ent.text)
    return lista


def class_detection_rules(doc,run):
    nouns = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and token.pos_ == "NOUN" ]

    words = nouns.copy()
    words_final = nouns.copy()
    technicalities = get_key_words("key_words/tecnicismos.txt")
    attributes_list = get_key_words("key_words/atributos.txt")
    classes = []
    attributes = []
    for word in words:
        value = nouns.count(word)

        if not Class.objects.filter(name=word).exists():
            clase = Class(name=word,score=0,run_fk=run)


            # Rule 1: Infrequent words
            if value == 1 and float(value / len(words)) < 0.02:
                clase.score(clase.score()-10)
            else:
                clase.score(clase.score()+10)

            # Rule 2: Technicalities
            if word.lower() in technicalities:
                clase.score(clase.score()-100)
            else:
                clase.score(clase.score()+10)

            # Rule 3: Attributes

            if word.lower() in attributes_list:
                clase.score(clase.score()-100)
            else:
                clase.score(clase.score()+10)

            # Rule 4: Si la palabra es una localización u organización ignorarla
            if word in lista_locs(doc):
                clase.score(clase.score()-100)
            else:
                clase.score(clase.score()+10)

            if clase.score >= 0:
                classes.append(clase)

        if not Attribute.objects.filter(name=word).exists():
            attribute = Attribute(name=word, score=0)
            attributes.append(attribute)

    phrases = doc.text.split(".")

    #detector atributos y clase tras ":"

    for phrase in phrases:
        clase_objetivo = None
        if ":" in phrase:
            for clase in classes:
                if clase.name in phrase[0:phrase.index(":")]:
                    clase.score(clase.score()+20)
                    clase_objetivo = clase

            for attribute in attributes:
                if attribute.name in phrase[phrase.index(":"):len(phrase)]:
                    attribute.score(attribute.score+20)
                    attribute.class_fk = clase_objetivo
                    list_classes = [x for x in classes if x.name == attribute.name]
                    if len(list_classes) > 0:
                        el = list_classes[0]
                        el.score(el.score-50)

    classes_final = []
    for clase in classes:

        if clase.score >= 0:
            classes_final.append(clase)

    for phrase in phrases:
        if "de cada" in phrase:
            before = phrase[0:phrase.index("de cada")]
            after = phrase[phrase.index("de cada"):len(phrase)]
            clase_objetivo = None

            for clase in classes:
                if clase.name in after:
                    clase_objetivo = clase
                    clase_objetivo.score(clase_objetivo.score+10)
            for attribute in attributes:

                if attribute.name in before:
                    attribute.class_fk = clase_objetivo
                    if attribute.name in attributes_list:
                        attribute.score(attribute.score+50)
                    else:
                        attribute.score(attribute.score+20)

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
