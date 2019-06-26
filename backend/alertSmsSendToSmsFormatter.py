#!/usr/bin/env python
# -*- coding: utf-8 -*-

from raspiot.events.formatter import Formatter
from raspiot.events.alertSmsProfile import AlertSmsProfile

class AlertSmsSendToSmsFormatter(Formatter):
    """
    Sms data to SmsProfile
    """
    def __init__(self, events_broker):
        """
        Constuctor

        Args:
            events_broker (EventsBroker): events broker instance
        """
        Formatter.__init__(self, events_broker, u'alert.sms.send', AlertSmsProfile())

    def _fill_profile(self, event_values, profile):
        """
        Fill profile with event data
        """
        profile.message = event_values[u'message']

        return profile

