from typing import List, Dict
from fastapi.responses import JSONResponse
from schemas.resp_schema import Error

FIELD_NAMES = {
    "f_name": "First Name",
    "l_name": "Last Name",
    "name": "Name",
    "email": "Email",
    "password": "Password",
    "role": "Role",
    "cpassword": "Confirm Password",
    "new_password": "New Password",
    "confirm_password": "Confirm Password"
}

def SuccessResp(message: str = None, data=None):
    return JSONResponse(
        status_code=200,
        content={
            "status": True,
            "message": message,
            "data":data
        }
    )

def ErrorResp(message: str = None, data=None):
    return JSONResponse(
        status_code=422,
        content={
            "status": False,
            "message": message,
            "data":data
        }
    )

def FieldErrorResp(errors: Dict[str, str]=[],field: str=None, message: str=None, jsnorsp=True, data=None):
    errs = errors

    if field != None and message != None:
        errs = {
            field:message
        }

    rspDct = {
                "status": False,
                "errors": errs,
            }
    
    if data is not None:
        rspDct["data"] = data

    if jsnorsp ==True:
        return JSONResponse(
            status_code=422,
            content=rspDct
        )
    else:
        return rspDct

async def validation_exception_handler(exc):
    formatted_errors = {}
    print(exc.errors())
    for error in exc.errors():

        field = error["loc"][-1]

        field_name = FIELD_NAMES.get(field, field)

        error_type = error["type"]

        message = error["msg"]


        # =========================
        # Custom Friendly Messages
        # =========================

        if error_type == "string_too_short":

            min_length = error["ctx"]["min_length"]

            message = (
                f"{field_name} should have at least "
                f"{min_length} characters"
            )


        elif error_type == "string_too_long":

            max_length = error["ctx"]["max_length"]

            message = (
                f"{field_name} should not exceed "
                f"{max_length} characters"
            )

        elif error_type == "missing":

            message = f"{field_name} is required"

        elif error_type == "enum":

            expected_values = error["ctx"]["expected"]

            cleaned_values = (
                expected_values
                .replace("'", "")
            )

            message = f"{field_name} must be {cleaned_values}"

        elif error_type == "json_invalid":
            message = "Invalid JSON format in request body"
            field = "body"

        elif error_type == "value_error":

            message = f"Invalid value for {field_name}"

        elif error_type == "string_pattern_mismatch":

            message = message = message.replace("String", field_name)

        formatted_errors[field] = message

    return FieldErrorResp(errors=formatted_errors)