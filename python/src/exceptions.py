from fastapi import HTTPException, status
class NotFoundException(Exception):
    pass

class NoUserException(NotFoundException):
    pass

class NoSampleException(NotFoundException):
    pass

class NoQrCodeException(NotFoundException):
    pass

class NoResearchException(NotFoundException):
    pass

class NoKitException(NotFoundException):
    pass

class HTTPForbiddenException(HTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=self.status_code, *args, **kwargs)
        

class HTTPNotFoundException(HTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=self.status_code, *args, **kwargs)

