from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool = True


class SuccessResponse(BaseResponse):
    pass

class UnsuccessResponse(BaseResponse):
    success: bool = False
    error: str