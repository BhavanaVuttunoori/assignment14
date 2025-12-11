from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, User, Calculation
from app.schemas import CalculationCreate, CalculationUpdate, CalculationResponse
from app.auth import get_current_user

router = APIRouter(prefix="/calculations", tags=["Calculations"])


def calculate_result(operation: str, operand1: float, operand2: float) -> float:
    """Perform calculation based on operation type"""
    if operation == "add":
        return operand1 + operand2
    elif operation == "subtract":
        return operand1 - operand2
    elif operation == "multiply":
        return operand1 * operand2
    elif operation == "divide":
        if operand2 == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot divide by zero"
            )
        return operand1 / operand2
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation. Must be one of: add, subtract, multiply, divide"
        )


# Add (Create) - POST /calculations
@router.post("/", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
def create_calculation(
    calculation: CalculationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new calculation"""
    # Calculate result
    result = calculate_result(
        calculation.operation,
        calculation.operand1,
        calculation.operand2
    )
    
    # Create calculation object
    db_calculation = Calculation(
        operation=calculation.operation,
        operand1=calculation.operand1,
        operand2=calculation.operand2,
        result=result,
        user_id=current_user.id
    )
    
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation


# Browse (List All) - GET /calculations
@router.get("/", response_model=List[CalculationResponse])
def get_calculations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve all calculations for the logged-in user"""
    calculations = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return calculations


# Read (Get One) - GET /calculations/{id}
@router.get("/{calculation_id}", response_model=CalculationResponse)
def get_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve a specific calculation by ID"""
    calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    return calculation


# Edit (Update) - PUT /calculations/{id}
@router.put("/{calculation_id}", response_model=CalculationResponse)
def update_calculation(
    calculation_id: int,
    calculation_update: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an existing calculation"""
    # Find the calculation
    db_calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    
    if not db_calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Update fields if provided
    update_data = calculation_update.dict(exclude_unset=True)
    
    if update_data:
        for field, value in update_data.items():
            setattr(db_calculation, field, value)
        
        # Recalculate result
        db_calculation.result = calculate_result(
            db_calculation.operation,
            db_calculation.operand1,
            db_calculation.operand2
        )
        
        db.commit()
        db.refresh(db_calculation)
    
    return db_calculation


# Edit (Partial Update) - PATCH /calculations/{id}
@router.patch("/{calculation_id}", response_model=CalculationResponse)
def patch_calculation(
    calculation_id: int,
    calculation_update: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Partially update an existing calculation"""
    return update_calculation(calculation_id, calculation_update, db, current_user)


# Delete - DELETE /calculations/{id}
@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calculation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a calculation by ID"""
    calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    db.delete(calculation)
    db.commit()
    return None
