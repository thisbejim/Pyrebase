"""
Functions for generating and verifying JSON Web Tokens.
"""

import threading
from datetime import datetime, timedelta
from calendar import timegm
from base64 import urlsafe_b64encode
from os import urandom
import jws

jws.utils.to_bytes_2and3 = lambda s: \
    s if isinstance(s, jws.utils.binary_type) else s.encode('utf-8')

#pylint: disable=protected-access
jws._signing_input = lambda head, payload, is_json=False: \
    '.'.join([b.decode('utf-8') for b in
              map(jws.utils.to_base64 if is_json else jws.utils.encode,
                  [head, payload])])

_tls = threading.local()

class _VerifyNotImplemented(jws.header.VerifyNotImplemented):
    def verify(self):
        if getattr(_tls, 'ignore_not_implemented', False):
            return self.value
        return super(_VerifyNotImplemented, self).verify()

for _header in jws.header.KNOWN_HEADERS:
    cls = jws.header.KNOWN_HEADERS[_header]
    if cls == jws.header.VerifyNotImplemented:
        jws.header.KNOWN_HEADERS[_header] = _VerifyNotImplemented

class _JWTError(Exception):
    """ Exception raised if claim doesn't pass. Private to this module because
        jws throws many exceptions too. """
    pass

def generate_jwt(claims, priv_key=None,
                 algorithm='PS512', lifetime=None, expires=None,
                 not_before=None,
                 jti_size=16):
    """
    Generate a JSON Web Token.

    :param claims: The claims you want included in the signature.
    :type claims: dict

    :param priv_key: The private key to be used to sign the token. Note: if you pass ``None`` then the token will be returned with an empty cryptographic signature and :obj:`algorithm` will be forced to the value ``none``.
    :type priv_key: `_RSAobj <https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA._RSAobj-class.html>`_ (for ``RSA*`` or ``PS*``), `SigningKey <https://github.com/warner/python-ecdsa>`_ (for ``ES*``) or str (for ``HS*``)

    :param algorithm: The algorithm to use for generating the signature. ``RS256``, ``RS384``, ``RS512``, ``PS256``, ``PS384``, ``PS512``, ``ES256``, ``ES384``, ``ES512``, ``HS256``, ``HS384``, ``HS512`` and ``none`` are supported.
    :type algorithm: str

    :param lifetime: How long the token is valid for.
    :type lifetime: datetime.timedelta

    :param expires: When the token expires (if :obj:`lifetime` isn't specified)
    :type expires: datetime.datetime

    :param not_before: When the token is valid from. Defaults to current time (if ``None`` is passed).
    :type not_before: datetime.datetime

    :param jti_size: Size in bytes of the unique token ID to put into the token (can be used to detect replay attacks). Defaults to 16 (128 bits). Specify 0 or ``None`` to omit the JTI from the token.
    :type jti_size: int

    :rtype: unicode
    :returns: The JSON Web Token. Note this includes a header, the claims and a cryptographic signature. The following extra claims are added, per the `JWT spec <http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html>`_:

    - **exp** (*IntDate*) -- The UTC expiry date and time of the token, in number of seconds from 1970-01-01T0:0:0Z UTC.
    - **iat** (*IntDate*) -- The UTC date and time at which the token was generated.
    - **nbf** (*IntDate*) -- The UTC valid-from date and time of the token.
    - **jti** (*str*) -- A unique identifier for the token.
    """
    header = {
        'typ': 'JWT',
        'alg': algorithm if priv_key else 'none'
    }

    claims = dict(claims)

    now = datetime.utcnow()

    if jti_size:
        claims['jti'] = urlsafe_b64encode(urandom(jti_size)).decode('utf-8')

    claims['nbf'] = timegm((not_before or now).utctimetuple())
    claims['iat'] = timegm(now.utctimetuple())

    if lifetime:
        claims['exp'] = timegm((now + lifetime).utctimetuple())
    elif expires:
        claims['exp'] = timegm(expires.utctimetuple())

    return u'%s.%s.%s' % (
        jws.utils.encode(header).decode('utf-8'),
        jws.utils.encode(claims).decode('utf-8'),
        '' if header['alg'] == 'none' else jws.sign(header, claims, priv_key).decode('utf-8')
    )

#pylint: disable=R0912,too-many-locals

