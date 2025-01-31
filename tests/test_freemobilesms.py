#!/usr/bin/env python
# -*- coding: utf-8 -*-
from cleep.libs.tests import session
import unittest
import logging
import sys

sys.path.append("../")
from backend.freemobilesms import Freemobilesms
from cleep.exception import InvalidParameter, MissingParameter, CommandError
from unittest.mock import patch, MagicMock, Mock, ANY
from cleep.libs.tests.common import get_log_level
import responses

LOG_LEVEL = get_log_level()


class TestsFreemobilesms(unittest.TestCase):

    def setUp(self):
        self.session = session.TestSession(self)
        logging.basicConfig(
            level=LOG_LEVEL,
            format="%(asctime)s %(name)s:%(lineno)d %(levelname)s : %(message)s",
        )

    def tearDown(self):
        self.session.clean()

    def init_context(self):
        self.app = self.session.setup(
            Freemobilesms, mock_on_start=False, mock_on_stop=False
        )
        self.session.start_module(self.app)

    def test_set_credentials(self):
        self.init_context()
        self.app._update_config = Mock()

        self.app.set_credentials("useriddd", "apikey")

        self.app._update_config.assert_called_with(
            {"userid": "useriddd", "apikey": "apikey"}
        )

    def test_set_crendetials_invalid_parameters(self):
        self.init_context()
        self.app_update_config = Mock()

        with self.assertRaises(InvalidParameter) as cm:
            self.app.set_credentials("userid", "apikey")
        self.assertEqual(str(cm.exception), "Userid must be 8 characters long")
        with self.assertRaises(MissingParameter) as cm:
            self.app.set_credentials(None, "apikey")
        self.assertEqual(str(cm.exception), 'Parameter "userid" is missing')
        with self.assertRaises(InvalidParameter) as cm:
            self.app.set_credentials("", "apikey")
        self.assertEqual(
            str(cm.exception), 'Parameter "userid" is invalid (specified="")'
        )

        with self.assertRaises(MissingParameter) as cm:
            self.app.set_credentials("useriddd", None)
        self.assertEqual(str(cm.exception), 'Parameter "apikey" is missing')
        with self.assertRaises(InvalidParameter) as cm:
            self.app.set_credentials("useriddd", "")
        self.assertEqual(
            str(cm.exception), 'Parameter "apikey" is invalid (specified="")'
        )

    @responses.activate
    def test_test(self):
        self.init_context()
        responses.add(
            responses.GET,
            "https://smsapi.free-mobile.fr/sendmsg?user=useriddd&pass=apikey&msg=Hello+this+is+Cleep",
            status=200,
        )
        self.app._get_config = Mock(
            return_value={"userid": "useriddd", "apikey": "apikey"}
        )

        result = self.app.test()

        self.assertTrue(result)

    def test_test_invalid_response(self):
        self.init_context()
        self.app._get_config = Mock(return_value={"userid": None, "apikey": None})

        with self.assertRaises(CommandError) as cm:
            self.app.test()
        self.assertEqual(str(cm.exception), "Please fill credentials first")

    @responses.activate
    def test_test_invalid_response(self):
        self.init_context()
        responses.add(
            responses.GET,
            "https://smsapi.free-mobile.fr/sendmsg?user=useriddd&pass=apikey&msg=Hello+this+is+Cleep",
            status=402,
        )
        self.app._get_config = Mock(
            return_value={"userid": "useriddd", "apikey": "apikey"}
        )

        with self.assertRaises(CommandError) as cm:
            self.app.test()
        self.assertEqual(str(cm.exception), "SMS limit reached")

    @responses.activate
    def test_test_exception(self):
        self.init_context()
        responses.add(
            responses.GET,
            "https://smsapi.free-mobile.fr/sendmsg?user=useriddd&pass=apikey&msg=Hello+this+is+Cleep",
            body=Exception("Test error"),
            status=404,
        )
        self.app._get_config = Mock(
            return_value={"userid": "useriddd", "apikey": "apikey"}
        )

        with self.assertRaises(CommandError) as cm:
            self.app.test()
        self.assertEqual(str(cm.exception), "Internal error (see logs)")

    @responses.activate
    def test_on_render(self):
        self.init_context()
        responses.add(
            responses.GET,
            "https://smsapi.free-mobile.fr/sendmsg?user=useriddd&pass=apikey&msg=Intruder+detected",
            status=200,
        )
        self.app._get_config = Mock(
            return_value={"userid": "useriddd", "apikey": "apikey"}
        )

        result = self.app.on_render("AlertProfile", {"message": "Intruder detected"})

        self.assertTrue(result)

    def test_on_render_no_credentials(self):
        self.init_context()
        self.app._get_config = Mock(return_value={"userid": None, "apikey": None})
        self.app.logger.warning = Mock()

        result = self.app.on_render("AlertProfile", {"message": "Intruder detected"})

        self.assertFalse(result)
        self.app.logger.warning.assert_called_with(
            "Unable to send SMS because credentials are not configured"
        )

    @responses.activate
    def test_on_render_invalid_response(self):
        self.init_context()
        responses.add(
            responses.GET,
            "https://smsapi.free-mobile.fr/sendmsg?user=useriddd&pass=apikey&msg=Intruder+detected",
            status=404,
        )
        self.app._get_config = Mock(
            return_value={"userid": "useriddd", "apikey": "apikey"}
        )

        result = self.app.on_render("AlertProfile", {"message": "Intruder detected"})

        self.assertFalse(result)

    @responses.activate
    def test_on_render_exception(self):
        self.init_context()
        responses.add(
            responses.GET,
            "https://smsapi.free-mobile.fr/sendmsg?user=useriddd&pass=apikey&msg=Intruder+detected",
            body=Exception("Test error"),
            status=404,
        )
        self.app._get_config = Mock(
            return_value={"userid": "useriddd", "apikey": "apikey"}
        )

        result = self.app.on_render("AlertProfile", {"message": "Intruder detected"})

        self.assertFalse(result)


if __name__ == "__main__":
    # coverage run --include="**/backend/**/*.py" --concurrency=thread test_freemobilesms.py; coverage report -m -i
    unittest.main()
