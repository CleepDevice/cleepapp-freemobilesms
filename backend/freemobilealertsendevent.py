#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cleep.libs.internals.event import Event

class CoreAlertSendEvent(Event):
    """
    Core.alert.send event
    """

    EVENT_NAME = 'core.alert.send'
    EVENT_PROPAGATE = True
    EVENT_PARAMS = ['subject', 'message', 'attachment', 'timestamp']

    def __init__(self, params):
        """
        Constructor

        Args:
            params (dict): event parameters
        """
        Event.__init__(self, params)

