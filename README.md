# NiallBot
Slack slash command for iOS and Android download stats designed for AWS Lambda.

<img src="resources/screenshot.png" width="600"/>

## How it works
NiallBot is written in Python 2.7 and is prepared to be deployed to AWS Lambda. It uses iTunes Connect API to download sales reports and extract values from them. It also reads Google Play reports. At the moment it gives monthly downloads and run rates (see screenshot). Everything is configurable via enviroment variables so you don't have to touch the code.

## Installation
Clone repository, ZIP it and upload to AWS Lambda. But…

### Reporting Android
In order to access Google play reports, you need to generate configuration and create sevice account. The easiest way to do so is to follow [Google Cloud Getting Started Guidelines](https://cloud.google.com/docs/authentication/getting-started). When you create a service account, you'll get a json configuration file that you need to append to your ZIP archive. Then you need to specify its name in enviroment variable.

### Enviroment variables
+ `BOT_TOKEN` - Slack BOT OAUTH2 token
+ `ITC_ACC_NUMBER` - iTunes connect Account number
+ `ITC_TOKEN` - iTunes Connect token (at the moment you need to generate one through their reporter.jar)
+ `GPLAY_SERVICE_ACC` - Google play service account email address to access reports
+ `GPLAY_CFG_JSON` - Google JSON configuration file
+ `ITC_VENDOR_ID` - Your iTunes connect vendor ID. You can use ITCReporter.get_vendors function to get all vendors for your account

#### Report configuration variables
These have special format how to define them. Use `|` to separate items in array, `;` to separate items in second-level inner array and `~` for third-level inner arrays. Titles are just strings that will be displayed in the report.
+ `ITC_SKUS` - Each iOS app in vendor sales report is identified by its SKU. Define which one you want to include in your report. [[sku, title]]
+ `GPLAY_IDS` - Each app on google play [[app_id, bucket, title]]
+ `OVERALL_REPORT_IDS` - IDs of apps to include in the overall report. [[list_of_ids], title]

#### Example configuration
```python
'BOT_TOKEN' = 'xoxb-XXXXXxxxxxx'
'ITC_ACC_NUMBER' = '30235800'
'ITC_TOKEN' = '3ddds0d-aeed-4c7f-8dda-0e03006d1b3'
'GPLAY_SERVICE_ACC' = 'niallbot@myapp.iam.gserviceaccount.com'
'GPLAY_CFG_JSON' = 'Appname-4db30e3302d6.json'
'ITC_VENDOR_ID' = '12345677'
'ITC_SKUS' = '20160203;iOS App 1|22350522;iOS App 2'
'GPLAY_IDS' = 'com.test.app1;pubsite_prod_rev_00000;Android App 1|com.test.app2;pubsite_prod_rev_0000001;Android App 2'
'OVERALL_REPORT_IDS' = 'com.test.app1~20160203;App 1|com.test.app2~22350522;App 2'
```
This will generate a report like this:

<img src="resources/screenshot-two-apps.png" width="600"/>

As you can see, there we are reporting two iOS apps (iOS App 1 and iOS App 2) and two Android apps (Android App 1 and Android App 2) and in the overall report we combine iOS and Android apps (iOS App 1 and Android App 1) and (iOS App 2 and Android App 2).

You can simply adjust the configuration to suit your needs. For example report for only 1 iOS and 1 Android app.
```python
'BOT_TOKEN' = 'xoxb-XXXXXxxxxxx'
'ITC_ACC_NUMBER' = '30235800'
'ITC_TOKEN' = '3ddds0d-aeed-4c7f-8dda-0e03006d1b3'
'GPLAY_SERVICE_ACC' = 'niallbot@myapp.iam.gserviceaccount.com'
'GPLAY_CFG_JSON' = 'Appname-4db30e3302d6.json'
'ITC_VENDOR_ID' = '12345677'
'ITC_SKUS' = '20160203;iOS App 1'  # SKU;title
'GPLAY_IDS' = 'com.test.app1;pubsite_prod_rev_00000;Android App 1'  # app_id;bucket_for_report;title
'OVERALL_REPORT_IDS' = 'com.test.app1~20160203;App 1'  #SKU or app_id separated by ~;title
```

<img src="resources/screenshot-single-app.png" width="600"/>

### How to setup AWS Lambda
Due to the nature of iTunes Connect API, it takes around 10-20 seconds to download all the reports (depending on month, report needed for each day). Slack slashcommand requires you to respond within 3 seconds. That's why I designed it in a way that one lambda handles all the slash commands and if needed invokes asynchronously another lambda and passes `response_url` (the slack url to respond). Here's example of our lambda function that is being triggered by the slack slash command:

```python
# -*- coding: utf-8 -*-
import boto3
import json

def lambda_handler(event, context):
    
    payload = json.dumps({"response_url": event["response_url"]})
    
    if event['text'] == 'downloads':
        
        lambda_client = boto3.client('lambda')
        lambda_client.invoke(FunctionName="niallbot-downloads", InvocationType='Event', Payload=payload)
    
        return {"response_type": "in_channel","text": "Just give me a sec… :point_up:"}
    if event['text'] == 'help':
        return {"response_type": "ephemeral","text": "Usage: `/niallbot <command>`\nCommands:\n`downloads` - monthly report of downloads and run rates up to date"}
    else:
        return {"response_type": "ephemeral","text": "Sorry, I don't know how to do that.\nTry `/niallbot help` command"}

```

### Test enviroment
You can test your function locally, just create a new file in the repository fill all the enviroment variables.

```python

import os
os.environ['BOT_TOKEN'] = 'xoxb-xxx'
os.environ['ITC_ACC_NUMBER'] = '123456'
os.environ['ITC_TOKEN'] = 'o231no231n-aeed-o2n3o-859a-no213on13'
os.environ['GPLAY_SERVICE_ACC'] = 'niallbot@app.iam.gserviceaccount.com'
os.environ['GPLAY_CFG_JSON'] = 'Invest-30131n0d1nd1d0.json'
os.environ['ITC_VENDOR_ID'] = '123456789'
os.environ['ITC_SKUS'] = '20160203;iOS App 1'
os.environ['GPLAY_IDS'] = 'com.test.app1;pubsite_prod_rev_00000;Android App 1'
os.environ['OVERALL_REPORT_IDS'] = 'com.test.app1~20160203;App 1'

from lambda_function import lambda_handler

lambda_handler({'is_debug': True, 'response_url': 'test'}, {})
```

When you pass `is_debug = True`, it will just print the composed slack message to console.
