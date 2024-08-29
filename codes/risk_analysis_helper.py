def get_iba_full_puid_value(custom_fields):
    iba_full_puid_value = next(
        (item['value'] for item in custom_fields['Custom'] if item['key'] == 'ibaFullPuid'),
        None
    )
    return iba_full_puid_value


def get_hazardous_situation_value(custom_fields):
    hazardous_situation_value = next(
        (item['value']['content'] for item in custom_fields['Custom'] if item['key'] == 'ibaHazardousSituation'),
        None
    )
    return hazardous_situation_value


def get_initiating_event_value(custom_fields):
    initiating_event_value = next(
        (item['value']['content'] for item in custom_fields['Custom'] if item['key'] == 'ibaInitiatingEvent'),
        None
    )
    return initiating_event_value


def get_harm_value(custom_fields):
    harm_value = next(
        (item['value']['content'] for item in custom_fields['Custom'] if item['key'] == 'ibaHarm'),
        None
    )
    return harm_value


def get_ra_failure_mode_value(custom_fields):
    ra_failure_mode_value = next(
        (item['value']['content'] for item in custom_fields['Custom'] if item['key'] == 'ibaRAFailureMode'),
        None
    )
    return ra_failure_mode_value


def get_ra_cause_value(custom_fields):
    ra_cause_value = next(
        (item['value']['content'] for item in custom_fields['Custom'] if item['key'] == 'ibaRACause'),
        None
    )
    return ra_cause_value


def get_ra_effects_value(custom_fields):
    ra_effects_value = next(
        (item['value']['content'] for item in custom_fields['Custom'] if item['key'] == 'ibaRAEffects'),
        None
    )
    return ra_effects_value
