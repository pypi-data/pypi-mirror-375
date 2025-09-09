# dependencies

import random


def vocales():
  return "aeiou"

def consonantes():
  return "bcdfghjklmnpqrstvwxyz"

def aleatoreizarMayusculas(texto, probabilidad=0.5):
  nuevoTexto = ""
  listaTexto = texto.split()
  for palabra in listaTexto:
    nuevaPalabra = ""
    for caracter in palabra:
      if (random.random() < probabilidad):
        caracter = caracter.upper()
    nuevaPalabra = nuevaPalabra + caracter
    nuevoTexto = nuevoTexto + nuevaPalabra
  return nuevoTexto