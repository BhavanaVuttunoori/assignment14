from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Calculation Schemas
class CalculationBase(BaseModel):
    operation: str = Field(..., pattern="^(add|subtract|multiply|divide)$")
    operand1: float
    operand2: float


class CalculationCreate(CalculationBase):
    pass


class CalculationUpdate(BaseModel):
    operation: Optional[str] = Field(None, pattern="^(add|subtract|multiply|divide)$")
    operand1: Optional[float] = None
    operand2: Optional[float] = None


class CalculationResponse(CalculationBase):
    id: int
    result: float
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
