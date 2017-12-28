# -*- coding: utf-8 -*-

from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import csv


class GooglePlayReporter:

    def __init__(self, client_email, json_file):
        self.client_email = client_email
        self.json_file = json_file

    # it downloads a report for a month of a given date
    def get_installs_report(self, bucket, app_id, date):
        # https://console.developers.google.com/storage/:bucket:/stats/installs/
        cloud_storage_bucket = bucket

        report_to_download = 'stats/installs/installs_{0}_{1}_overview.csv'.format(app_id, date.strftime("%Y%m"))

        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_file, scopes=['https://www.googleapis.com/auth/devstorage.read_only'])
        storage = build('storage', 'v1', http=credentials.authorize(Http()))
        content = storage.objects().get_media(bucket=cloud_storage_bucket, object=report_to_download).execute()
        decoded_content = content.decode('utf-16')
        installs = list(csv.reader(decoded_content.splitlines(), delimiter='\t'))

        return installs
