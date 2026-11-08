"""Tests for the fetcher's SSRF protection. Run: python -m unittest -v"""
import socket
import unittest
from unittest import mock

from fetcher import net_safety
from fetcher.net_safety import BlockedURLError, check_url, safe_get


def resolves_to(ip):
    """Fake DNS: every hostname resolves to `ip`."""
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    return mock.patch("socket.getaddrinfo",
                      return_value=[(family, socket.SOCK_STREAM, 6, "", (ip, 443))])


def fake_response(status=200, body=b"ok", location=None):
    r = mock.MagicMock()
    r.status_code = status
    r.is_redirect = status in (301, 302, 303, 307, 308)
    r.headers = {"Location": location} if location else {}
    r.encoding = "utf-8"
    r.iter_content.return_value = [body]
    r.raise_for_status.return_value = None
    return r


PUBLIC_IP = "93.184.216.34"


class AllowlistTests(unittest.TestCase):
    def test_configured_source_host_is_allowed(self):
        with resolves_to(PUBLIC_IP):
            check_url("https://krebsonsecurity.com/feed/")

    def test_subdomain_of_allowed_host_is_allowed(self):
        with resolves_to(PUBLIC_IP):
            check_url("https://www.microsoft.com/en-us/security/blog/feed/")

    def test_unknown_host_is_blocked(self):
        # The real domain tl;dr sec's page pointed us to on Nov 2.
        with resolves_to(PUBLIC_IP), self.assertRaises(BlockedURLError):
            check_url("https://rss.hiivinternal.com/feeds/xgTKUmMmUm.xml")

    def test_lookalike_domains_are_blocked(self):
        with resolves_to(PUBLIC_IP):
            for url in ("https://microsoft.com.evil.example/",
                        "https://evilmicrosoft.com/",
                        "https://krebsonsecurity.com.attacker.net/feed"):
                with self.subTest(url=url), self.assertRaises(BlockedURLError):
                    check_url(url)

    def test_plain_http_is_blocked(self):
        with resolves_to(PUBLIC_IP), self.assertRaises(BlockedURLError):
            check_url("http://krebsonsecurity.com/feed/")


class PrivateAddressTests(unittest.TestCase):
    def test_allowed_host_resolving_to_internal_ip_is_blocked(self):
        for ip in ("127.0.0.1", "10.0.0.5", "192.168.1.1",
                   "169.254.169.254",   # cloud metadata address
                   "::1", "fd00::1"):
            with self.subTest(ip=ip), resolves_to(ip), self.assertRaises(BlockedURLError):
                check_url("https://krebsonsecurity.com/feed/")


class RedirectAndSizeTests(unittest.TestCase):
    def test_redirect_to_unknown_host_is_blocked(self):
        hop = fake_response(302, location="https://attacker.example/steal")
        with resolves_to(PUBLIC_IP), mock.patch("requests.get", return_value=hop):
            with self.assertRaises(BlockedURLError):
                safe_get("https://krebsonsecurity.com/feed/")

    def test_redirect_within_allowlist_is_followed(self):
        hops = [fake_response(301, location="https://www.microsoft.com/feed/"),
                fake_response(200, body=b"<rss/>")]
        with resolves_to(PUBLIC_IP), mock.patch("requests.get", side_effect=hops):
            resp = safe_get("https://microsoft.com/feed/")
        self.assertEqual(resp.content, b"<rss/>")
        self.assertEqual(resp.url, "https://www.microsoft.com/feed/")

    def test_redirect_loop_is_stopped(self):
        loop = fake_response(302, location="https://krebsonsecurity.com/feed/")
        with resolves_to(PUBLIC_IP), mock.patch("requests.get", return_value=loop):
            with self.assertRaises(BlockedURLError):
                safe_get("https://krebsonsecurity.com/feed/")

    def test_oversized_response_is_rejected(self):
        big = fake_response(200)
        big.iter_content.return_value = [b"x" * 65536] * (net_safety.MAX_BYTES // 65536 + 2)
        with resolves_to(PUBLIC_IP), mock.patch("requests.get", return_value=big):
            with self.assertRaises(BlockedURLError):
                safe_get("https://krebsonsecurity.com/feed/")


class AutodiscoveryTests(unittest.TestCase):
    def test_feed_link_to_unknown_host_on_source_page_is_not_followed(self):
        from fetcher import rss_fetcher
        page = (b'<html><head><link rel="alternate" type="application/rss+xml" '
                b'href="https://rss.hiivinternal.com/feeds/x.xml"></head></html>')
        source = {"id": 9, "name": "tl;dr sec", "url": "https://tldrsec.com/",
                  "category": "Cyber", "frequency": "weekly"}
        calls = []

        def fake_get(url, **kwargs):
            calls.append(url)
            return fake_response(200, body=page)

        with resolves_to(PUBLIC_IP), mock.patch("requests.get", side_effect=fake_get):
            with self.assertRaises(ValueError):          # no entries -> source skipped
                rss_fetcher._fetch_feed(source, window_hours=168)
        self.assertEqual(calls, ["https://tldrsec.com/"])  # the unknown host was never contacted


if __name__ == "__main__":
    unittest.main()
