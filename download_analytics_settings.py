import os
import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
from datetime import datetime

# Replace with the path to your client_secret.json
CLIENT_SECRET_FILE = 'path/to/client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

def initialize_analytics():
    creds = None
    token_path = 'token.pickle'
    
    # Check if token.pickle file exists to use saved credentials
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials are available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    analytics = build('analytics', 'v3', credentials=creds)
    return analytics

def get_accounts(analytics):
    accounts = analytics.management().accounts().list().execute()
    return accounts.get('items', [])

def get_properties(analytics, account_id):
    properties = analytics.management().webproperties().list(accountId=account_id).execute()
    return properties.get('items', [])

def get_views(analytics, account_id, property_id):
    views = analytics.management().profiles().list(accountId=account_id, webPropertyId=property_id).execute()
    return views.get('items', [])

def get_segments(analytics):
    segments = analytics.management().segments().list().execute()
    return segments.get('items', [])

def get_filters(analytics, account_id):
    filters = analytics.management().filters().list(accountId=account_id).execute()
    return filters.get('items', [])

def get_profile_filter_links(analytics, account_id, property_id, view_id):
    profile_filter_links = analytics.management().profileFilterLinks().list(
        accountId=account_id, webPropertyId=property_id, profileId=view_id).execute()
    return profile_filter_links.get('items', [])

def get_goals(analytics, account_id, property_id, view_id):
    goals = analytics.management().goals().list(
        accountId=account_id, webPropertyId=property_id, profileId=view_id).execute()
    return goals.get('items', [])

def get_uploads(analytics, account_id, property_id, custom_data_source_id):
    uploads = analytics.management().uploads().list(
        accountId=account_id, webPropertyId=property_id, customDataSourceId=custom_data_source_id).execute()
    return uploads.get('items', [])

def get_custom_dimensions(analytics, account_id, property_id):
    custom_dimensions = analytics.management().customDimensions().list(
        accountId=account_id, webPropertyId=property_id).execute()
    return custom_dimensions.get('items', [])

def get_custom_metrics(analytics, account_id, property_id):
    custom_metrics = analytics.management().customMetrics().list(
        accountId=account_id, webPropertyId=property_id).execute()
    return custom_metrics.get('items', [])

def save_to_csv(data, filename, output_dir):
    df = pd.DataFrame(data)
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(os.path.join(output_dir, filename), index=False)

