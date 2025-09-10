# -*- coding: utf-8 -*-
'''
Moduulikohtainen, ajonaikaisesti laskettava määre.

Määreen nimi muodostetaan poistamalla argumenttina annetun
funktion nimen edestä mahdolliset alaviivat.

Huomaa, että määrettä ei voida teknisistä rajoitteista johtuen
asettaa samalla nimellä samaan moduuliin kuin toteuttava funktio.

Esim.

>>> import sys
>>> from mmaare import mmaare # tai: import mmaare
>>> import xyz
>>> ...
>>> # Asetetaan määre `f` käsillä olevaan moduuliin (__main__).
>>> @mmaare
>>> def __f(moduuli):
>>>  return ''.join(reversed(list(moduuli.__name__)))
>>>...
>>> # Asettaa määreen eri nimellä toiseen moduuliin.
>>> mmaare(__f.fget, nimi='__nimi_vaarinpain__', moduuli=xyz)
>>> ...
>>>  print(sys.modules['__main__'].f) # --> __niam__
>>>  print(xyz.__nimi_vaarinpain__) # --> zyx
'''

import functools
import sys
import warnings


class _Py36:
  '''Python 3.6 -toteutus.

  Periytetään moduulin luokka, lisätään datakuvaaja.
  '''
  # pylint: disable=no-member
  def __init__(self, *args, **kwargs):
    import types
    super().__init__(*args, **kwargs)
    if not isinstance(self.moduuli, types.ModuleType):
      # Asetetaan arvo sellaisenaan muille kuin `ModuleType`-olioille.
      # Tällaisten moduulien `__class__` ei salli asettamista.
      setattr(self.moduuli, self.nimi, self.__get__(self.moduuli))
      return
    self.moduuli.__class__ = functools.wraps(
      self.moduuli.__class__,
      updated=()
    )(type(
      '_Moduuli',
      (self.moduuli.__class__, ),
      {self.nimi: self}
    ))
    # def __init__

  def __get__(self, obj, cls=None):
    # Poimitaan mahdollinen olemassaoleva arvo.
    try: return obj.__dict__[self.nimi]
    except KeyError: pass
    # Haetaan ja asetetaan.
    arvo = super().__get__(obj, cls)
    self.__set__(obj, arvo)
    return arvo
    # def __get__

  # Ohitetaan poikkeukset `mappingproxy`-tyyppisen
  # kontekstisanakirjan muokkaamiseen liittyen.

  def __set__(self, obj, arvo):
    try: obj.__dict__[self.nimi] = arvo
    except TypeError: pass
    # def __set__

  def __delete__(self, obj):
    try: del obj.__dict__[self.nimi]
    except TypeError: pass
    # def __delete__

  # class _Py36


class _Py37:
  '''Python 3.7+ -toteutus.

  "Periytetään" `__getattr__`-funktio (ks. PEP 562).
  '''
  # pylint: disable=no-member

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    def __getattr__(avain):
      # pylint: disable=no-member, protected-access
      if avain == self.nimi:
        return self.__get__(self.moduuli)

      # Estetään rekursio samalla avaimella.
      # Muuten ne __getattr__-toteutukset
      # (esim. `celery.local.LazyModule`), jotka käyttävät
      # `ModuleType.__getattribute__`-metodia puuttuvien arvojen
      # hakemiseen, aiheuttavat päättymättömän rekursiosilmukan.
      if avain in __getattr__.__rekursio__:
        return self._ei_loydy(self.moduuli, avain)

      __getattr__.__rekursio__.add(avain)
      try:
        return __getattr__.__wrapped__(avain)
      finally:
        __getattr__.__rekursio__.discard(avain)
      # def __getattr__

    try:
      mod_getattr = self.moduuli.__getattr__
    except AttributeError:
      mod_getattr = functools.partial(
        self._ei_loydy,
        self.moduuli
      )
    try:
      self.moduuli.__getattr__ = functools.wraps(
        mod_getattr
      )(__getattr__)
    except AttributeError:
      # Mikäli moduuli ei salli `__getattr__`-
      # funktion asettamista, ohitetaan.
      warnings.warn(
        f'Funktion `{self.moduuli}.__getattr__`'
        f' asettaminen ei sallittu, ohitetaan.',
        stacklevel=3,
      )
    else:
      __getattr__.__rekursio__ = set()
    # def __init__

  @staticmethod
  def _ei_loydy(moduuli, avain):
    raise AttributeError(f'{moduuli.__name__}: {avain!r}')
    # def _ei_loydy

  # class _Py37


class mmaare(
  _Py36 if sys.version_info < (3, 7) else _Py37,
  property
):
  # pylint: disable=invalid-name

  def __new__(cls, *args, **kwargs):
    '''
    Sallitaan käyttö koristeena seuraavilla tavoilla:

    # Tuottaa moduulimääreen nimellä `f`.
    @mmaare
    def _f(m): ...

    # Tuottaa moduulimääreen nimellä `def`.
    @mmaare(nimi='def')
    def abc(m): ...

    # Tuottaa moduulimääreen nimellä `g`
    @mmaare # tai: @mmaare(nimi='g')
    @staticmethod
    def _g(): ...
    '''
    if args:
      return super().__new__(cls, *args, **kwargs)
    else:
      return functools.partial(cls, **kwargs)
    # def __new__

  def __init__(self, fget, nimi=None, moduuli=None):
    if isinstance(fget, staticmethod):
      # pylint: disable=function-redefined, unused-argument
      @functools.wraps(fget.__func__)
      def fget(m):
        return fget.__wrapped__()
    self.nimi = nimi or fget.__name__.lstrip('_')
    self.moduuli = moduuli or sys.modules[fget.__module__]
    if (self.moduuli.__name__, self.nimi) == (fget.__module__, fget.__name__):
      raise ValueError(f'Määrettä ei voida asettaa samalla nimellä: {fget}')
    super().__init__(fget)
    # def __init__

  # class mmaare


# Sallitaan tämän moduulin käyttö sellaisenaan koristeena.
sys.modules[__name__].__class__ = functools.wraps(
  sys.modules[__name__].__class__,
  updated=()
)(type('mmaare', (
  sys.modules[__name__].__class__,
), {'__call__': mmaare}))
