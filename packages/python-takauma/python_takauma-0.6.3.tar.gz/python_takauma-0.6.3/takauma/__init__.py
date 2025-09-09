# -*- coding: utf-8 -*-
# pylint: disable=invalid-name, unused-import

import importlib
import sys
import threading
import warnings

import mmaare

# pylint: disable=import-error
from .hakemisto import Versiohakemisto
from .jakelu import _jakelu
from .luokka import Versio, Versiot
from .moduuli import _versio, _versiot
# pylint: enable=import-error


_lukko = threading.RLock()
def tuotu(moduuli):
  '''
  Aseta moduulin tietoihin määreet __jakelu__, __versio__ ja __versiot__.
  '''
  with _lukko:
    mmaare(_jakelu, nimi='__jakelu__', moduuli=moduuli)
    mmaare(_versio, nimi='__versio__', moduuli=moduuli)
    mmaare(_versiot, nimi='__versiot__', moduuli=moduuli)
  # def tuotu


class Lataaja:

  def __init__(self, lataaja):
    self.lataaja = lataaja

  def create_module(self, spec):
    return self.lataaja.create_module(spec)

  def exec_module(self, module):
    with warnings.catch_warnings(record=True) as warning_list:
      self.lataaja.exec_module(module)
      tuotu(module)
    for warning in warning_list:
      warnings.warn(warning.message, warning.category, stacklevel=3)
    # def exec_module

  def __getattribute__(self, avain):
    if avain in ('__init__', 'lataaja', 'create_module', 'exec_module'):
      return super().__getattribute__(avain)
    return self.lataaja.__getattribute__(avain)
    # def __getattribute__

  # class Lataaja


class Etsija(importlib.abc.MetaPathFinder):
  def __init__(self):
    self.kaynnissa = set()

  def find_spec(
    self, fullname, path, target=None
  ) -> importlib._bootstrap.ModuleSpec:
    with _lukko:
      if fullname in self.kaynnissa:
        return None
      self.kaynnissa.add(fullname)
      try:
        spec = importlib.util.find_spec(fullname)
        if spec and spec.loader:
          spec.loader = Lataaja(spec.loader)
        return spec
      finally:
        self.kaynnissa.remove(fullname)
      # with _lukko
    # def find_spec

  # class Etsija


# Lisää edellä kuvatut määreet automaattisesti
# tämän jälkeen tuotuihin moduuleihin.
sys.meta_path.insert(0, Etsija())


# Lisää määreet heti aiemmin tuotuihin moduuleihin.
# Ohitetaan mahdolliset varoitukset __getattr__-
# funktion ylikuormittamisen yhteydessä.
# Huomaa, että kaikki Python-moduulit eivät salli
# tämän funktion ylikuormittamista.
with warnings.catch_warnings():
  warnings.simplefilter('ignore')
  for aiemmin_tuotu_moduuli in sys.modules.values():
    tuotu(aiemmin_tuotu_moduuli)
