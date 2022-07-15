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

class Relation:
    def __init__(self, class1,class2,verb, phrase):
        self.class1 = class1
        self.class2 = class2
        self.verb = verb
        self.phrase = phrase

    def __str__(self):
        return "" + self.class1.name + " - " + self.verb + " - " + self.class2.name

    def __eq__(self, class1):
        return self.class1 == class1

    def __hash__(self):
        return hash(self.class1)


