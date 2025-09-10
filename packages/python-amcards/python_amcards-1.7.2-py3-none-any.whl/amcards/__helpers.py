import time
from typing import Optional
import datetime

REQUIRED_SHIPPING_ADDRESS_FIELDS = {
    'first_name',
    'last_name',
    'address_line_1',
    'city',
    'state',
    'postal_code',
}

REQUIRED_CONTACT_FIELDS = {
    'first_name',
    'last_name',
    'address_line_1',
    'city',
    'state',
    'postal_code',
}

OPTIONAL_CONTACT_FIELDS = {
    'country',
    'organization',
    'phone_number',
    'birth_date',
    'anniversary_date',
    'third_party_contact_id',
    'address_line_2',
    'extra_data',
}

CARD_OPTIONAL_SHIPPING_ADDRESS_FIELDS = {
    'country',
    'organization',
    'third_party_contact_id',
    'address_line_2',
}

CAMPAIGN_OPTIONAL_SHIPPING_ADDRESS_FIELDS = {
    'country',
    'organization',
    'phone_number',
    'birth_date',
    'anniversary_date',
    'third_party_contact_id',
    'address_line_2',
}

OPTIONAL_RETURN_ADDRESS_FIELDS = {
    'first_name',
    'last_name',
    'address_line_1',
    'city',
    'state',
    'postal_code',
    'country',
}

def current_timestamp() -> int:
    return int(time.time() * 1000)

def today() -> str:
    today = datetime.datetime.today()
    yyyy = today.year
    mm, dd = map(lambda x: str(x).zfill(2), (today.month, today.day))
    return f'{yyyy}-{mm}-{dd}'

def to_datetime(datetime_str: Optional[str]) -> Optional[datetime.datetime]:
    if datetime_str is None:
        return None

    if 'T' in datetime_str:
        if '.' in datetime_str:
            return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S')

    if ' ' in datetime_str:
        if '.' in datetime_str:
            return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    if '.' in datetime_str:
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d%H:%M:%S.%f')
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%d%H:%M:%S')

def format_cents(price_in_cents: int) -> str:
    whole, fractional = map(str, divmod(price_in_cents, 100))
    fractional = fractional.zfill(2)
    return f'${whole}.{fractional}'

def get_missing_required_shipping_address_fields(shipping_address: dict) -> list:
    missings = []
    for req in REQUIRED_SHIPPING_ADDRESS_FIELDS:
        if (shipping_address.get(req, '') or '').strip(): continue
        missings.append(req)
    return missings

def is_valid_date(date: str) -> bool:
    if not isinstance(date, str):
        return False
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except:
        return False

def is_valid_birthdate(date: str) -> bool:
    if not isinstance(date, str):
        return False
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except:
        pass
    try:
        datetime.datetime.strptime(date, '%m-%d')
        return True
    except:
        return False

def is_valid_phone(phone: str) -> bool:
    if not isinstance(phone, str): return False
    return len(phone) == 10 and phone.isdigit()

def sanitize_extra_data(extra_data: dict) -> Optional[dict]:
    if not isinstance(extra_data, dict): return None
    return {k: v for k, v in extra_data.items() if isinstance(k, str) and isinstance(v, str)}

def sanitize_shipping_address_for_card_send(shipping_address: dict) -> dict:
    sanitized_shipping_address = {field: shipping_address[field] for field in REQUIRED_SHIPPING_ADDRESS_FIELDS}
    for optional in CARD_OPTIONAL_SHIPPING_ADDRESS_FIELDS:
        if not shipping_address.get(optional): continue
        sanitized_shipping_address[optional] = shipping_address[optional]
    return sanitized_shipping_address

def sanitize_shipping_address_for_campaign_send(shipping_address: dict) -> dict:
    sanitized_shipping_address = {field: shipping_address[field] for field in REQUIRED_SHIPPING_ADDRESS_FIELDS}
    for optional in CAMPAIGN_OPTIONAL_SHIPPING_ADDRESS_FIELDS:
        if not shipping_address.get(optional): continue
        sanitized_shipping_address[optional] = shipping_address[optional]
    return sanitized_shipping_address

def sanitize_contact_for_campaign_multi_send(contact: dict) -> dict:
    sanitized_contact = {field: contact[field] for field in REQUIRED_CONTACT_FIELDS}
    for optional in OPTIONAL_CONTACT_FIELDS:
        if not contact.get(optional): continue
        sanitized_contact[optional] = contact[optional]
    return sanitized_contact

def sanitize_return_address(return_address: dict) -> dict:
    sanitized_return_address = {}
    for optional in OPTIONAL_RETURN_ADDRESS_FIELDS:
        if optional not in return_address: continue
        sanitized_return_address[optional] = return_address[optional]
    return sanitized_return_address

def repr(cls):
    props = [(prop, getattr(cls, prop)) for prop in dir(cls) if not prop.startswith('_')]
    return '(' + ', '.join([f'{k}={v}' for k, v in props]) + ')'

def parse_shipping_address(json: dict) -> dict:
    shipping_address = {}
    for key, value in json.items():
        match key[8:]:
            case 'city': shipping_address['city'] = value
            case 'country': shipping_address['country'] = value
            case 'first_name': shipping_address['first_name'] = value
            case 'last_name': shipping_address['last_name'] = value
            case 'line_1': shipping_address['address_line_1'] = value
            case 'organization' if value: shipping_address['organization'] = value
            case 'postal': shipping_address['postal_code'] = value
            case 'state': shipping_address['state'] = value
    if json['third_party_contact_id']:
        shipping_address['third_party_contact_id'] = json['third_party_contact_id']
    return shipping_address

def parse_return_address(json: dict) -> dict:
    return_address = {}
    for key, value in json.items():
        match key[10:]:
            case 'city': return_address['city'] = value
            case 'country': return_address['country'] = value
            case 'first_name': return_address['first_name'] = value
            case 'last_name': return_address['last_name'] = value
            case 'line_1': return_address['address_line_1'] = value
            case 'postal': return_address['postal_code'] = value
            case 'state': return_address['state'] = value
    return return_address