def verify_jwt(jwt,
               pub_key=None,
               allowed_algs=None,
               iat_skew=timedelta(),
               checks_optional=False,
               ignore_not_implemented=False):
    """
    Verify a JSON Web Token.

    :param jwt: The JSON Web Token to verify.
    :type jwt: str or unicode

    :param pub_key: The public key to be used to verify the token. Note: if you pass ``None`` and **allowed_algs** contains ``none`` then the token's signature will not be verified.
    :type pub_key: `_RSAobj <https://www.dlitz.net/software/pycrypto/api/current/Crypto.PublicKey.RSA._RSAobj-class.html>`_, `VerifyingKey <https://github.com/warner/python-ecdsa>`_, str or NoneType

    :param allowed_algs: Algorithms expected to be used to sign the token. The ``in`` operator is used to test membership.
    :type allowed_algs: list, dict or NoneType

    :param iat_skew: The amount of leeway to allow between the issuer's clock and the verifier's clock when verifiying that the token was generated in the past. Defaults to no leeway.
    :type iat_skew: datetime.timedelta

    :param checks_optional: If ``False``, then the token must contain the **typ** header property and the **iat**, **nbf** and **exp** claim properties.
    :type checks_optional: bool

    :param ignore_not_implemented: If ``False``, then the token must *not* contain the **jku**, **kid**, **x5u** or **x5t** header properties.
    :type ignore_not_implemented: bool

    :rtype: tuple
    :returns: ``(header, claims)`` if the token was verified successfully. The token must pass the following tests:

    - Its header must contain a property **alg** with a value in **allowed_algs**.
    - Its signature must verify using **pub_key** (unless its algorithm is ``none`` and ``none`` is in **allowed_algs**).
    - If the corresponding property is present or **checks_optional** is ``False``:

      - Its header must contain a property **typ** with the value ``JWT``.
      - Its claims must contain a property **iat** which represents a date in the past (taking into account :obj:`iat_skew`).
      - Its claims must contain a property **nbf** which represents a date in the past.
      - Its claims must contain a property **exp** which represents a date in the future.

    :raises: If the token failed to verify.
    """
    header, claims, sig = jwt.split('.')

    header = jws.utils.from_base64(header).decode('utf-8')
    parsed_header = jws.utils.from_json(header)

    if allowed_algs is None:
        allowed_algs = []

    alg = parsed_header.get('alg')
    if alg is None:
        raise _JWTError('alg not present')
    if alg not in allowed_algs:
        raise _JWTError('algorithm not allowed: ' + alg)

    claims = jws.utils.from_base64(claims).decode('utf-8')

    if pub_key:
        _tls.ignore_not_implemented = ignore_not_implemented
        try:
            jws.verify(header, claims, sig, pub_key, True)
        finally:
            _tls.ignore_not_implemented = False
    elif 'none' not in allowed_algs:
        raise _JWTError('no key but none alg not allowed')

    parsed_claims = jws.utils.from_json(claims)

    utcnow = datetime.utcnow()
    now = timegm(utcnow.utctimetuple())

    typ = parsed_header.get('typ')
    if typ is None:
        if not checks_optional:
            raise _JWTError('type not present')
    elif typ != 'JWT':
        raise _JWTError('type is not JWT')

    iat = parsed_claims.get('iat')
    if iat is None:
        if not checks_optional:
            raise _JWTError('iat claim not present')
    elif iat > timegm((utcnow + iat_skew).utctimetuple()):
        raise _JWTError('issued in the future')

    nbf = parsed_claims.get('nbf')
    if nbf is None:
        if not checks_optional:
            raise _JWTError('nbf claim not present')
    elif nbf > now:
        raise _JWTError('not yet valid')

    exp = parsed_claims.get('exp')
    if exp is None:
        if not checks_optional:
            raise _JWTError('exp claim not present')
    elif exp <= now:
        raise _JWTError('expired')

    return parsed_header, parsed_claims

#pylint: enable=R0912

def process_jwt(jwt):
    """
    Process a JSON Web Token without verifying it.

    Call this before :func:`verify_jwt` if you need access to the header or claims in the token before verifying it. For example, the claims might identify the issuer such that you can retrieve the appropriate public key.

    :param jwt: The JSON Web Token to verify.
    :type jwt: str or unicode

    :rtype: tuple
    :returns: ``(header, claims)``
    """
    header, claims, _ = jwt.split('.')
    header = jws.utils.from_json(jws.utils.from_base64(header).decode('utf-8'))
    claims = jws.utils.from_json(jws.utils.from_base64(claims).decode('utf-8'))
    return header, claims
