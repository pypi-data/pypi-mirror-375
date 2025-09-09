# -*- coding: utf-8 -*-

import functools
import sys


class Versio:
  '''
  Hae sen python-paketin versionumero, johon määrittelevä luokka
  sisältyy.

  Käytettävissä luokan määreenä seuraavasti:
  class Foo:
    __versio__ = Versio()
  '''
  def __get__(self, instance, cls=None):
    return getattr(
      sys.modules.get((cls or type(instance)).__module__),
      '__versio__',
      None
    )
    # def __get__

  # class Versio


class Versiot:
  '''
  Hae kaikki määrittelevää luokkaa vastaavat versiot vanhemmista,
  saatavilla olevista moduuliversioista.

  Käytettävissä luokan määreenä seuraavasti:
  class Foo:
    __versiot__ = Versiot()
  '''
  def __get__(self, instance, cls):
    cls = cls or type(instance)
    moduulin_versiot = getattr(
      sys.modules.get(cls.__module__),
      '__versiot__',
      None
    )
    if moduulin_versiot is None:
      return None
    def hae_kohde(moduuli):
      try:
        return functools.reduce(
          getattr, cls.__qualname__.split('.'), moduuli
        )
      except AttributeError:
        return None
    *muut, tama = moduulin_versiot.items()
    return type(moduulin_versiot)((*filter(lambda x: x[1] is not None, (
      (versio, hae_kohde(versioitu_moduuli))
      for versio, versioitu_moduuli in muut
    )), (tama[0], cls)))
    # def __get__

  # class Versiot
