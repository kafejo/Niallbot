# -*- coding: utf-8 -*-
"""
Slack chat-bot Lambda handler.
"""

from niallbot import *
from slacker import *
from google_play_reporter import GooglePlayReporter
from config import *

import logging


def lambda_handler(event, context):

    # Disable googleapiclient warnings
    logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

    # Grab the Slack response url
    slack_response_url = event['response_url']
    is_debug = event['is_debug']

    if is_debug is None:
        is_debug = False

    # Create a slacker, itc and gplay reporters
    slacker = Slacker(slack_response_url, BOT_TOKEN, is_debug)
    itc_reporter = ITCReporter(Credentials(ITC_ACC_NUMBER, ITC_TOKEN, 'Robot.XML'))
    gpc_reporter = GooglePlayReporter(GPLAY_SERVICE_ACC, GPLAY_CFG_JSON)

    # Create Niallbot
    niallBot = NiallBot(slacker, itc_reporter, gpc_reporter)

    # Download statistics and
    niallBot.report_statistics()

    return "200 OK"
