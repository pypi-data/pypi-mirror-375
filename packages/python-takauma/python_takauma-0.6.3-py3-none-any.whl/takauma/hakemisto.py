# -*- coding: utf-8 -*-

import collections

from packaging.version import parse, Version


class Versiohakemisto(collections.OrderedDict):
  '''
  Sanakirjaluokka, joka palauttaa pyydettyä avainta lähinnä
  vastaavan, saman tai aiemman version.

  Sanakirjaan kuuluminen määräytyy sen mukaan, sisältääkö
  se vähintään yhden kysyttyä avainta vastaavan tai sitä vanhemman
  version.

  Avaimet "__min__" ja "__max__" noutavat vanhimman / uusimman
  saatavilla olevan version.

  Sisältää myös määreet `__min__` ja `__max__`, jotka viittaavat
  vanhimpaan ja uusimpaan saatavilla olevaan versionumeroon.
  '''

  @property
  def __min__(self):
    return next(iter(self.keys()), None)

  @property
  def __max__(self):
    return next(reversed(self.keys()), None)

  def __contains__(self, versio):
    if versio in ('__min__', '__max__'):
      return bool(self)
    if isinstance(versio, str):
      versio = parse(versio)
    if not isinstance(versio, Version):
      return False
    return next(iter(self)) <= versio
    # def __contains__

  def __getitem__(self, versio):
    if versio in ('__min__', '__max__'):
      try: return next((
        iter if versio == '__min__' else reversed
      )(self.values()))
      except StopIteration: pass
    elif isinstance(versio, str):
      versio = parse(versio)
    if not isinstance(versio, Version):
      raise KeyError(repr(versio))
    for avain, arvo in reversed(self.items()):
      if avain == '__max__':
        continue
      if avain <= versio:
        return arvo
    raise KeyError(repr(versio))
    # def __getitem__

  # class Versiohakemisto
