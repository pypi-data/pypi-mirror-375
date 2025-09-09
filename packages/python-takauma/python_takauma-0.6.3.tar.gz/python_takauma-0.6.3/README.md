python-takauma
==============

Python-moduulien tiedostoversiointi


Luokkakohtainen versionmuodostus:
--------------------------------

Oletetaan, että paketti `python-foobar` on asennettu, ja sen versionumero on 1.2.3.

Olkoon tiedosto `spam.py` seuraavansisältöinen:
```python
# python-foobar/foobar/spam.py
from takauma import Versio

class Spam:
  __versio__ = Versio()

print(Foo.__versio__)
```

Tällöin komento `python -m foobar.spam` tulostaa `Version('1.2.3')`.


Aiemmat luokkaversiot:
---------------------

Oletetaan paketin asennus samoin kuin edellä.

Olkoon tiedosto `eggs.py` seuraavansisältöinen:
```python
# python-foobar/foobar/eggs.py
# versiointi: *
from takauma import etsi_versiot

class Eggs:
  luku = 42

Eggs._aiemmat_versiot = etsi_versiot(Eggs)

for versio in '1.2.4', '1.2.3', '1.2.2', '1.2.1', '1':
  try: print(Eggs._aiemmat_versiot[versio].luku)
  except Exception as exc: print(exc)
```

Oletetaan lisäksi, että levyllä on jäljellä aiempi versio samasta tiedostosta:
```python
# python-foobar/foobar/eggs-1.2.1.py
class Eggs:
  luku = 24
```

Silloin komento `python -m foobar.eggs` tulostaa seuraavasti:
```
42
42
24
24
KeyError: '1'
```

Aiempien versioiden luonti:
--------------------------

Aiempi tiedostoversio tunnistetaan tiedostonimen mukaan silloin, kun se on muotoa `<moduuli>-<versio>.py`, missä `<moduuli>.py` on viimeisin, ajossa oleva tiedostoversio.

Git-versiointi (https://pypi.org/project/git-versiointi/) tallentaa aiemmat versiot automaattisesti git-muutostietojen mukaan erityisen versiointimerkinnän perusteella: ks. edellä `eggs.py`-tiedostossa rivi 2.

Versiointimääritys (`# versiointi: x`) aiheuttaa sen, että kopiot tiedostosta tallennetaan git-versiohistorian mukaisesti git-revisioon `x` asti (poissulkevasti), tai historian alkuun saakka (`*`).

Huomaa, että aiempien tiedostoversioiden muodostus versiomäärityksen perusteella tapahtuu pip-asennuksen `build_py`-vaiheessa, eikä niitä siis synny automaattisesti kehitystilassa olevalle paketin sisälle. Sen sijaan aiemman version testaus onnistuu vaikkapa seuraavantyyppisen komennon avulla:
```bash
git -C python-foobar show HEAD~2:foobar/eggs.py > python-foobar/foobar/eggs-1.2.1.py
```
