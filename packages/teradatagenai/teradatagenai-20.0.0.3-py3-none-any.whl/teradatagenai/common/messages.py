# ##################################################################
#
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Snigdha Biswas (snigdha.biswas@teradata.com)
# Secondary Owner: Aanchal Kavedia (aanchal.kavedia@teradata.com)
#
# Notes:
#   * This code is only for internal use.
#   * This file includes the teradatgenai error messages.
#
# ##################################################################
from teradatagenai.common.message_codes import MessageCodes

class Messages:
    """
    Class to store and retrieve error messages for the teradatagenai package.
    """
    __standard_message = "[Teradata][teradatagenai]"
    _messages = {
        MessageCodes.METHOD_NOT_IMPLEMENTED: "Method is not supported for the api_type '{api_type}'",
        MessageCodes.INVALID_FUNCTION_PARAMETER: "Parameters {params} not are suported by {api}().",
        MessageCodes.ATTRIBUTE_UNAVAILABLE: "Attribute '{attribute_name}' not available when '{attribute_name_1}' is '{value}'."
    }

    @staticmethod
    def get_message(code, *args, **kwargs):
        """
        Retrieves and formats the error message for the given code.

        PARAMETERS:
            code:
                The message code to retrieve the message for.
                Types: str

            *args, **kwargs:
                Additional arguments to format the message.

        RETURNS:
            str
        """
        if code not in Messages._messages:
            raise ValueError(f"Message code '{code}' not found.")
        message = "{}({}) {}".format(Messages.__standard_message, code, Messages._messages[code])
        return message.format(*args, **kwargs)