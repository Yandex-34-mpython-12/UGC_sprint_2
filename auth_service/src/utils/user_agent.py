from enum import Enum

from user_agents import parse


class DeviceType(Enum):
    web: str = 'web'
    mobile: str = 'mobile'
    smart: str = 'smart'


def get_type_from_user_agent(user_agent: str) -> DeviceType:
    parsed_ua = parse(user_agent)

    if parsed_ua.is_pc:
        return DeviceType.web
    elif parsed_ua.is_mobile:
        return DeviceType.mobile
    else:
        return DeviceType.smart
