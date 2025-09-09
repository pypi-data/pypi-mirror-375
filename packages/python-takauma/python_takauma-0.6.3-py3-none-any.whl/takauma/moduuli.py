# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

import glob
import importlib
import os
import re
import sys

from packaging.version import parse

from .hakemisto import Versiohakemisto


def _versio(moduuli):
  jakelu = moduuli.__jakelu__
  return parse(jakelu.version) if jakelu is not None else None
  # def _versio


class Sisallonlataaja(importlib.machinery.SourceFileLoader):
  ''' Lataa moduuli muistissa olevasta tiedostosisällöstä. '''
  def __init__(self, fullname, path, sisalto):
    super().__init__(fullname, path)
    self.sisalto = sisalto
  def get_data(self, path):
    return self.sisalto
  # class Sisallonlataaja


def _kehitysversiot(moduuli):
  '''
  Etsi git-tietovarastosta kaikki versiointimäärityksen mukaiset
  aiemmat versiot moduulin määrittelevästä tiedostosta.

  Edellyttää `git-versiointi`-paketin (v1.4.9+) asennusta.
  '''
  # pylint: disable=import-error
  try:
    if parse(importlib.metadata.version('git-versiointi')) < parse('1.4.9'):
      return
  except importlib.metadata.PackageNotFoundError:
    return

  from versiointi.tiedostot import tiedostoversiot
  from versiointi import tarkista_git_versiointi

  jakelu = moduuli.__jakelu__

  # Alusta versiointimääritys.
  tarkista_git_versiointi(
    jakelu,
    'git_versiointi',
    str(jakelu.locate_file('setup.py')),
  )

  # Käy läpi annetun moduulin tallennetut versiot.
  for versio, tiedostosisalto in tiedostoversiot(
    jakelu.git_versiointi,
    os.path.relpath(
      os.path.realpath(moduuli.__file__),
      os.path.realpath(jakelu.locate_file('.')),
    )
  ):
    nimi = '-'.join((moduuli.__name__, str(versio)))
    spec = importlib.util.spec_from_loader(nimi, Sisallonlataaja(
      nimi,
      f'-{versio}'.join(os.path.splitext(
        moduuli.__file__
      )),
      tiedostosisalto
    ))
    versioitu_moduuli = importlib.util.module_from_spec(spec)
    versioitu_moduuli.__versio__ = parse(versio)
    yield versioitu_moduuli
    # for versio, tiedostosisalto in tiedostoversiot
  # def _kehitysversiot


def _asennetut_versiot(moduuli):
  '''
  Etsi levyltä kaikki versiot moduulin määrittelevästä tiedostosta.

  Python-tiedostoja etsitään nimellä <moduuli>-<versio>.py, missä
  moduuli vastaa `moduuli.__file__`-arvoa (ilman .py-päätettä).
  '''
  # Etsi vanhempia versioita moduulin nimen mukaan.
  try: tiedosto = moduuli.__file__
  except AttributeError: return

  alku, loppu = os.path.splitext(tiedosto)
  for versioitu_tiedosto in glob.glob('-*'.join((alku, loppu))):
    versio = parse(re.sub(
      rf'-(.*){loppu}', r'\1', versioitu_tiedosto.replace(alku, '')
    ))
    nimi = '-'.join((moduuli.__name__, str(versio)))

    # Lataa versioidun moduulitiedoston sisältö;
    # ks. https://docs.python.org/3.6/library/importlib.html, kpl 31.5.6.3.
    spec = importlib.util.spec_from_file_location(
      nimi, versioitu_tiedosto,
    )
    versioitu_moduuli = importlib.util.module_from_spec(spec)
    versioitu_moduuli.__versio__ = versio
    yield versioitu_moduuli
    # for versioitu_tiedosto
  # def _asennetut_versiot


def _versiot(moduuli):
  '''
  Etsi kaikki saatavilla olevat versiot moduulista ja palauta ne
  sanakirjana (Versiohakemistona).
  '''
  # Kootaan olemassaolevat versiot sanakirjaan.
  versiot = {}
  if moduuli.__jakelu__ is not None:
    def _versiot():
      yield from _asennetut_versiot(moduuli)
      try: yield from _kehitysversiot(moduuli)
      except: pass
    for versioitu_moduuli in _versiot():
      sys.modules[versioitu_moduuli.__name__] = versioitu_moduuli
      try:
        versioitu_moduuli.__loader__.exec_module(versioitu_moduuli)
      except: # pylint: disable=bare-except
        sys.modules.pop(versioitu_moduuli.__name__)
      else:
        versiot[versioitu_moduuli.__versio__] = versioitu_moduuli
      # for versioitu_moduuli
    # if moduuli.__jakelu__ is not None

  # Mikäli nykyistä versionumeroa ei löydy sanakirjasta,
  # lisätään se.
  nykyinen_versio = moduuli.__versio__ or parse('0')
  if nykyinen_versio not in versiot:
    versiot[nykyinen_versio] = moduuli

  # Järjestä aiemmat versionumerot.
  jarjestetyt_versionumerot = sorted(versiot)

  # Muodosta ja aseta versiohakemisto.
  return Versiohakemisto((*zip(
    jarjestetyt_versionumerot,
    map(versiot.get, jarjestetyt_versionumerot)
  ), (
    # Lisää nykyinen versio aina (myös) avaimella "__max__".
    '__max__', moduuli,
  )))
  # def _versiot
