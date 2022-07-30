from main.models import Class, Attribute, Relation

class ClassFKs:
    def __init__(self, clase):
        self.clase = clase
        self.fks = set()
        self.attributes = []

    def add_fk(self, fk):
        self.fks.add(fk)

    def add_attributes(self, attributes):
        self.attributes = attributes

    def __str__(self):
        return self.clase

    def __eq__(self, clase):
        return self.clase == clase

    def __hash__(self):
        return hash(self.clase)

def convertir_run_codigo_sql(run):

    classes = Class.objects.filter(run_fk=run)
    order_classes = []
    classes_fk = []

    #1. Creación de las clases auxiliares ClassFK
    for clase in classes:
        class_fk = ClassFKs(clase)
        relations_class = Relation.objects.filter(class_fk_1=clase)
        attributes_class = Attribute.objects.filter(class_fk=clase)
        class_fk.add_attributes(attributes_class)

        for r in relations_class:
            if r.multiplicity_1 == "*":
                class_fk.add_fk(r.class_fk_2)

        relations_class = Relation.objects.filter(class_fk_2=clase)

        for r in relations_class:
            if r.multiplicity_2 == "*":
                class_fk.add_fk(r.class_fk_1)

        classes_fk.append(class_fk)

    #2. Reordenación de las clases según los fks
    while len(order_classes) < len(classes_fk):
        for c in classes_fk:
            if c.fks.issubset(order_classes) and c not in order_classes:
                order_classes.append(c)

    #3. Creación del script sql
    script = ""
    for c in order_classes:
        script += "CREATE TABLE "+ c.clase.name + " (\n"
        script += c.clase.name + "Id int NOT NULL,\n"
        for a in c.attributes:
            script += a.name + " " + a.type + ",\n"
        for fk in c.fks:
            script += fk.name + "Id int,\n"
        script += "PRIMARY KEY ("+c.clase.name + "Id)"
        if (len(c.fks) == 0):
            script += "\n);"
        else:
            for fk in c.fks:
                script += ",\n" + "FOREIGN KEY ("+ fk.name+"Id) REFERENCES "+fk.name+"("+ fk.name+"Id)\n"
            script +=");"
        script += "\n\n"

    print(script)