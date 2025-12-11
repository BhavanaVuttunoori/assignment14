# Web API - Module 14 Assignment

The Assignment 14 deliverable is a fully tested FastAPI user authentication and calculation service with BREAD operations, packaged for local development, Docker usage, and CI/CD. This README documents how the project is structured, what was implemented, and how to reproduce the results.

## Project Highlights

Built with FastAPI and SQLAlchemy to expose user registration/login and calculation operations through REST endpoints with database persistence. Secure user authentication with JWT tokens, bcrypt password hashing, and comprehensive validation. BREAD pattern implementation (Browse, Read, Edit, Add, Delete) for calculation management. Robust Pydantic validation in app/schemas.py with explicit error handling (division by zero, email format, password strength). Comprehensive automated E2E test suite with Playwright covering user and calculation scenarios (15+ tests). SQLAlchemy ORM models with proper relationships between Users and Calculations tables. Continuous Integration via GitHub Actions to test with PostgreSQL, build Docker images, and deploy to Docker Hub. Containerized delivery: public Docker image available at bhavanavuttunoori/calculations-api.

## Getting Started

### 1. Setup Environment
```bash
cd WEBAPI_ASS14
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Run the Application Locally
```bash
uvicorn app.main:app --reload
```
Navigate to http://localhost:8000 for the web interface or http://localhost:8000/docs for the Swagger UI.

## Docker Usage

### Build Locally (optional)
```bash
docker build -t calculations-api .
docker run -p 8000:8000 -e DATABASE_URL=postgresql://postgres:postgres@localhost:5432/calculations_db calculations-api
```

### Pull Prebuilt Image
```bash
docker pull bhavanavuttunoori/calculations-api:latest
docker run -p 8000:8000 -e DATABASE_URL=postgresql://postgres:postgres@localhost:5432/calculations_db bhavanavuttunoori/calculations-api:latest
```

### Using Docker Compose
```bash
docker-compose up -d
```
The application will be available at http://localhost:8000 with PostgreSQL database.

## Testing Strategy

**E2E Tests (tests/test_e2e.py)**: verify user registration, login, validation rules, and complete BREAD operations through browser automation with Playwright.

**Test Categories**:
- Authentication: Registration, login, duplicate handling, invalid credentials
- BREAD Operations: Browse, Read, Edit, Add, Delete calculations
- Edge Cases: Decimal numbers, negative numbers, large numbers, division by zero
- Security: User isolation, unauthorized access prevention

Run the full suite:
```bash
pytest tests/test_e2e.py -v
```

Run with Playwright headed mode (see browser):
```bash
pytest tests/test_e2e.py --headed
```

## Project Structure

```
WEBAPI_ASS14/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application with all endpoints
│   ├── database.py          # Database configuration and ORM models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── auth.py              # JWT authentication and password hashing
│   └── routes/
│       ├── __init__.py
│       ├── auth_routes.py   # User registration and login endpoints
│       └── calculation_routes.py  # Calculation BREAD endpoints
├── static/
│   ├── index.html           # Web interface
│   ├── styles.css           # Responsive styling
│   └── app.js               # Client-side JavaScript
├── tests/
│   ├── __init__.py
│   └── test_e2e.py          # Playwright E2E tests
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions CI/CD pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── setup.bat / setup.sh     # Quick setup scripts
├── .env
├── .gitignore
└── README.md
```

## API Endpoints

### User Operations

**Create User (Register)**:
```http
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Login**:
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=securepassword123
```

**Get Current User**:
```http
GET /auth/me
Authorization: Bearer <token>
```

### Calculation Operations (BREAD)

**Browse Calculations**:
```http
GET /calculations/
Authorization: Bearer <token>
```

**Read Calculation**:
```http
GET /calculations/{calculation_id}
Authorization: Bearer <token>
```

**Edit Calculation**:
```http
PUT /calculations/{calculation_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "operation": "multiply",
  "operand1": 20,
  "operand2": 5
}
```

Or partial update with PATCH:
```http
PATCH /calculations/{calculation_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "operand1": 20
}
```

**Add Calculation**:
```http
POST /calculations/
Authorization: Bearer <token>
Content-Type: application/json

