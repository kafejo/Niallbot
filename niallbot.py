# -*- coding: utf-8 -*-

from itc_reporter import *
from slacker import *
from calendar import monthrange
import csv
from config import *

"""This is where the magic happens.
"""

class NiallBot:

    def __init__(self, slacker, itc_reporter, gpc_reporter):
        self.itc_reporter = itc_reporter
        self.gpc_reporter = gpc_reporter
        self.slacker = slacker

    def report_statistics(self):

        end_date = datetime.date.today() - datetime.timedelta(days=1)

        # Report iOS
        ios_report_attachments, ios_sales = self.report_ios(end_date)

        if len(ios_report_attachments) > 0:  # Report only if there is something to report
            self.slacker.send(':appleinc: downloads:', ios_report_attachments)

        # Report Android
        an_report_attachments, an_sales = self.report_android(end_date)

        if len(an_report_attachments):  # Report only if there is something to report
            self.slacker.send(':android: downloads:', an_report_attachments)

        # Generate overall report
        overall_attachments = NiallBot.report_overall(end_date, ios_sales, an_sales)

        if len(overall_attachments):  # Report only if there is something to report
            self.slacker.send('That\'s in *overall* :nerd_face: :', overall_attachments)

    @staticmethod
    def report_overall(end_date, ios_sales, an_sales):
        sales = ios_sales + an_sales

        days_in_month = monthrange(end_date.year, end_date.month)[-1]
        overall_attachments = []

        for report_group in OVERALL_REPORT_IDS:
            group_sales = 0
            for app_id in report_group[0]:
                for sale in sales:
                    if sale[1] == app_id:
                        group_sales += sale[0]

            group_runrate = (group_sales / end_date.day) * days_in_month
            attachment = NiallBot.create_attachment(report_group[1], group_sales, group_runrate)
            overall_attachments.append(attachment)

        return overall_attachments

    # Generate iOS report from end_date to the beginning of the month
    def report_ios(self, end_date):
        end_date_day_index = end_date.day
        # Build array of tuples of (sales_count, SKU, title)
        sales = map(lambda x: [0, x[0], x[1]], ITC_SKUS)

        # Download reports for each day to the beginning of the month
        while end_date_day_index >= 1:
            report_date = end_date.replace(day=end_date_day_index)
            end_date_day_index -= 1
            try:
                report = self.itc_reporter.get_sales_report(ITC_VENDOR_ID, report_type='Sales', date_type='Daily',
                                                            date=report_date)
            except ValueError:
                # If reports is not available, just skip it
                continue

            # Get sales from downloaded report for each SKU
            for index, sale in enumerate(sales):
                sales[index][0] += NiallBot.sales_from_report(report, sale[1])

        days_in_month = monthrange(end_date.year, end_date.month)[-1]
        slack_attachments = []

        # Generate slack attachments for each sale
        for sale in sales:
            sales_count = sale[0]
            title = sale[2]
            run_rate = (sales_count / end_date.day) * days_in_month
            slack_attachments.append(NiallBot.create_attachment(title, sales_count, run_rate))

        return slack_attachments, sales

    def report_android(self, end_date):
        days_in_month = monthrange(end_date.year, end_date.month)[-1]
        slack_attachments = []
        sales = map(lambda x: [0, x[0], x[1], x[2]], GPLAY_IDS)

        for index, sale in enumerate(sales):
            app_id = sale[1]
            bucket = sale[2]
            report = self.gpc_reporter.get_installs_report(bucket, app_id, end_date)
            sales_count = NiallBot.count_google_sales(report)
            sales[index][0] = sales_count
            run_rate = (sales_count / end_date.day) * days_in_month
            attachment = NiallBot.create_attachment(sale[3], sales_count, run_rate)
            slack_attachments.append(attachment)

        return slack_attachments, sales

    @staticmethod
    def create_attachment(title, sales_count, run_rate):
        invest_sales_field = AttachmentField(':bar_chart: This month', sales_count, True)
        invest_runrate_field = AttachmentField(':runner: Runrate', run_rate, True)

        return Attachment(title, [invest_sales_field, invest_runrate_field])

    @staticmethod
    def count_google_sales(report):
        installs = 0

        for row in report:
            try:
                installs += int(row[6])
            except Exception:
                continue

        return installs

    @staticmethod
    def sales_from_report(report, sku):

        decoded_content = report.decode('utf-8')
        invr = list(csv.reader(decoded_content.splitlines(), delimiter='\t'))

        sales = 0

        for row in invr:
            if row[2] == sku and (any(x in row[6] for x in ['1'])):
                sales += int(row[7])

        return sales
