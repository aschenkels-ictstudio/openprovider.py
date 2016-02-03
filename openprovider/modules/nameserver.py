# -*- coding: utf-8 -*-

from openprovider.modules import E, OE, common
from openprovider.models import Model, ZoneDetails


def _domain(domain):
    sld, tld = domain.split('.', 1)
    print E.domain(
            E.name(sld),
            E.extension(tld),
    )
    return E.domain(
        E.name(sld),
        E.extension(tld),
    )


def _records(records):
    items = []
    for rec in records:
        if rec.get('prio') and rec.get('ttl'):
            item = E.item(E.type(rec.get('type')), E.name(rec.get('name')), E.value(rec.get('value')), E.prio(rec.get('prio')), E.ttl(rec.get('ttl')))
        elif not rec.get('prio') and rec.get('ttl'):
            item = E.item(E.type(rec.get('type')), E.name(rec.get('name')), E.value(rec.get('value')), E.ttl(rec.get('ttl')))
        elif not rec.get('prio') and not rec.get('ttl'):
            item = E.item(E.type(rec.get('type')), E.name(rec.get('name')), E.value(rec.get('value')))
        items.append(item)
    return E.records(E.array(*items))

class NameserverModule(common.Module):
    """Bindings to API methods in the nameserver module."""

    def search_zone_dns_request(self, limit=None, offset=None, extension=None,
                              name_pattern=None, type=None,
                              with_records=None, with_history=None):

        request = E.searchZoneDnsRequest(
            OE('limit', limit),
            OE('offset', offset),
            OE('namePattern', name_pattern),
            OE('type', type),
            OE('withRecords', with_records),
            OE('withHistory', with_history),
        )
        response = self.request(request)
        return response.as_models(ZoneDetails)

    def retrieve_zone_dns_request(self, name, with_records=True, with_history=False):

        request = E.retrieveZoneDnsRequest(
            OE('name', name),
            OE('withRecords', with_records),
            OE('withHistory', with_history),
        )
        response = self.request(request)
        return response.as_model(ZoneDetails)

    def modify_master_zone_dns_request(self, domain, records=None):
        """Modify DNS Records"""

        self.request(
            E.modifyZoneDnsRequest(
                _domain(domain),
                E.type('master'),
                _records(records),
            ),
        )

        return True
