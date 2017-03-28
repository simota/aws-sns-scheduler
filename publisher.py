# -*- Coding: utf-8 -*-
import sys
import boto.sns
import json
import concurrent.futures
from pprint import pprint
import settings


def create_client():
    return boto.sns.connect_to_region(
        settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)


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
    payload['default'] = message
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
    return _get_application_endpoints(application_arn, endpoints, next_token=token)


def _get_endpoints():
    endpoints = []
    endpoints = endpoints + _get_application_endpoints(settings.IOS_ARN, [])
    endpoints = endpoints + \
        _get_application_endpoints(settings.ANDROID_ARN, [])
    return endpoints


def publish_targets():
    targets = {}
    targets['ios'] = len(_get_application_endpoints(settings.IOS_ARN, []))
    targets['android'] = len(
        _get_application_endpoints(settings.ANDROID_ARN, []))
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


def publish_to_topic(message):
    payload = _create_payload(message)
    for arn in settings.TOPIC_ARN_LIST:
        res = sns_client.publish(
            message=payload,
            message_structure='json',
            target_arn=arn)
        pprint(res)


def publish(message):
    payload = _create_payload(message)
    endpoints = _get_endpoints()
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=7)
    futures = [executor.submit(_publish, payload, endpoint)
               for endpoint in endpoints]
    for future in concurrent.futures.as_completed(futures):
        print future.result(),
    executor.shutdown()
