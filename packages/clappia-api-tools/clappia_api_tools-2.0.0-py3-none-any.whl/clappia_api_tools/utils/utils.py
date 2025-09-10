import phonenumbers
from phonenumbers import (
    NumberParseException,
    is_valid_number,
    format_number,
    PhoneNumberFormat,
)


class Utils:
    def __init__(self):
        pass

    def validate_phone_number(
        self, phone: str, default_region: str = "IN"
    ) -> str | None:
        """
        Validate and format a phone number.

        :param phone: Phone number string input
        :param default_region: Default region code (e.g., 'IN', 'US')
        :return: E.164 formatted number if valid, None otherwise
        """
        try:
            parsed = phonenumbers.parse(phone, default_region)
            if is_valid_number(parsed):
                # Return in E.164 format: +[country code][number]
                return format_number(parsed, PhoneNumberFormat.E164)
            return None
        except NumberParseException:
            return None
