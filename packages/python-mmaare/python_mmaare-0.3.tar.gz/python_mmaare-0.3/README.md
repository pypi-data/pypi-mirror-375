python-mmaare
==============

Python-moduulimääretoteutus

Yhteensopivuus: Python 3.6+

Käyttö:
------

```python
# moduuli.py
import mmaare

@mmaare
def nimi(moduuli):
  return moduuli.__name__.split('.')[-1]
```
