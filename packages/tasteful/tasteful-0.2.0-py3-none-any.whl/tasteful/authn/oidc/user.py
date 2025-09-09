from tasteful.authn.base import BaseUser


class OIDCUser(BaseUser):
    user_info: dict
