from importlib.metadata import (
  Distribution,
  distribution,
  packages_distributions,
)
from types import ModuleType
from typing import Optional


_jakelut = packages_distributions()


def _jakelu(moduuli: ModuleType) -> Optional[Distribution]:
  '''
  Hae se asennettu paketti, johon annettu moduuli sisältyy.
  '''
  # Tutkitaan vain moduulipolun ensimmäistä osaa.
  juurimoduuli = moduuli.__name__.split('.')[0]

  # Haetaan välimuistista.
  try:
    return distribution(_jakelut[juurimoduuli][0])
  except (KeyError, IndexError):
    return None
  # def _jakelu
