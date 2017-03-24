# -*- coding: utf-8 -*-
import sys
import boto.sns
import json
import concurrent.futures


ANDROID_ARM = 'arn:aws:sns:ap-northeast-1:345493687167:app/GCM/daice-android'
IOS_ARM = 'arn:aws:sns:ap-northeast-1:345493687167:app/APNS/daice-ios'


def create_client():
    AWS_REGION = 'ap-northeast-1'
    AWS_ACCESS_KEY = 'AKIAJMU2MW3SUZ6UFWIQ'
    AWS_SECRET_ACCESS_KEY = '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'
    return boto.sns.connect_to_region(
        AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


sns_client = create_client()


def _extract_endpoints(response):
    a = response['ListEndpointsByPlatformApplicationResponse']
    b = a['ListEndpointsByPlatformApplicationResult']
    c = b['Endpoints']
    d = filter(lambda x: x['Attributes']['Enabled'], c)
    return list(d)


def _extract_next_token(response):
    a = response['ListEndpointsByPlatformApplicationResponse']
    b = a['ListEndpointsByPlatformApplicationResult']
    return b['NextToken']


def _create_payload(message):
    payload = {}
    apns = {'aps': {'alert': message, 'badge': 1}}
    gcm = {'data': {'message': message}}
    payload['APNS'] = json.dumps(apns)
    payload['GCM'] = json.dumps(gcm)
    return json.dumps(payload)


def _get_application_endpoints(application_arn, endpoints, next_token=None):
    response = sns_client.list_endpoints_by_platform_application(
        platform_application_arn=application_arn, next_token=next_token)
    endpoints = endpoints + _extract_endpoints(response)
    token = _extract_next_token(response)
    if token is None:
        return endpoints
    return get_android_endpoints(application_arn, endpoints, next_token=token)


def _get_endpoints():
    endpoints = []
    endpoints = endpoints + _get_application_endpoints(IOS_ARM, [])
    endpoints = endpoints + _get_application_endpoints(ANDROID_ARM, [])
    return endpoints


def publish_targets():
    targets = {}
    targets['ios'] = len(_get_application_endpoints(IOS_ARM, []))
    targets['android'] = len(_get_application_endpoints(ANDROID_ARM, []))
    return targets


def _publish(payload, endpoint):
    try:
        sns_client.publish(
            message=payload,
            message_structure='json',
            target_arn=endpoint['EndpointArn'])
        return '.'
    except:
        print sys.exc_info()
        return 'x'


def publish(message):
    payload = _create_payload(message)
    endpoints = _get_endpoints()
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=7)
    futures = [executor.submit(_publish, payload, endpoint)
               for endpoint in endpoints]
    for future in concurrent.futures.as_completed(futures):
        print future.result(),
    executor.shutdown()