{
  "operation": "add",
  "operand1": 10.5,
  "operand2": 5.2
}
```

**Delete Calculation**:
```http
DELETE /calculations/{calculation_id}
Authorization: Bearer <token>
```

## BREAD Pattern Implementation

The BREAD pattern in app/routes/calculation_routes.py provides comprehensive calculation management:

- **Browse**: List all calculations with user-specific filtering (only see your own)
- **Read**: Retrieve specific calculation by ID with authorization check
- **Edit**: Update calculation operation or operands with automatic result recalculation (PUT/PATCH)
- **Add**: Create new calculation with validation and automatic result computation
- **Delete**: Remove calculation from database with ownership verification

**Supported operations**: Add, Subtract, Multiply, Divide with division by zero protection.

Example usage:
```bash
# Browse calculations
GET /calculations/
Authorization: Bearer <token>

# Add new calculation
POST /calculations/
Authorization: Bearer <token>
{"operation": "add", "operand1": 10, "operand2": 5}  # Returns 15

# Edit calculation
PUT /calculations/1
Authorization: Bearer <token>
{"operation": "multiply", "operand1": 10, "operand2": 5}  # Recalculates to 50

# Delete calculation
DELETE /calculations/1
Authorization: Bearer <token>
```

## Database Schema

**Users Table**:
- id (Integer, Primary Key)
- username (String, Unique, Indexed)
- email (String, Unique, Indexed)
- hashed_password (String)
- created_at (DateTime)

**Calculations Table**:
- id (Integer, Primary Key)
- operation (String: add, subtract, multiply, divide)
- operand1 (Float)
- operand2 (Float)
- result (Float)
- created_at (DateTime)
- updated_at (DateTime)
- user_id (Integer, Foreign Key to users.id)

**Relationship**: One User can have many Calculations (one-to-many with cascade delete).

## Continuous Integration

The repository includes a GitHub Actions workflow (.github/workflows/ci-cd.yml) that runs on every push:

**Test Job**:
- Set up Python 3.11
- Start PostgreSQL 15 service container
- Install dependencies with caching
- Install Playwright browsers
- Start FastAPI application
- Run E2E tests (test_e2e.py)
- Generate and upload test results

**Build and Push Job (main branch only)**:
- Build Docker image
- Tag with latest and commit SHA
- Push to Docker Hub (bhavanavuttunoori/calculations-api)

**Required GitHub Secrets**:
- DOCKER_USERNAME: Your Docker Hub username
- DOCKER_PASSWORD: Your Docker Hub access token

## Assignment Instructions & Deliverables

**Objective**: Implement and test user authentication with calculation BREAD operations, comprehensive E2E testing, and CI/CD pipeline.

### Implementation Checklist
- ✅ SQLAlchemy models for User and Calculation with proper relationships
- ✅ Pydantic schemas with validation (division by zero, email format, password strength)
- ✅ User registration endpoint with duplicate detection and password hashing
- ✅ User login endpoint with JWT token generation
- ✅ Calculation BREAD endpoints (Browse, Read, Edit, Add, Delete)
- ✅ 15+ comprehensive Playwright E2E tests
- ✅ FastAPI application with full CRUD operations
- ✅ GitHub Actions workflow with PostgreSQL integration
- ✅ Docker containerization with docker-compose support
- ✅ Responsive web interface with client-side validation
- ✅ Comprehensive documentation

### Submission Package
- **GitHub repository**: https://github.com/BhavanaVuttunoori/assignment14
- **Docker Hub image**: https://hub.docker.com/r/bhavanavuttunoori/calculations-api
- **Screenshots demonstrating**:
  - Successful GitHub Actions workflow
  - Docker Hub deployment
  - Web interface (registration, login, BREAD operations)
  - API documentation (Swagger UI)
  - Test execution results

## Grading Guidelines

**Criterion: BREAD Endpoints (25 Points)**
- Browse endpoint with user filtering
- Read endpoint for specific calculation
- Edit endpoint with automatic recalculation (PUT/PATCH)
- Add endpoint with validation and calculation
- Delete endpoint with authorization
- Proper error handling (division by zero, not found, unauthorized)

**Criterion: Authentication (25 Points)**
- Registration endpoint with validation and password hashing
- Login endpoint with JWT token generation
- User isolation (users only see their own calculations)
- Proper error handling (duplicate users, invalid credentials)

**Criterion: Testing (25 Points)**
- 15+ E2E tests with Playwright
- User registration and login tests
- Calculation BREAD operation tests
- Error scenario tests (negative testing)
- Edge case tests (decimals, negatives, large numbers)

**Criterion: CI/CD Pipeline (15 Points)**
- GitHub Actions workflow configuration
- PostgreSQL service container integration
- Docker build and push automation
- Automated test execution

**Criterion: Documentation (10 Points)**
- Comprehensive README with setup instructions
- API documentation via Swagger
- Code comments and docstrings
- Web interface with user-friendly design

## Helpful Commands

| Task | Command |
|------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Run application | `uvicorn app.main:app --reload` |
| Run E2E tests | `pytest tests/test_e2e.py -v` |
| Run tests headed mode | `pytest tests/test_e2e.py --headed` |
| Install Playwright | `playwright install chromium` |
| Build Docker image | `docker build -t calculations-api .` |
| Run with Docker Compose | `docker-compose up -d` |
| Stop Docker Compose | `docker-compose down` |
| View container logs | `docker logs -f webapi_ass14_web_1` |
| Quick setup (Windows) | `.\setup.bat` |
| Quick setup (Linux/Mac) | `./setup.sh` |

## Submission Tips

- Commit frequently with meaningful messages describing each feature
- Keep .env or secrets out of version control (use .gitignore)
- Verify all tests pass locally before pushing
- Ensure GitHub Actions workflow completes successfully
- Capture required screenshots showing green checkmarks in Actions tab
- Verify Docker image is publicly accessible on Docker Hub
- Update README with your actual GitHub and Docker Hub usernames
- Test the application end-to-end before submission

## Learning Outcomes

**CLO3: Create Python applications with automated testing**
- Comprehensive E2E tests with Playwright for browser automation
- Test fixtures and database isolation
- 15+ tests with comprehensive coverage of positive, negative, and edge cases

**CLO4: Set up GitHub Actions for CI**
- Automated testing on push and pull requests
- PostgreSQL service containers
- Automated Docker builds and deployment
- Test result uploads

**CLO9: Apply containerization techniques**
- Optimized Dockerfile for production
- Docker Compose for local development
- Environment variable management
- Service orchestration with health checks

**CLO10: Create, consume, and test REST APIs**
- RESTful endpoint design (BREAD pattern)
- Proper HTTP methods and status codes
- API documentation with OpenAPI/Swagger
- Request/response validation

**CLO11: Integrate with SQL databases**
- SQLAlchemy ORM models with relationships
- Foreign key constraints and cascade operations
- Database session management
- PostgreSQL in production

**CLO12: Serialize/deserialize JSON with Pydantic**
- Input validation schemas with custom validators
- Output serialization with from_attributes
- Type safety with Python type hints
- Email validation and password strength checks

**CLO13: Implement secure authentication**
- JWT token-based authentication
- Password hashing with bcrypt
- Secure password storage
- User authorization and data isolation

## Author

**Bhavana Vuttunoori**

- GitHub: https://github.com/BhavanaVuttunoori
- Repository: https://github.com/BhavanaVuttunoori/assignment14
- Docker Hub: https://hub.docker.com/r/bhavanavuttunoori/calculations-api

## Acknowledgments

FastAPI documentation and community examples. SQLAlchemy ORM patterns and best practices. Pydantic validation framework. Playwright testing framework. GitHub Actions workflow templates. Course instructors for project guidance.

## Support

For questions or issues:
- Check the GitHub Issues: https://github.com/BhavanaVuttunoori/assignment14/issues
- Review the API documentation at http://localhost:8000/docs
- Review setup scripts (setup.bat / setup.sh)
- Contact the repository maintainer

## License

This project is created for educational purposes as part of Module 14 assignment for demonstrating user authentication, calculation BREAD operations, comprehensive E2E testing, and CI/CD pipelines.

---

**Note**: This project was created as part of Module 14 assignment for demonstrating BREAD functionality with user authentication, JWT tokens, comprehensive Playwright E2E testing, and CI/CD pipelines with Docker deployment.
