#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlencode
import requests
from cleep.core import CleepRenderer
from cleep.exception import CommandError
from cleep.profiles.alertprofile import AlertProfile

__all__ = ["Freemobilesms"]


class Freemobilesms(CleepRenderer):
    """
    FreemobileSms application.
    this application is able to render core.alert.send events
    """

    MODULE_AUTHOR = "Cleep"
    MODULE_VERSION = "1.1.0"
    MODULE_PRICE = 0.0
    MODULE_CATEGORY = "SERVICE"
    MODULE_DEPS = []
    MODULE_DESCRIPTION = "Sends you SMS alerts using french Freemobile provider."
    MODULE_LONGDESCRIPTION = (
        "French Freemobile telecom provider gives a way to send to you (and only you) "
        "freely SMS using your account. Configure this application and your device will "
        "be able to send you some message directly on your mobile."
    )
    MODULE_TAGS = ["sms", "alert", "freemobile"]
    MODULE_COUNTRY = "fr"
    MODULE_URLSITE = "https://github.com/CleepDevice/cleepapp-freemobilesms"
    MODULE_URLHELP = None
    MODULE_URLBUGS = "https://github.com/CleepDevice/cleepapp-freemobilesms/issues"
    MODULE_URLINFO = "https://mobile.free.fr/"

    MODULE_CONFIG_FILE = "freemobilesms.conf"
    DEFAULT_CONFIG = {"userid": None, "apikey": None}

    RENDERER_PROFILES = [AlertProfile]

    FREEMOBILESMS_API_URL = "https://smsapi.free-mobile.fr/sendmsg"
    FREEMOBILESMS_RESPONSE = {
        200: "Message sent",
        400: "Missing parameter",
        402: "SMS limit reached",
        403: "Service not enabled",
        500: "Server error",
    }

    def __init__(self, bootstrap, debug_enabled):
        """
        Constructor

        Params:
            bootstrap (dict): bootstrap objects
            debug_enabled: debug status
        """
        CleepRenderer.__init__(self, bootstrap, debug_enabled)

    def set_credentials(self, userid, apikey):
        """
        Set FreemobileSms credentials

        Params:
            userid (str): userid
            apikey (str): apikey

        Returns:
            bool: True if credentials saved successfully
        """
        self._check_parameters(
            [
                {
                    "name": "userid",
                    "value": userid,
                    "type": str,
                    "none": False,
                    "empty": False,
                    "validator": lambda val: len(val) == 8,
                    "message": "Userid must be 8 characters long",
                },
                {
                    "name": "apikey",
                    "value": apikey,
                    "type": str,
                    "none": False,
                    "empty": False,
                },
            ]
        )

        return self._update_config({"userid": userid, "apikey": apikey})

    def send_sms(self, message):
        """
        Send sms message

        Args:
            message (str): message to send
        """
        user_id, api_key = self.__get_credentials()
        params = urlencode({"user": user_id, "pass": api_key, "msg": message})
        self.logger.debug("Request params: %s", params)

        try:
            status = self.__send_request(params)
        except Exception as error:
            self.logger.exception("Error sending sms during test:")
            raise CommandError("Internal error (see logs)") from error

        if status != 200:
            message = self.FREEMOBILESMS_RESPONSE.get(
                status, f"Unknown error [{status}]"
            )
            self.logger.error(
                "Error sending test SMS: %s [%s]",
                message,
                status,
            )
            raise CommandError(message)

        return True

    def test(self):
        """
        Send test sms

        Returns:
            bool: True if test succeed

        Raises:
            CommandError: failed to send SMS
        """
        return self.send_sms("Hello this is Cleep")

    def on_render(self, profile_name, profile_values):
        """
        On render profile

        Args:
            profile_name (str): profile name
            profile_values (dict): profile values to render

        Returns:
            bool: True if render succeed, False otherwise
        """
        try:
            user_id, api_key = self.__get_credentials()
        except Exception:
            self.logger.warning(
                "Unable to send SMS because credentials are not configured"
            )
            return False

        try:
            params = urlencode(
                {
                    "user": user_id,
                    "pass": api_key,
                    "msg": profile_values.get("message", "No message"),
                }
            )

            status = self.__send_request(params)

            if status != 200:
                self.logger.error(
                    "Unable to send SMS: %s [%s]",
                    self.FREEMOBILESMS_RESPONSE.get(
                        status, f"Unknown error [{status}]"
                    ),
                    status,
                )
                return False

            self.logger.info("SMS sent successfully")
            return True

        except Exception:
            self.logger.exception("Unable to send sms:")
            return False

    def __get_credentials(self):
        """
        Get credentials from command parameters or config

        Returns:
            tuple: credentials

                (
                    user id (str): user identifier
                    api key (str): api key
                )

        Raises:
            CommandError: command error exception

        """
        config = self._get_config()
        if (
            config["userid"] is None
            or len(config["userid"]) == 0
            or config["apikey"] is None
            or len(config["apikey"]) == 0
        ):
            raise CommandError("Please fill credentials first")

        return config["userid"], config["apikey"]

    def __send_request(self, params):
        """
        Send request to freemobile sms api

        Args:
            params (dict): dict of request parameters

        Returns:
            int: response status code

        """
        url = f"{self.FREEMOBILESMS_API_URL}?{params}"
        self.logger.debug("Request url: %s", url)
        response = requests.get(url, timeout=2.0)
        status = response.status_code
        self.logger.debug("Request response status: %s", status)

        return status
