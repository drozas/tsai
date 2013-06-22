#!/usr/bin/python

a = 3
nombre = "drozas"
asignaturas = ["TSAI", "ISII", "HUM", "AW", "IA", "DE", "IR", 123]
amigos = {"dani": "666784532", "isma": "635155325", "jeanette" : "00474568087"}

print a
print nombre
print asignaturas
print amigos

print asignaturas[-2]
print amigos["dani"]
try:
    print amigos["no_existe"]
except KeyError: 
    print "esa clave no existe!"
    