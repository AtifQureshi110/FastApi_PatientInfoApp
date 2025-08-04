from pydantic import BaseModel
from typing import List
from pydantic import EmailStr 
from pydantic import AnyUrl    
from pydantic import field_validator
from pydantic import computed_field, FieldSerializationInfo
from typing   import Annotated # this will add the description.
from pydantic import Field
from typing import Literal # this use to add the options in an attribute.
from typing import Optional


class Patient(BaseModel):
    id: Annotated[str,Field(..., description='ID ofthe patient', examples=['POO1']) ]
    name: str
    age: int
    weight: float
    married: bool
    allergies: List[str]  # or List[dict] if needed
    contact_details: str  # just a string
    email: EmailStr  
    linkedin_url: AnyUrl              # Required: must be a valid URL (e.g., LinkedIn profile link)
    height: float



    @field_validator('email', mode='before')
    @classmethod
    def email_validator(cls, value):
        valid_domains = ['hdfc.com', 'icici.com', 'gmail.com']
        domain_name = value.split('@')[-1]
        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        return value


    
    @field_validator('name', mode='before')
    @classmethod
    def transform_name_validator(cls, value):
        valid_domain = value.upper()
        return valid_domain

    from pydantic import field_validator

    @field_validator('age', mode='before')
    @classmethod
    def age_validator(cls, value):
        try:
            value = int(value)
        except:
            raise ValueError("Age must be a number.")
        
        if 0 <= value <= 100:
            return value
        else:
            raise ValueError("AGE SHOULD BE B/W 0 TO 100")

    # @field_validator('age', mode='before')
    # @classmethod
    # def age_validator(cls, value):
    #     try:
    #         value = int(value)
    #     except:
    #         raise ValueError("Age must be a number.")
        
    #     if 0<value<100:
    #         return value
    #     else:
    #         raise ValueError("AGE SHOULD BE B/W 0 TO 100")
        
    @computed_field(return_type=float)
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field(return_type=str)
    @property
    def verdict(self) -> str:
        bmi = round(self.weight / (self.height ** 2), 2)
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "Normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"   # ✅ You were missing this return statement
        



class PatientUpdate(BaseModel):
    # All fields are optional to allow partial updates
    name:   Annotated[Optional[str], Field(default=None)]  # Optional string field
    city:   Annotated[Optional[str], Field(default=None)]  # Optional string field
    age:    Annotated[Optional[int], Field(default=None, gt=0, lt=120)]  # Optional int with range validation
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]  # Must be one of the allowed literals
    height: Annotated[Optional[float], Field(default=None, gt=0)]  # Optional float > 0
    weight: Annotated[Optional[float], Field(default=None, gt=0)]  # Optional float > 0