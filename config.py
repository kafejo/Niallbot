import os

# You can use ITCReporter.get_vendors function to get all vendors for your account
ITC_VENDOR_ID = os.environ['ITC_VENDOR_ID']
# Each app in vendor sales report is identified by its SKU. Define which one you want to include in your report.
ITC_SKUS = map(lambda x: x.split(';'), os.environ['ITC_SKUS'].split('|'))
# Each app on google play (app_id, bucket, title)
GPLAY_IDS = map(lambda x: x.split(';'), os.environ['GPLAY_IDS'].split('|'))
# Overall report array of ([list_of_ids_to_group], title)
OVERALL_REPORT_IDS = map(lambda x: map(lambda y: y.split('~'), x.split(';')), os.environ['OVERALL_REPORT_IDS'].split('|'))
# Slack BOT OAUTH2 token
BOT_TOKEN = os.environ['BOT_TOKEN']
# iTunes connect Account number
ITC_ACC_NUMBER = os.environ['ITC_ACC_NUMBER']
# iTunes Connect token (at the moment you need to generate one through their reporter.jar)
ITC_TOKEN = os.environ['ITC_TOKEN']
# Google play service account email address to access reports
GPLAY_SERVICE_ACC = os.environ['GPLAY_SERVICE_ACC']
# Google JSON configuration file
GPLAY_CFG_JSON = os.environ['GPLAY_CFG_JSON']