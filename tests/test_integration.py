# coding=utf-8

"""
The test_integration module provides integration (black-box) tests for the
entire library.
"""

from betamax import Betamax

from openprovider.data.sslcerts import CertTypes
from openprovider.exceptions import BadRequest, ValidationError
from openprovider.models import Reseller, Address

from tests.factories.domainname import domainname
from tests.factories.nameserver import nameservers

import tests
import textwrap
import uuid


class TestDomains(tests.ApiTestCase):
    """Smoke tests for the domain module."""

    @tests.betamaxed
    def test_domain_check_active(self):
        """Obviously taken domains should return 'active'."""
        self.assertEqual(self.api.domains.check("example.com"), "active")

    @tests.betamaxed
    def test_domain_check_free(self):
        """Obviously free domain should return 'free'."""
        self.assertEqual(self.api.domains.check("oy6uT6caew3deej.com"), "free")

    @tests.betamaxed
    def test_domain_check_invalid_tld(self):
        """Domains with an invalid TLD should raise a BadRequest."""
        self.assertRaises(BadRequest, self.api.domains.check, "a.invalid")

    @tests.betamaxed
    def test_domain_check_invalid_sld(self):
        """Domains with an invalid SLD should raise a BadRequest."""
        self.assertRaises(BadRequest, self.api.domains.check, "a.com")

    @tests.betamaxed
    def test_domain_check_many(self):
        """Test for checking multiple domains."""
        result = self.api.domains.check_many(["example.com", "example.net"])
        self.assertEqual(result,
                         {"example.com": "active", "example.net": "active"})

    @tests.betamaxed
    def test_domain_search_empty(self):
        """Searching for example.com should return nothing."""
        result = self.api.domains.search_domain_request(domain_name_pattern="example.com")
        self.assertEqual(result, [])

    def test_domain_order(self):
        """Test that creates a domain name, then deletes it."""
        dname = domainname()
        name_servers = nameservers()
        cust = "YN000088-NL"

        with Betamax(self.api.session).use_cassette('test_domain_order_create'):
            self.api.domains.create_domain_request(
                    domain=dname,
                    period=1,
                    owner_handle=cust,
                    admin_handle=cust,
                    tech_handle=cust,
                    name_servers=name_servers,
            )

        with Betamax(self.api.session).use_cassette('test_domain_order_modify'):
            self.api.domains.modify_domain_request(dname, comments="Test")

        with Betamax(self.api.session).use_cassette('test_domain_order_retrieve'):
            result = self.api.domains.retrieve_domain_request(dname)
            self.assertEqual(result.comments, "Test")
            self.assertEqual(result.owner_handle, cust)
            self.assertEqual(result.admin_handle, cust)
            self.assertEqual(result.tech_handle, cust)

        with Betamax(self.api.session).use_cassette('test_domain_order_delete'):
            self.api.domains.delete_domain_request(dname)

        with Betamax(self.api.session).use_cassette('test_domain_order_post'):
            result = self.api.domains.search_domain_request(domain_name_pattern=dname)
            self.assertEqual(result, [])


class TestExtensions(tests.ApiTestCase):
    """Smoke tests for the extensions module."""

    @tests.betamaxed
    def test_search_extension(self):
        """Search should return something sensible."""
        r = self.api.extensions.search_extension(with_usage_count=True)
        self.assertTrue(r[0].usage_count is not None)

    @tests.betamaxed
    def test_retrieve_extension(self):
        """Retrieve should return a proper Extension."""
        r = self.api.extensions.retrieve_extension("nl", with_description=True)
        self.assertTrue(r.description is not None)


