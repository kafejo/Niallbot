#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib, urllib2, json, zlib, datetime

VERSION = '2.2'
ENDPOINT_SALES = 'https://reportingitc-reporter.apple.com/reportservice/sales/v1'
ENDPOINT_FINANCE = 'https://reportingitc-reporter.apple.com/reportservice/finance/v1'


class Credentials:
    def __init__(self, account_number, accessToken, mode):
        self.account_number = account_number
        self.accessToken = accessToken
        self.mode = mode

class ITCReporter:

    def __init__(self, credentials):
        self.credentials = credentials

    def get_vendors(self):
        command = 'Sales.getVendors'
        request = APIClient.post_request(ENDPOINT_SALES, self.credentials, command)
        return ITCReporter.get_content(request)

    def get_status(self, service):
        command = service + '.getStatus'
        endpoint = ENDPOINT_SALES if service == 'Sales' else ENDPOINT_FINANCE
        request = APIClient.post_request(endpoint, self.credentials, command)
        return ITCReporter.get_content(request)

    def get_accounts(self, service):
        command = service + '.getAccounts'
        endpoint = ENDPOINT_SALES if service == 'Sales' else ENDPOINT_FINANCE
        request = APIClient.post_request(endpoint, self.credentials, command)
        return ITCReporter.get_content(request)

    def get_sales_report(self, vendor, report_type='Sales', report_subtype='Summary', date_type='Daily',
                         date=datetime.date.today()):
        params = ','.join([vendor, report_type, report_subtype, date_type, date.strftime("%Y%m%d")])
        command = 'Sales.getReport, ' + params
        request = APIClient.post_request(ENDPOINT_SALES, self.credentials, command)
        return ITCReporter.get_content(request)

    def get_financial_report(self, vendor, region_code, fiscal_year, fiscal_period):
        command = 'Finance.getReport, {0},{1},Financial,{2},{3}'.format(vendor, region_code, fiscal_year, fiscal_period)
        request = APIClient.post_request(ENDPOINT_FINANCE, self.credentials, command)
        return ITCReporter.get_content(request)

    def get_vendor_and_regions(self):
        command = 'Finance.getVendorsAndRegions'
        request = APIClient.post_request(ENDPOINT_FINANCE, self.credentials, command)
        return ITCReporter.get_content(request)

    @staticmethod
    def get_content(result):
        """Output (and when necessary unzip) the result of the request to the screen or into a report file"""

        content, header = result

        # unpack content if it is gzip compressed.
        if header.gettype() == 'application/a-gzip':
            return zlib.decompress(content, 15 + 32)
        else:
            return content


class APIClient:

    @staticmethod
    def post_request(endpoint, credentials, command):
        """Execute the HTTP POST request"""
        print(command)
        command = "[p=Reporter.properties, %s]" % command
        request_data = APIClient.build_json_request_string(credentials, command)
        request = urllib2.Request(endpoint, request_data)
        request.add_header('Accept', 'text/html,image/gif,image/jpeg; q=.2, */*; q=.2')

        try:
            response = urllib2.urlopen(request)
            content = response.read()
            header = response.info()

            return content, header
        except urllib2.HTTPError, e:
            if e.code == 400 or e.code == 401 or e.code == 403 or e.code == 404:
                # for these error codes, the body always contains an error message
                raise ValueError(e.read())
            else:
                raise ValueError("HTTP Error %s. Did you choose reasonable query arguments?" % str(e.code))

    @staticmethod
    def build_json_request_string(credentials, query):
        """Build a JSON string from the urlquoted credentials and the actual query input"""

        request_data = dict(version=VERSION, mode=credentials.mode, queryInput=query)
        request_data.update(account=credentials.account_number)  # empty account info would result in error 404
        request_data.update(accesstoken=credentials.accessToken)

        request = {k: urllib.quote_plus(v) for k, v in request_data.items()}
        request = json.dumps(request)

        return 'jsonRequest=' + request
