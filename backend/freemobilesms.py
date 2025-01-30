#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlencode
import requests
from cleep.core import CleepRenderer
from cleep.exception import CommandError, MissingParameter
from cleep.profiles.alertprofile import AlertProfile

__all__ = ["Freemobilesms"]


class Freemobilesms(CleepRenderer):
    """
    FreemobileSms application.
    this application is able to render core.alert.send events
    """

    MODULE_AUTHOR = "Cleep"
    MODULE_VERSION = "1.1.0"
    MODULE_PRICE = 0
    MODULE_CATEGORY = "SERVICE"
    MODULE_DEPS = []
    MODULE_DESCRIPTION = "Sends you SMS alerts using french Freemobile provider."
    MODULE_LONGDESCRIPTION = (
        "French Freemobile telecom provider gives a way to send to you (and only you) ",
        "freely SMS using your account. Configure this application and your device will ",
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
        402: "Limit reached",
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
            userid: userid (string)
            apikey: apikey (string)

        Returns:
            bool: True if credentials saved successfully
        """
        if userid is None or len(userid) == 0:
            raise MissingParameter("Userid parameter is missing")
        if apikey is None or len(apikey) == 0:
            raise MissingParameter("Apikey parameter is missing")

        # save config
        return self._update_config({"userid": userid, "apikey": apikey})

    def test(self):
        """
        Send test sms

        Returns:
            bool: True if test succeed

        Raises:
            CommandError: failed to send SMS
        """
        user_id, api_key = self.__get_credentials(userid, apikey)
        params = urlencode(
            {"user": user_id, "pass": api_key, "msg": "Hello this is Cleep"}
        )
        self.logger.debug("Request params: %s", params)

        try:
            status = self.__send_request(params)

            if status != 200:
                self.logger.error(
                    "Unable to test: %s [%s]",
                    self.FREEMOBILESMS_RESPONSE[status],
                    status,
                )
                error = self.FREEMOBILESMS_RESPONSE[status]

        except Exception:
            self.logger.exception("Error sending sms during test:")
            raise CommandError("Internal error (see logs)")

        return True

    def on_render(self, profile_name, profile_values):
        """
        On render profile

        Args:
            profile_name (str): profile name
            profile_values (dict): profile values to render

        Returns:
            bool: True if render succeed, False otherwise
        """
        error = False
        try:
            user_id, api_key = self.__get_credentials(None, None)
            params = urlencode(
                {
                    "user": user_id,
                    "pass": api_key,
                    "msg": profile_values["message"],
                }
            )

            status = self.__send_request(params)

            if status == 200:
                self.logger.info("SMS sent successfully")
            else:
                self.logger.error(
                    "Unable to send sms: %s [%s]",
                    self.FREEMOBILESMS_RESPONSE[status],
                    status,
                )
                error = True

        except Exception:
            self.logger.exception("Unable to send sms:")
            error = True

        return error

    def __get_credentials(self, user_id, api_key):
        """
        Get credentials from command parameters or config

        Args:
            user_id (str): user identifier
            api_key (str): api key

        Returns:
            tuple: credentials

                (
                    user id (str): user identifier
                    api key (str): api key
                )

        Raises:
            CommandError: command error exception

        """
        if user_id is None or api_key is None:
            config = self._get_config()
            if (
                config["userid"] is None
                or len(config["userid"]) == 0
                or config["apikey"] is None
                or len(config["apikey"]) == 0
            ):
                raise CommandError("Please fill credentials first")

            user_id = config["userid"]
            api_key = config["apikey"]

        return user_id, api_key

    def __send_request(self, params):
        """
        Send request to freemobile sms api

        Args:
            params (dict): dict of request parameters

        Returns:
            int: response status code

        """
        error = False
        try:
            url = f"{self.FREEMOBILESMS_API_URL}?{params}"
            self.logger.debug('Request url: %s', url)
            response = requests.get(url, timeout=2.0)
            status = response.status_code
            self.logger.debug("Request response status: %s", status)

            return status

        except Exception:
            self.logger.exception("Unable to send sms:")
            return None
