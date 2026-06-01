from pydantic import ValidationError

def custome_validation_error(field: str, message: str):
   return ValidationError.from_exception_data(
                title="Validation Error",
                line_errors=[
                    {
                        "type": "value_error",
                        "loc": (field,),
                        "msg": message,
                        "input": "",
                    }
                ])