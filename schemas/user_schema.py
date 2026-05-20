from pydantic_core import ValidationError, PydanticCustomError
from typing import Annotated
from pydantic import BaseModel, EmailStr, model_validator, Field, StringConstraints
from enum import Enum


class UserRole(Enum):
    admin = "Admin"
    manager = "Manager"
    user = "User"

NameType = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z]+$"
    )
]

def custome_validation_error(field: str, message: str):
   return ValidationError.from_exception_data(
                title="Validation Error",
                line_errors=[
                    {
                        "type": PydanticCustomError(
                            "custome-validation-error",
                            message
                        ),
                        "loc": (field,),
                        "input": "",
                    }
                ])

class CreateUser(BaseModel):
    f_name: NameType
    l_name: NameType
    email: EmailStr = Field(..., strict=True)
    password: str = Field(..., min_length=8, max_length=20)
    cpassword: str = Field(..., min_length=8,max_length=20)
    role: UserRole

    @model_validator(mode="after")
    def validate(cls,values):
        
        if values.cpassword != values.password:
            raise custome_validation_error("cpassword", "Password did not matched")
            


        values.email = values.email.lower()
        values.f_name = values.f_name.capitalize()
        values.l_name = values.l_name.capitalize()

        return values

class UpdateUser(BaseModel):
    f_name: NameType
    l_name: NameType
    email: EmailStr = Field(..., strict=True)
    role: UserRole

    @model_validator(mode="after")
    def validate(cls,values):  

        values.email = values.email.lower()
        values.f_name = values.f_name.capitalize()
        values.l_name = values.l_name.capitalize()

        return values
