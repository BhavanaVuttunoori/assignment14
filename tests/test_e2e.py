import pytest
from playwright.sync_api import Page, expect
import time

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720}
    }

# Helper function to register a test user
def register_user(page: Page, username: str, email: str, password: str):
    page.goto(BASE_URL)
    page.click("text=Register")
    page.fill("#register-username", username)
    page.fill("#register-email", email)
    page.fill("#register-password", password)
    page.click("#register-form button[type='submit']")
    time.sleep(1)

# Helper function to login
def login_user(page: Page, username: str, password: str):
    page.goto(BASE_URL)
    page.fill("#login-username", username)
    page.fill("#login-password", password)
    page.click("#login-form button[type='submit']")
    time.sleep(1)

# Helper function to logout
def logout_user(page: Page):
    page.click("text=Logout")
    time.sleep(1)


class TestAuthentication:
    """Test user authentication functionality"""
    
    def test_register_positive(self, page: Page):
        """Positive test: Successful user registration"""
        timestamp = int(time.time())
        username = f"testuser_{timestamp}"
        email = f"test_{timestamp}@example.com"
        password = "TestPass123"
        
        register_user(page, username, email, password)
        
        # Check for success message
        message = page.locator("#auth-message")
        expect(message).to_contain_text("Registration successful")
    
    def test_register_duplicate_username(self, page: Page):
        """Negative test: Register with duplicate username"""
        timestamp = int(time.time())
        username = f"duplicate_{timestamp}"
        email = f"test1_{timestamp}@example.com"
        password = "TestPass123"
        
        # Register first time
        register_user(page, username, email, password)
        time.sleep(1)
        
        # Try to register again with same username
        page.click("text=Register")
        page.fill("#register-username", username)
        page.fill("#register-email", f"test2_{timestamp}@example.com")
        page.fill("#register-password", password)
        page.click("#register-form button[type='submit']")
        time.sleep(1)
        
        # Check for error message
        message = page.locator("#auth-message")
        expect(message).to_contain_text("already registered")
    
    def test_register_invalid_email(self, page: Page):
        """Negative test: Register with invalid email format"""
        page.goto(BASE_URL)
        page.click("text=Register")
        page.fill("#register-username", "testuser")
        page.fill("#register-email", "invalid-email")
        page.fill("#register-password", "TestPass123")
        
        # HTML5 validation should prevent submission
        # The form should not be submitted
        is_invalid = page.locator("#register-email").evaluate("el => !el.validity.valid")
        assert is_invalid
    
    def test_login_positive(self, page: Page):
        """Positive test: Successful login"""
        timestamp = int(time.time())
        username = f"logintest_{timestamp}"
        email = f"login_{timestamp}@example.com"
        password = "TestPass123"
        
        # Register user first
        register_user(page, username, email, password)
        time.sleep(1)
        
        # Login
        login_user(page, username, password)
        
        # Check if calculations section is visible
        calc_section = page.locator("#calculations-section")
        expect(calc_section).not_to_have_class("hidden")
    
    def test_login_wrong_password(self, page: Page):
        """Negative test: Login with wrong password"""
        timestamp = int(time.time())
        username = f"wrongpass_{timestamp}"
        email = f"wrongpass_{timestamp}@example.com"
        password = "TestPass123"
        
        # Register user first
        register_user(page, username, email, password)
        time.sleep(1)
        
        # Try to login with wrong password
        login_user(page, username, "WrongPassword")
        
        # Check for error message
        message = page.locator("#auth-message")
        expect(message).to_contain_text("Incorrect username or password")


