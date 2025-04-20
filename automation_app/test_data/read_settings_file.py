from test_data.config.config import Settings_Common, Settings_Rest_api, Settings_Graphql

def get_rest_api_settings(attribute):
    attribute_lower = attribute.lower()
    return Settings_Rest_api.get(attribute_lower)

def get_graphql_settings(attribute):
    attribute_lower = attribute.lower()
    return Settings_Graphql.get(attribute_lower)

def get_common_settings(attribute):
    attribute_lower = attribute.lower()
    return Settings_Common.get(attribute_lower)
