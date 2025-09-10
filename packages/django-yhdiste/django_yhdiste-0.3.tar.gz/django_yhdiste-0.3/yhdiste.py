# -*- coding: utf-8 -*-

import functools
import inspect

from django.http import (
  HttpResponseBadRequest,
  HttpResponseForbidden,
  HttpResponseNotAllowed,
)


class luokkavalimuisti:
  # pylint: disable=invalid-name
  name = None

  def __init__(self, method=None):
    self.fget = method

  def __set_name__(self, owner, name):
    self.name = name

  def __get__(self, instance, cls=None):
    tulos = self.fget(cls)
    if self.name is not None:
      setattr(cls, self.name, tulos)
    return tulos

  # class luokkavalimuisti


class Yhdiste:
  '''
  Yhdistenäkymä, joka valitsee ja suorittaa erikseen
  määritellyn toimintometodin HTTP-metodin (GET, POST, jne.) ja
  HTTP-pyynnöllä annettujen GET-parametrien (`?...`) perusteella.
  '''

  @classmethod
  def oikeus_vaaditaan(cls, oikeus):
    '''
    Vaadi annettu Django-oikeustaso toiminnon käyttöön; esim.

    @Yhdiste.toiminto
    @Yhdiste.oikeus_vaaditaan('auth.view_user')
    def toiminto(self, request, **kwargs):
      ...
    '''
    def _oikeus_vaaditaan(metodi):
      @functools.wraps(metodi)
      def _metodi(self, request, *args, **kwargs):
        if not request.user.has_perm(oikeus):
          return HttpResponseForbidden()
        return _metodi.__wrapped__(self, request, *args, **kwargs)
      return _metodi
    return _oikeus_vaaditaan
    # def oikeus_vaaditaan

  @classmethod
  def kohdekohtainen(cls, parametri='pk', hae_kohde='hae_kohde'):
    '''
    Hae ja aseta `self.object` ennen metodin suoritusta; esim.

    def hae_kohde(self, *, pk):
      return self.malli.objects.filter(...).get(pk=pk)
    ...
    @Yhdiste.toiminto
    @Yhdiste.kohdekohtainen
    def toiminto(self, request, *, pk, **kwargs):
      print(self.object)
      ...
    '''
    def _kohdekohtainen(metodi):
      @functools.wraps(metodi)
      def _metodi(self, request, *args, **kwargs):
        pk = kwargs.get(parametri)
        if not pk:
          return HttpResponseBadRequest()
        self.object = getattr(self, hae_kohde)(**{parametri: pk})
        return _metodi.__wrapped__(self, request, *args, **kwargs)
      return _metodi
    return _kohdekohtainen
    # def kohdekohtainen

  @classmethod
  def toiminto(
    cls,
    *args,
    tyyppi='GET',
    allekirjoitus=None,
    parametrit=None,
  ):
    '''
    Merkitse annettu metodi HTTP-toiminnoksi.

    Aseta annetulle metodille tarvittaessa uusi määre `toiminnot` ja
    lisää tähän (lista-) määreeseen uusi merkintä: tuple(
      tyypit,
      funktioallekirjoitus (inspect.Signature)
    ).

    Args:
      *args: funktio, joka merkitään toiminnoksi
      tyyppi (str / tuple): käsiteltävä HTTP-pyynnön tyyppi/tyypit,
        oletus ('GET', )
      allekirjoitus (inspect.Signature): käsittelevän metodin
        allekirjoitus, oletuksena haetaan automaattisesti
      parametrit (tuple / list / set): pyynnöltä vaadittavien
        GET-parametrien nimet, oletus automaattinen haku

    Returns:
      koristeltu, alkuperäinen funktio

    Mikäli `args` on tyhjä, palautetaan python-koriste, jota kutsutaan
    funktioargumentilla ja joka tekee toiminnoksi merkitsemisen.
    '''
    # pylint: disable=no-else-raise

    # Käsitellään yksittäinen tyyppi yksikkönä.
    if isinstance(tyyppi, str):
      tyyppi = (tyyppi, )

    def koriste(metodi):
      if allekirjoitus is not None:
        # Käytä annettua allekirjoitusta.
        _allekirjoitus = allekirjoitus
      elif parametrit is not None:
        # Määritä allekirjoitus annetuin parametrein.
        _allekirjoitus = inspect.Signature([
          inspect.Parameter(
            name=p, kind=inspect.Parameter.POSITIONAL_OR_KEYWORD
          )
          for p in ('self', 'request')
        ] + [
          inspect.Parameter(name=p, kind=inspect.Parameter.KEYWORD_ONLY)
          for p in parametrit
        ])
      else:
        # Poimi allekirjoitus oletuksena metodin tiedoista.
        _allekirjoitus = inspect.signature(metodi)

      metodi.__dict__.setdefault(
        'toiminnot', []
      ).append(
        (tyyppi, _allekirjoitus)
      )
      return metodi
      # def koriste

    if args:
      return koriste(*args)
    else:
      return koriste
    # def toiminto

  @luokkavalimuisti
  def _toiminnot(cls):
    # pylint: disable=no-self-argument, no-member
    def __toiminnot():
      for luokka in cls.__mro__:
        # Käydään periytyshierarkia läpi ja tutkitaan kunkin luokan metodit.
        for nimi in dir(luokka):
          try:
            metodi = luokka.__dict__[nimi]
          except KeyError:
            continue
          for tyypit, allekirjoitus in getattr(metodi, 'toiminnot', []):
            for tyyppi in tyypit:
              yield nimi, tyyppi.upper(), allekirjoitus
    return list(__toiminnot())
    # def _toiminnot

  def _allowed_methods(self):
    ''' Vrt. `django.views.generic.View._allowed_methods. '''
    # pylint: disable=not-an-iterable
    return [tyyppi for nimi, tyyppi, allekirjoitus in self._toiminnot]

  def dispatch(self, request, *args, **kwargs):
    '''
    Tutkitaan, vastaako HTTP-pyyntöä jokin näkymäluokassa määritetty
    toiminto. Silloin palautetaan (määrittelyjärjestyksessä) ensimmäisen
    täsmäävän toiminnon tuottama paluusanoma.

    Mikäli GET-parametreja vastaavaa toimintoa ei löydy, ojennetaan pyyntö
    super-toteutukselle – ks. esim. `django.views.generic.View.dispatch`.

    Ellei super-toteutusta ole, palautetaan 405 Method Not Allowed.
    '''
    # pylint: disable=unused-argument, not-an-iterable
    parametrit = dict(request.GET.items())
    for nimi, tyyppi, allekirjoitus in self._toiminnot:
      if request.method.upper() == tyyppi:
        try:
          allekirjoitus.bind(self=self, request=request, **parametrit)
        except TypeError:
          continue
        vastaus = getattr(self, nimi)(request, *args, **parametrit)
        if not isinstance(vastaus, HttpResponseNotAllowed):
          return vastaus
        # if request.method.upper == tyyppi
      # for nimi, tyyppi, allekirjoitus in self._toiminnot

    # Muut pyynnöt ojennetaan mahdolliselle super-toteutukselle.
    # Huomaa, että `django.views.generic.View.dispatch` tuottaa silloin
    # `HttpResponseNotAllowed` (405) -sanoman, ellei periytetty näkymä
    # määrittele esim. `get`-metodia (ks. vaikkapa `TemplateView`).
    # Ellei näkymä periydy `View`-luokasta, palautetaan 405.
    try:
      super_dispatch = super().dispatch
    except AttributeError:
      return HttpResponseNotAllowed(self._allowed_methods())
    else:
      return super_dispatch(request, *args, **kwargs)
    # def dispatch

  # class Yhdiste