def main():
    analytics = initialize_analytics()

    all_settings = []
    segment_settings = []
    filter_settings = []
    profile_filter_link_settings = []
    goal_settings = []
    custom_dimension_settings = []
    custom_metric_settings = []
    view_settings = []

    accounts = get_accounts(analytics)
    for account in accounts:
        account_id = account['id']
        properties = get_properties(analytics, account_id)
        for property in properties:
            property_id = property['id']
            views = get_views(analytics, account_id, property_id)
            for view in views:
                view_id = view['id']

                settings = {
                    'account_id': account_id,
                    'account_name': account['name'],
                    'property_id': property_id,
                    'property_name': property['name'],
                    'view_id': view_id,
                    'view_name': view['name'],
                }
                all_settings.append(settings)

                view_info = {
                    'id': view['id'],
                    'kind': view.get('kind'),
                    'selfLink': view.get('selfLink'),
                    'accountId': view.get('accountId'),
                    'webPropertyId': view.get('webPropertyId'),
                    'internalWebPropertyId': view.get('internalWebPropertyId'),
                    'name': view.get('name'),
                    'currency': view.get('currency'),
                    'timezone': view.get('timezone'),
                    'websiteUrl': view.get('websiteUrl'),
                    'defaultPage': view.get('defaultPage'),
                    'excludeQueryParameters': view.get('excludeQueryParameters'),
                    'siteSearchQueryParameters': view.get('siteSearchQueryParameters'),
                    'stripSiteSearchQueryParameters': view.get('stripSiteSearchQueryParameters'),
                    'siteSearchCategoryParameters': view.get('siteSearchCategoryParameters'),
                    'stripSiteSearchCategoryParameters': view.get('stripSiteSearchCategoryParameters'),
                    'type': view.get('type'),
                    'permissions': view.get('permissions', {}).get('effective'),
                    'created': view.get('created'),
                    'updated': view.get('updated'),
                    'eCommerceTracking': view.get('eCommerceTracking'),
                    'enhancedECommerceTracking': view.get('enhancedECommerceTracking'),
                    'botFilteringEnabled': view.get('botFilteringEnabled'),
                    'starred': view.get('starred'),
                    'parentLink': view.get('parentLink', {}).get('href'),
                    'childLink': view.get('childLink', {}).get('href')
                }
                view_settings.append(view_info)

                profile_filter_links = get_profile_filter_links(analytics, account_id, property_id, view_id)
                for link in profile_filter_links:
                    profile_filter_link_settings.append({
                        'account_id': account_id,
                        'property_id': property_id,
                        'view_id': view_id,
                        'filter_id': link['filterRef']['id'],
                        'link_id': link['id']
                    })

                goals = get_goals(analytics, account_id, property_id, view_id)
                for goal in goals:
                    goal_settings.append({
                        'account_id': account_id,
                        'property_id': property_id,
                        'view_id': view_id,
                        'goal_id': goal['id'],
                        'goal_name': goal['name']
                    })

            custom_dimensions = get_custom_dimensions(analytics, account_id, property_id)
            for dimension in custom_dimensions:
                custom_dimension_settings.append({
                    'account_id': account_id,
                    'property_id': property_id,
                    'dimension_id': dimension['id'],
                    'dimension_name': dimension['name'],
                    'kind': dimension.get('kind'),
                    'index': dimension.get('index'),
                    'scope': dimension.get('scope'),
                    'active': dimension.get('active'),
                    'created': dimension.get('created'),
                    'updated': dimension.get('updated'),
                    'selfLink': dimension.get('selfLink'),
                    'parentLink': dimension.get('parentLink', {}).get('href')
                })

            custom_metrics = get_custom_metrics(analytics, account_id, property_id)
            for metric in custom_metrics:
                custom_metric_settings.append({
                    'account_id': account_id,
                    'property_id': property_id,
                    'metric_id': metric['id'],
                    'metric_name': metric['name']
                })

    segments = get_segments(analytics)
    for segment in segments:
        segment_settings.append({
            'segment_id': segment['id'],
            'segment_name': segment['name'],
            'definition': segment.get('definition'),
            'kind': segment.get('kind'),
            'type': segment.get('type'),
            'created': segment.get('created'),
            'updated': segment.get('updated')
        })

    for account in accounts:
        account_id = account['id']
        filters = get_filters(analytics, account_id)
        for filter in filters:
            filter_info = {
                'account_id': account_id,
                'filter_id': filter['id'],
                'kind': filter.get('kind'),
                'selfLink': filter.get('selfLink'),
                'name': filter.get('name'),
                'type': filter.get('type'),
                'created': filter.get('created'),
                'updated': filter.get('updated'),
                'parentLink': filter.get('parentLink', {}).get('href')
            }

            include_details = filter.get('includeDetails')
            if include_details:
                filter_info.update({
                    'include_kind': include_details.get('kind'),
                    'include_field': include_details.get('field'),
                    'include_matchType': include_details.get('matchType'),
                    'include_expressionValue': include_details.get('expressionValue'),
                    'include_caseSensitive': include_details.get('caseSensitive'),
                    'include_fieldIndex': include_details.get('fieldIndex')
                })

            exclude_details = filter.get('excludeDetails')
            if exclude_details:
                filter_info.update({
                    'exclude_kind': exclude_details.get('kind'),
                    'exclude_field': exclude_details.get('field'),
                    'exclude_matchType': exclude_details.get('matchType'),
                    'exclude_expressionValue': exclude_details.get('expressionValue'),
                    'exclude_caseSensitive': exclude_details.get('caseSensitive'),
                    'exclude_fieldIndex': exclude_details.get('fieldIndex')
                })

            lowercase_details = filter.get('lowercaseDetails')
            if lowercase_details:
                filter_info.update({
                    'lowercase_field': lowercase_details.get('field'),
                    'lowercase_fieldIndex': lowercase_details.get('fieldIndex')
                })

            uppercase_details = filter.get('uppercaseDetails')
            if uppercase_details:
                filter_info.update({
                    'uppercase_field': uppercase_details.get('field'),
                    'uppercase_fieldIndex': uppercase_details.get('fieldIndex')
                })

            search_and_replace_details = filter.get('searchAndReplaceDetails')
            if search_and_replace_details:
                filter_info.update({
                    'searchReplace_field': search_and_replace_details.get('field'),
                    'searchReplace_fieldIndex': search_and_replace_details.get('fieldIndex'),
                    'searchReplace_searchString': search_and_replace_details.get('searchString'),
                    'searchReplace_replaceString': search_and_replace_details.get('replaceString'),
                    'searchReplace_caseSensitive': search_and_replace_details.get('caseSensitive')
                })

            advanced_details = filter.get('advancedDetails')
            if advanced_details:
                filter_info.update({
                    'advanced_fieldA': advanced_details.get('fieldA'),
                    'advanced_fieldAIndex': advanced_details.get('fieldAIndex'),
                    'advanced_extractA': advanced_details.get('extractA'),
                    'advanced_fieldB': advanced_details.get('fieldB'),
                    'advanced_fieldBIndex': advanced_details.get('fieldBIndex'),
                    'advanced_extractB': advanced_details.get('extractB'),
                    'advanced_outputToField': advanced_details.get('outputToField'),
                    'advanced_outputToFieldIndex': advanced_details.get('outputToFieldIndex'),
                    'advanced_outputConstructor': advanced_details.get('outputConstructor'),
                    'advanced_fieldARequired': advanced_details.get('fieldARequired'),
                    'advanced_fieldBRequired': advanced_details.get('fieldBRequired'),
                    'advanced_overrideOutputField': advanced_details.get('overrideOutputField'),
                    'advanced_caseSensitive': advanced_details.get('caseSensitive')
                })

            filter_settings.append(filter_info)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join('output', timestamp)

    save_to_csv(all_settings, 'account_property_view_settings.csv', output_dir)
    save_to_csv(segment_settings, 'segment_settings.csv', output_dir)
    save_to_csv(filter_settings, 'filter_settings.csv', output_dir)
    save_to_csv(profile_filter_link_settings, 'profile_filter_link_settings.csv', output_dir)
    save_to_csv(goal_settings, 'goal_settings.csv', output_dir)
    save_to_csv(custom_dimension_settings, 'custom_dimension_settings.csv', output_dir)
    save_to_csv(custom_metric_settings, 'custom_metric_settings.csv', output_dir)
    save_to_csv(view_settings, 'view_settings.csv', output_dir)

if __name__ == '__main__':
    main()
