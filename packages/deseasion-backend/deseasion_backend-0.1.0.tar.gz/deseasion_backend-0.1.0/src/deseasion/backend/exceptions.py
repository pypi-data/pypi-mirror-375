class RequestError(Exception):
    """Used generate error messages for the http responses"""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Constructor

        Args:
            message (str): the message to send to the client
            code (int): the http error code (optionnal)
            payload (dict): additionnal information (optionnal)
        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def __str__(self):
        return "Error {}: {}".format(self.status_code, self.message)

    def to_dict(self):
        data = dict(self.payload or ())
        data["message"] = self.message
        return data


class InvalidValue(RequestError):
    """Used to indicate an incorrect value for a field"""

    status_code = 400

    def __init__(self, message):
        return super().__init__(message=message)


class PermissionError(RequestError):
    status_code = 403

    def __init__(self, message="Permission denied"):
        return super().__init__(message=message)


class UserTokenError(Exception):
    """Used to indicate a user could not be associated with a json web token"""

    pass


class ProcessingError(Exception):
    """Used to indicate the error in the processing of a criterion"""

    pass


class InferenceError(Exception):
    """Used to indicate an error in the inference of the MR-Sort model."""

    pass


class UploadError(Exception):
    """Used to indicate a problem on uploaded files"""

    pass


class GeometryTypeError(TypeError):
    """Used to indicate the a geometry does not have the correct type"""

    pass


class InvalidAuthenticationHeader(Exception):
    """Used to indicate that the authentication header is not valid"""

    pass


class ExternalRequestError(Exception):
    """Used to indicate an external request to third party server failed.

    :param url: request tried
    :param msg: error message
    :param request_type: type of request tried, defaults 'External'
    """

    request_type = "External"

    def __init__(self, url: str, msg: str = None, request_type: str = None):
        self.url = url
        self.msg = msg or ""
        if request_type is not None:
            self.request_type = request_type

    def __str__(self) -> str:
        return f"{self.request_type} request {self.url} failed: {self.msg}"


class CapabilitiesXMLParsingError(Exception):
    """Used to indicate a parsing error on a XML GetCapabilities response
    (WMS/WFS)
    """

    pass
