#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raspiot.events.formatter import Formatter
from raspiot.events.alertSmsProfile import AlertSmsProfile

class AlertSmsSendToSmsFormatter(Formatter):
    """
    Sms data to SmsProfile
    """
    def __init__(self, events_factory):
        """
        Constuctor

        Args:
            events_factory (EventsFactory): events factory instance
        """
        Formatter.__init__(self, events_factory, u'alert.sms.send', AlertSmsProfile())

    def _fill_profile(self, event_values, profile):
        """
        Fill profile with event data
        """
        profile.message = event_values[u'message']

        return profile

