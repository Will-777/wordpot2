"""Smoke tests: the honeypot must boot and answer probes without a 500.

Deliberately loose on status codes — the point is not to freeze WordPress-mimicking
behaviour, it's to catch a broken template, a broken route or a dependency bump that
takes the whole honeypot down.
"""

import pytest

from wordpot import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


@pytest.mark.parametrize('path', [
    '/',                        # front page, themed
    '/index.php',
    '/wp-login.php',            # badlogin plugin
    '/readme.html',             # commonfiles plugin
    '/xmlrpc.php',              # commonfiles plugin
    '/?author=1',               # userenumeration plugin
    '/wp-admin',                # redirects to wp-login.php
    '/wp-content/plugins/akismet',
    '/wp-content/themes/twentytwentyfour',
])
def test_probe_does_not_error(client, path):
    resp = client.get(path)
    assert resp.status_code < 500, f'{path} returned {resp.status_code}'


def test_login_post_is_handled(client):
    """Bruteforce attempts must be absorbed, never crash the honeypot."""
    resp = client.post('/wp-login.php', data={'log': 'admin', 'pwd': 'admin'})
    assert resp.status_code < 500


def test_server_header_is_spoofed(client):
    """Fingerprinting relies on the fake Server header being present."""
    resp = client.get('/')
    assert resp.headers.get('Server') == app.config['SERVER']


def test_unknown_file_is_404(client):
    """A real WordPress 404s on junk — leaking 200s everywhere is a tell."""
    assert client.get('/definitely-not-a-wp-file.zzz').status_code == 404
