
class AppHelper:
    # TODO: 他の方法
    # make_random_password
    # https://docs.djangoproject.com/en/dev/topics/auth/customizing/#django.contrib.auth.models.BaseUserManager.make_random_password
    @classmethod
    def generate_password(cls):
        return AppHelper.random_string(8)

    # アルファベット大文字小文字+数字(0-9, a-z, A-F)
    def random_string(length, chars=None):
        import random
        import string
        if chars is None:
            chars = string.digits + string.ascii_letters
        return ''.join([random.choice(chars) for i in range(length)])

