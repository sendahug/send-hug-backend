"""
Push notifications related methods.
"""
from typing import Dict, Union
from datetime import datetime, timedelta


def generate_push_data(data: Dict) -> Dict[str, str]:
    """
    Generates the push notification's data from the
    given raw data.
    """
    notification_data = {
        'title': 'New ' + data['type'],
        'body': data['text']
    }

    return notification_data


def generate_vapid_claims() -> Dict[str, Union[str, float]]:
    """
    Generates the VAPID claims dictionary.
    """
    expiry_time = datetime.timestamp(datetime.utcnow() +
                                      timedelta(hours=12))
    vapid_claims = {
        'sub': 'mailto:theobjectivistb@gmail.com',
        'exp': expiry_time
    }

    return vapid_claims