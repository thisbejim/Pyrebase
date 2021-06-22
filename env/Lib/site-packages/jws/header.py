from __future__ import absolute_import

import jws.algos as algos

from .exceptions import AlgorithmNotImplemented, ParameterNotImplemented, ParameterNotUnderstood, RouteMissingError

class HeaderBase(object):
    def __init__(self, name, value, data):
        self.name = name
        self.value = self.clean(value)
        self.data = data
    def sign(self): return self.value
    def verify(self): return self.value
    def clean(self, value): return value

class GenericString(HeaderBase):
    def clean(self, value):
        return str(value)

class SignNotImplemented(HeaderBase):
    def sign(self):
        raise ParameterNotImplemented("Header Parameter %s not implemented in the context of signing" % self.name)

class VerifyNotImplemented(HeaderBase):
    def verify(self):
        raise ParameterNotImplemented("Header Parameter %s not implemented in the context of verifying" % self.name)

class NotImplemented(HeaderBase):
    def clean(self, *a):
        raise ParameterNotUnderstood("Could not find an action for Header Parameter '%s'" % self.name)

class Algorithm(HeaderBase):
    def clean(self, value):
        try:
            self.methods = algos.route(value)
        except RouteMissingError as e:
            raise AlgorithmNotImplemented('"%s" not implemented.' % value)

    def sign(self):
        self.data['signer'] = self.methods['sign']
    def verify(self):
        self.data['verifier'] = self.methods['verify']

KNOWN_HEADERS = {
    # REQUIRED, signing algo, see signing_methods
    'alg': Algorithm,
    # OPTIONAL, type of signed content
    'typ': GenericString,
    # OPTIONAL, JSON Key URL. See http://self-issued.info/docs/draft-jones-json-web-key.html
    'jku': VerifyNotImplemented,
     # OPTIONAL, key id, hint for which key to use.
    'kid': VerifyNotImplemented,
    # OPTIONAL, x.509 URL pointing to certificate or certificate chain
    'x5u': VerifyNotImplemented,
    # OPTIONAL, x.509 certificate thumbprint
    'x5t': VerifyNotImplemented,
}

# data is by reference
def process(data, step):
    for param in data['header']:
        # The JWS Header Input MUST be validated to only include parameters
        # and values whose syntax and semantics are both understood and
        # supported. --- this is why it defaults to NotImplemented, which
        # raises an exception
        cls = KNOWN_HEADERS.get(param, NotImplemented)
        instance = cls(param, data['header'][param], data)
        procedure = getattr(instance, step)
        procedure()
    return data