class TestCalculationsBREAD:
    """Test BREAD operations for calculations"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup: Create and login a user before each test"""
        timestamp = int(time.time())
        self.username = f"calctest_{timestamp}"
        self.email = f"calc_{timestamp}@example.com"
        self.password = "TestPass123"
        
        register_user(page, self.username, self.email, self.password)
        time.sleep(1)
        login_user(page, self.username, self.password)
        time.sleep(1)
    
    def test_add_calculation_positive(self, page: Page):
        """Positive test: Add (Create) a new calculation"""
        page.select_option("#operation", "add")
        page.fill("#operand1", "10")
        page.fill("#operand2", "5")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Check for success message with result
        message = page.locator("#calc-message")
        expect(message).to_contain_text("15")
        
        # Verify calculation appears in list
        calc_list = page.locator("#calculations-list")
        expect(calc_list).to_contain_text("10 + 5 = 15")
    
    def test_add_calculation_divide_by_zero(self, page: Page):
        """Negative test: Add calculation with division by zero"""
        page.select_option("#operation", "divide")
        page.fill("#operand1", "10")
        page.fill("#operand2", "0")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Check for error message
        message = page.locator("#calc-message")
        expect(message).to_contain_text("Cannot divide by zero")
    
    def test_browse_calculations(self, page: Page):
        """Browse: List all calculations"""
        # Add multiple calculations
        operations = [
            ("add", "10", "5"),
            ("subtract", "20", "8"),
            ("multiply", "3", "7")
        ]
        
        for op, op1, op2 in operations:
            page.select_option("#operation", op)
            page.fill("#operand1", op1)
            page.fill("#operand2", op2)
            page.click("#add-calculation-form button[type='submit']")
            time.sleep(1)
        
        # Refresh list
        page.click("text=Refresh List")
        time.sleep(1)
        
        # Verify all calculations are displayed
        calc_list = page.locator("#calculations-list")
        expect(calc_list).to_contain_text("10 + 5 = 15")
        expect(calc_list).to_contain_text("20 - 8 = 12")
        expect(calc_list).to_contain_text("3 × 7 = 21")
    
    def test_read_calculation_via_edit(self, page: Page):
        """Read: View a specific calculation (via edit modal)"""
        # Add a calculation
        page.select_option("#operation", "multiply")
        page.fill("#operand1", "6")
        page.fill("#operand2", "7")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Click edit to read the calculation
        page.click(".calculation-item .btn-warning")
        time.sleep(1)
        
        # Verify edit modal shows correct values
        expect(page.locator("#edit-operation")).to_have_value("multiply")
        expect(page.locator("#edit-operand1")).to_have_value("6")
        expect(page.locator("#edit-operand2")).to_have_value("7")
    
    def test_edit_calculation_positive(self, page: Page):
        """Edit: Update an existing calculation"""
        # Add a calculation
        page.select_option("#operation", "add")
        page.fill("#operand1", "10")
        page.fill("#operand2", "5")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Edit the calculation
        page.click(".calculation-item .btn-warning")
        time.sleep(1)
        
        page.select_option("#edit-operation", "multiply")
        page.fill("#edit-operand1", "8")
        page.fill("#edit-operand2", "3")
        page.click("#edit-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Verify updated calculation
        calc_list = page.locator("#calculations-list")
        expect(calc_list).to_contain_text("8 × 3 = 24")
        expect(calc_list).not_to_contain_text("10 + 5 = 15")
    
    def test_delete_calculation_positive(self, page: Page):
        """Delete: Remove a calculation"""
        # Add a calculation
        page.select_option("#operation", "subtract")
        page.fill("#operand1", "100")
        page.fill("#operand2", "25")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Verify it exists
        calc_list = page.locator("#calculations-list")
        expect(calc_list).to_contain_text("100 - 25 = 75")
        
        # Delete the calculation
        page.on("dialog", lambda dialog: dialog.accept())
        page.click(".calculation-item .btn-danger")
        time.sleep(1)
        
        # Verify it's deleted
        page.click("text=Refresh List")
        time.sleep(1)
        
        # Check if empty or doesn't contain the deleted calculation
        content = page.locator("#calculations-list").inner_text()
        assert "100 - 25 = 75" not in content
    
    def test_calculations_user_isolation(self, page: Page):
        """Test that users can only see their own calculations"""
        # Add a calculation as first user
        page.select_option("#operation", "add")
        page.fill("#operand1", "50")
        page.fill("#operand2", "50")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Logout
        logout_user(page)
        
        # Register and login as second user
        timestamp = int(time.time())
        username2 = f"calctest2_{timestamp}"
        email2 = f"calc2_{timestamp}@example.com"
        password2 = "TestPass123"
        
        register_user(page, username2, email2, password2)
        time.sleep(1)
        login_user(page, username2, password2)
        time.sleep(1)
        
        # Verify second user doesn't see first user's calculations
        calc_list = page.locator("#calculations-list")
        expect(calc_list).not_to_contain_text("50 + 50 = 100")


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup: Create and login a user before each test"""
        timestamp = int(time.time())
        self.username = f"edgetest_{timestamp}"
        self.email = f"edge_{timestamp}@example.com"
        self.password = "TestPass123"
        
        register_user(page, self.username, self.email, self.password)
        time.sleep(1)
        login_user(page, self.username, self.password)
        time.sleep(1)
    
    def test_calculation_with_decimals(self, page: Page):
        """Test calculations with decimal numbers"""
        page.select_option("#operation", "multiply")
        page.fill("#operand1", "3.14")
        page.fill("#operand2", "2.5")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Check calculation exists (result should be approximately 7.85)
        message = page.locator("#calc-message")
        expect(message).to_contain_text("7.85")
    
    def test_calculation_with_negative_numbers(self, page: Page):
        """Test calculations with negative numbers"""
        page.select_option("#operation", "add")
        page.fill("#operand1", "-10")
        page.fill("#operand2", "5")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Check for result -5
        calc_list = page.locator("#calculations-list")
        expect(calc_list).to_contain_text("-10 + 5 = -5")
    
    def test_calculation_with_large_numbers(self, page: Page):
        """Test calculations with large numbers"""
        page.select_option("#operation", "multiply")
        page.fill("#operand1", "999999")
        page.fill("#operand2", "888888")
        page.click("#add-calculation-form button[type='submit']")
        time.sleep(1)
        
        # Check that calculation was created
        message = page.locator("#calc-message")
        expect(message).to_contain_text("Calculation created")