class TestSSL(tests.ApiTestCase):
    """Smoke tests for the SSL module."""

    @tests.betamaxed
    def test_ssl_search_product(self):
        """Test for the SSL product search method."""
        result = self.api.ssl.search_product()
        self.assertTrue(result[0].id)

    @tests.betamaxed
    def test_ssl_retrieve_product(self):
        """Test for retrieving details on a single product."""
        res = self.api.ssl.retrieve_product(CertTypes.COMODO_EV_SSL.product_id)
        self.assertEqual(res.id, CertTypes.COMODO_EV_SSL.product_id)

    def test_ssl_order(self):
        """Test that orders a SSL certificate, then cancels it."""

        csr = textwrap.dedent("""
        -----BEGIN CERTIFICATE REQUEST-----
        MIICzjCCAbYCAQAwgYgxCzAJBgNVBAYTAk5MMRMwEQYDVQQIDApPdmVyaWpzc2Vs
        MREwDwYDVQQHDAhFbnNjaGVkZTEYMBYGA1UECgwPQW50YWdvbmlzdCBCLlYuMSEw
        HwYDVQQLDBhPUEVOUFJPVklERVIgUFkgVEVTVCBDU1IxFDASBgNVBAMMC2V4YW1w
        bGUuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7WvbK/VDTxc/
        9DFkYreQNZo6j+0TrFFX1kqopS/COkkTaNY4xl7B/bq/CBS34nfjRT8x05RhyP2F
        mrNf6fZzl+8boQwJ4eVIDMjTNNecAsKrDTlZqwtvauPPEZ0pV7v6fxO+QOMn1uJq
        ZV7F+vdZ0IUihFUNwQoh9RaIoGtkaAiv1fgH/nrUuci/A9PqH2IBPRf9cCiIt1eK
        WCMXvWFzxkTATPVO35GByjN1GyMgRwTVrP53MKGAUOvbI4awS5x/ByKgigFhfLwr
        M86SSz1ZejlwZ7WqXFgPardMXOYt63ybKASanUTEUAgaEeK/9eL/sKQvEB0tBHbK
        e4uEksNsxwIDAQABoAAwDQYJKoZIhvcNAQELBQADggEBANlOjT4ddIgf9Zg1kR6p
        zbSfwuKLjS/w5RrnT5HliSTRUT/N8tNd2hRiukPqayJGhxtUIvyPdJTYUumIOnhu
        9ZZJcQJQDr5mvhP9hWn4/4yxOuZRd9q7DeoPSDRTkz7MuygoXQGt0ehOMcZBsfUC
        Uqx6ReCDz9PqgCa75XPL041SVot0RVswiiV54JRN0/cKzaItvtvinf0bPpPA1IWX
        qYm2QyYYJ8ayAsIw64YukRSOXp+escQ4rLfR1Un+QvgJM05x47jX8JivO3utexca
        cDJkVtg8DtoP1O1iF+xhNcHeWXUNO+PWHS9jIjL2Ofb78LjMpBjnB7C1L8rYxxg8
        cXU=
        -----END CERTIFICATE REQUEST-----
        """).strip()

        cert = CertTypes.COMODO_ESSENTIALSSL.product_id
        cust = "YN000088-NL"

        cname = "example.com"
        mail1 = "admin@example.com"
        mail2 = "administrator@example.com"

        with Betamax(self.api.session).use_cassette('test_ssl_order_decode_csr'):
            decoded_csr = self.api.ssl.decode_csr(csr)
            self.assertEqual(cname, decoded_csr.subject.commonName)

        with Betamax(self.api.session).use_cassette('test_ssl_order_create'):
            oid = self.api.ssl.create(cert, 1, csr, "linux", cust, mail1)

        with Betamax(self.api.session).use_cassette('test_ssl_order_retrieve'):
            self.assertEqual(cust, self.api.ssl.retrieve_order(oid).organizationHandle)

        with Betamax(self.api.session).use_cassette('test_ssl_order_change_approver'):
            self.assertEqual(oid, self.api.ssl.change_approver_email_address(oid, mail2))

        with Betamax(self.api.session).use_cassette('test_ssl_order_change_resend'):
            self.assertEqual(oid, self.api.ssl.resend_approver_email(oid))

        with Betamax(self.api.session).use_cassette('test_ssl_order_change_cancel'):
            self.assertEqual(oid, self.api.ssl.cancel(oid))

    @tests.betamaxed
    def test_ssl_approver_email(self):
        """Test for retrieving a list of allowed approver email addresses."""
        cert = CertTypes.COMODO_ESSENTIALSSL.product_id
        emails = self.api.ssl.retrieve_approver_email_list("example.com", cert)
        self.assertTrue("admin@example.com" in emails)


class TestReseller(tests.ApiTestCase):
    """Smoke tests for the reseller module."""

    @tests.betamaxed
    def test_reseller_retrieve(self):
        r = self.api.reseller.retrieve()
        self.assertTrue(isinstance(r, Reseller))
        self.assertTrue(isinstance(r.address, Address))


class TestCustomer(tests.ApiTestCase):
    """Smoke tests for the customer module."""

    @tests.betamaxed
    def test_customer_search(self):
        r = self.api.customers.search_customer()
        self.assertTrue(len(r) >= 1)

    @tests.betamaxed
    def test_customer_search_non_existing(self):
        r = self.api.customers.search_customer(email_pattern="doesntexist.com")
        self.assertTrue(len(r) == 0)


class TestEmail(tests.ApiTestCase):
    """Smoke tests for the email module."""

    # These tests are a bit flawed in that we expect some things to exist or not exist, but since
    # it's betamaxed we can probably get away with it for a long time

    @tests.betamaxed
    def test_seach_non_existing(self):
        email = 'nonexisting@example.org'
        results = self.api.email.search_customer_email_verification_request(email)
        self.assertEqual(results, [])

    @tests.betamaxed
    def test_seach_existing(self):
        email = 'test@example.org'
        results = self.api.email.search_customer_email_verification_request(email)
        self.assertEqual(len(results), 1)

        result = results[0]
        self.assertEqual(result.name, email)
        self.assertTrue(hasattr(result, 'id'))
        self.assertTrue(hasattr(result, 'status'))

    @tests.betamaxed
    def test_start_verification(self):
        email = '%s@example.org' % uuid.uuid4()
        results = self.api.email.start_customer_email_verification_request(email)
        self.assertIsNotNone(results)

    @tests.betamaxed
    def test_restart_non_existing_verification(self):
        email = '%s@example.org' % uuid.uuid4()
        with self.assertRaises(ValidationError) as cm:
            self.api.email.restart_customer_email_verification_request(email)
        self.assertEqual(cm.exception.code, 1203)

    @tests.betamaxed
    def test_restart_existing_verification(self):
        email = 'demo@example.org'
        result = self.api.email.restart_customer_email_verification_request(email)
        self.assertIsNotNone(result)
