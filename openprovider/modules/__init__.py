# coding=utf-8

import lxml

E = lxml.objectify.ElementMaker(annotate=False)

from openprovider.modules import customer
from openprovider.modules import domain
from openprovider.modules import extension
from openprovider.modules import financial
from openprovider.modules import nameserver
from openprovider.modules import nsgroup
from openprovider.modules import reseller
from openprovider.modules import ssl
