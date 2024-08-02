from pydantic import Field
from responses.base import BasicConflictResponse, BasicNotFoundResponse, BasicForbiddenResponse

class SampleNotFoundResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="Samples not found")
    data: dict | None = Field(..., example={'sample_id': 5})

class SampleNotOwnerResponse(BasicForbiddenResponse):
    msg: str = Field(..., example="Sample owner differs from autorized user")
    data: dict | None = Field(..., example={'sample_id': 5, 'user_id': 1})

class ResearchWithIDNotFoundResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="Research with id not found")
    data: dict | None = Field(..., example={'research_id': 5})

class UserNotInResearchResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="User does not participate in research")
    data: dict | None = Field(..., example={'research_id': 5, 'user_id': 1})

class ResearchNotOngoingResponse(BasicConflictResponse):
    msg: str = Field(..., example="Research is not in \"ongoing\" status.")
    data: dict | None = Field(..., example={'research_id': 5})

class QRNotFoundResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="Qr not found")
    data: dict | None = Field(..., example={'qr_hex': '123ABC'})

class QRAlreadyUsedResponse(BasicConflictResponse):
    msg: str = Field(..., example="Qr already used")
    data: dict | None = Field(..., example={'qr_hex': '123ABC'})

class QRIsNotAssignedToKitResponse(BasicConflictResponse):
    msg: str = Field(..., example="Qr is not assigned to any kit")
    data: dict | None = Field(..., example={'qr_hex': '123ABC'})

class KitNotFoundResponse(BasicNotFoundResponse):
    msg: str = Field(..., example="Kit not found")
    data: dict | None = Field(..., example={'kit_identifier': 5})

class KitIsNotAssignedToUserResponse(BasicForbiddenResponse):
    msg: str = Field(..., example="Kit is not assigned to any user")
    data: dict | None = Field(..., example={'kit_identifier': 5, 'user_id': 1})

class UserDoesNotOwnKitResponse(BasicForbiddenResponse):
    msg: str = Field(..., example="User does not own kit")
    data: dict | None = Field(..., example={'kit_identifier': 5, 'user_id': 1})

class KitDoesNotActivatedResponse(BasicForbiddenResponse):
    msg: str = Field(..., example="Kit is not activated")
    data: dict | None = Field(..., example={'kit_identifier': 5})