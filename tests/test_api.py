"""
API Tests for Calculations BREAD Operations
Tests authentication and all CRUD endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_register_user():
    """Test user registration"""
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert "id" in response.json()

def test_register_duplicate():
    """Test duplicate user registration fails"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    }
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400

def test_login():
    """Test user login"""
    # Register user
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    
    # Login
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_create_calculation():
    """Test creating a calculation (Add/Create)"""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = token_response.json()["access_token"]
    
    # Create calculation
    response = client.post("/calculations/", 
        json={
            "operand1": 10,
            "operand2": 5,
            "operation": "add"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["result"] == 15
    assert response.json()["operation"] == "add"

def test_browse_calculations():
    """Test listing calculations (Browse)"""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create calculations
    client.post("/calculations/", json={"operand1": 10, "operand2": 5, "operation": "add"}, headers=headers)
    client.post("/calculations/", json={"operand1": 20, "operand2": 4, "operation": "divide"}, headers=headers)
    
    # Browse calculations
    response = client.get("/calculations/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_read_calculation():
    """Test reading a single calculation (Read)"""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create calculation
    create_response = client.post("/calculations/", 
        json={"operand1": 10, "operand2": 5, "operation": "add"}, 
        headers=headers
    )
    calc_id = create_response.json()["id"]
    
    # Read calculation
    response = client.get(f"/calculations/{calc_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == calc_id
    assert response.json()["result"] == 15

def test_update_calculation():
    """Test updating a calculation (Edit with PUT)"""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create calculation
    create_response = client.post("/calculations/", 
        json={"operand1": 10, "operand2": 5, "operation": "add"}, 
        headers=headers
    )
    calc_id = create_response.json()["id"]
    
    # Update calculation
    response = client.put(f"/calculations/{calc_id}",
        json={"operand1": 20, "operand2": 3, "operation": "multiply"},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["result"] == 60
    assert response.json()["operation"] == "multiply"

def test_patch_calculation():
    """Test partially updating a calculation (Edit with PATCH)"""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create calculation
    create_response = client.post("/calculations/", 
        json={"operand1": 10, "operand2": 5, "operation": "add"}, 
        headers=headers
    )
    calc_id = create_response.json()["id"]
    
    # Patch calculation (only change operand2)
    response = client.patch(f"/calculations/{calc_id}",
        json={"operand2": 8},
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["result"] == 18
    assert response.json()["operand1"] == 10
    assert response.json()["operand2"] == 8

def test_delete_calculation():
    """Test deleting a calculation (Delete)"""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = token_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create calculation
    create_response = client.post("/calculations/", 
        json={"operand1": 10, "operand2": 5, "operation": "add"}, 
        headers=headers
    )
    calc_id = create_response.json()["id"]
    
    # Delete calculation
    response = client.delete(f"/calculations/{calc_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/calculations/{calc_id}", headers=headers)
    assert get_response.status_code == 404

def test_divide_by_zero():
    """Test divide by zero error handling"""
    # Register and login
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPass123"
    })
    token_response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = token_response.json()["access_token"]
    
    # Try to create calculation with division by zero
    response = client.post("/calculations/", 
        json={"operand1": 10, "operand2": 0, "operation": "divide"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_user_isolation():
    """Test that users can only see their own calculations"""
    # Create first user
    client.post("/auth/register", json={
        "username": "user1",
        "email": "user1@example.com",
        "password": "Pass123"
    })
    token1 = client.post("/auth/token", data={
        "username": "user1",
        "password": "Pass123"
    }).json()["access_token"]
    
    # Create second user
    client.post("/auth/register", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "Pass123"
    })
    token2 = client.post("/auth/token", data={
        "username": "user2",
        "password": "Pass123"
    }).json()["access_token"]
    
    # User1 creates calculation
    calc_response = client.post("/calculations/", 
        json={"operand1": 10, "operand2": 5, "operation": "add"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    calc_id = calc_response.json()["id"]
    
    # User2 tries to access user1's calculation
    response = client.get(f"/calculations/{calc_id}", 
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404
    
    # User2 can only see empty list
    list_response = client.get("/calculations/", 
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert len(list_response.json()) == 0
