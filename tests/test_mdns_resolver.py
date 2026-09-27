import hashlib
import json
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from controller import resolver
from controller.service import controller_url_from_host, pair_retropie


class MdnsResolverTests(unittest.TestCase):
    def test_local_name_uses_app_avahi_socket(self):
        class Connection:
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def settimeout(self, _timeout): pass
            def connect(self, endpoint): self.endpoint = endpoint
            def sendall(self, query): self.query = query
            def recv(self, _size): return b'+ 2 0 retropieconsole.local 10.0.2.57\n'
        with tempfile.TemporaryDirectory() as directory:
            endpoint = Path(directory) / 'resolver.sock'
            endpoint.touch()
            connection = Connection()
            resolver._cache.clear()
            with patch.object(resolver, 'APP_SOCKET', endpoint), patch.object(
                resolver.socket, 'socket', return_value=connection
            ), patch.object(resolver.socket, 'gethostbyname', side_effect=AssertionError('container DNS used')):
                self.assertEqual(resolver.resolve_ipv4('retropieconsole.local'), '10.0.2.57')
            self.assertEqual(connection.endpoint, str(endpoint))
            self.assertEqual(connection.query, b'RESOLVE-HOSTNAME-IPV4 retropieconsole.local\n')

    def test_app_lab_reports_missing_resolver_clearly(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(
            resolver, 'APP_SOCKET', Path(directory) / 'missing'
        ), patch.object(resolver, 'HOST_SOCKET', Path(directory) / 'missing-host'), patch.dict(
            'os.environ', {'APP_HOME': '/app'}
        ):
            with self.assertRaisesRegex(socket.gaierror, 'local-name resolver is unavailable'):
                resolver.resolve_ipv4('missing-console.local')

    def test_pairing_resolves_local_name_before_certificate_check(self):
        certificate = b'console certificate'
        fingerprint = hashlib.sha256(certificate).hexdigest()
        class Response:
            status = 200
            def read(self): return json.dumps({'paired': True, 'platform': 'retropie',
                                               'console_id': 'a' * 32}).encode()
        class Connection:
            sent = None
            def __init__(self, host, port, **_kwargs):
                self.host, self.port = host, port
            def connect(self): self.sock = self
            def getpeercert(self, **_kwargs): return certificate
            def request(self, _method, _path, body=None, **_kwargs):
                Connection.sent = json.loads(body)
            def getresponse(self): return Response()
            def close(self): pass
        with patch('controller.service.resolve_ipv4', return_value='10.0.2.57') as lookup, patch(
            'controller.service.http.client.HTTPSConnection', Connection
        ), patch('controller.service.socket.getaddrinfo', side_effect=AssertionError('container DNS used')):
            result = pair_retropie('retropieconsole.local', '123456', fingerprint,
                                   'secret-token-123456', 'a' * 32,
                                   controller_url=controller_url_from_host('virtualglove.local'))
        lookup.assert_called_once_with('retropieconsole.local')
        self.assertEqual(result['host'], 'retropieconsole.local')
        self.assertEqual(Connection.sent['controller_url'], 'http://virtualglove.local:8766')

    def test_pairing_uses_the_uno_q_address_from_setup(self):
        self.assertEqual(controller_url_from_host('virtualglove.local'),
                         'http://virtualglove.local:8766')
        self.assertEqual(controller_url_from_host('10.0.2.86'), 'http://10.0.2.86:8766')
        self.assertEqual(controller_url_from_host('virtualglove.local:8101'),
                         'http://virtualglove.local:8766')
        with self.assertRaises(ValueError):
            controller_url_from_host('127.0.0.1:8766')


if __name__ == '__main__':
    unittest.main()
