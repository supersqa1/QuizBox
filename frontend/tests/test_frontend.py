import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

FRONTEND_URL = "http://localhost:5151"  # Frontend port
BACKEND_URL = "http://localhost:5050"   # Backend port

@pytest.fixture(scope="module")
def driver():
    # Initialize Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, 10)

def test_setup_page(driver, wait):
    """Test the setup page functionality"""
    driver.get(f"{FRONTEND_URL}/setup")
    
    # Check if we're on setup page
    assert "QuizBox Setup" in driver.title
    
    # Test form elements exist
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    assert email_input.is_displayed()
    assert password_input.is_displayed()
    assert submit_button.is_displayed()

def test_login_page(driver, wait):
    """Test the login page functionality"""
    driver.get(f"{FRONTEND_URL}/login")
    
    # Check if we're on login page
    assert "Login" in driver.title
    
    # Test form elements exist
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    assert email_input.is_displayed()
    assert password_input.is_displayed()
    assert submit_button.is_displayed()

def test_dashboard_redirect_when_not_logged_in(driver):
    """Test that accessing dashboard when not logged in redirects to login"""
    driver.get(f"{FRONTEND_URL}/dashboard")
    
    # Should be redirected to login
    assert "/login" in driver.current_url

def test_successful_login(driver, wait):
    """Test successful login flow"""
    driver.get(f"{FRONTEND_URL}/login")
    
    # Fill in login form
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    email_input.send_keys("admin@example.com")
    password_input.send_keys("admin123")
    submit_button.click()
    
    # Wait for redirect to dashboard
    try:
        wait.until(EC.url_contains("/dashboard"))
        assert "/dashboard" in driver.current_url
    except TimeoutException:
        pytest.fail("Login failed - not redirected to dashboard")

def test_login_invalid_credentials(driver, wait):
    """Test login with invalid credentials"""
    driver.get(f"{FRONTEND_URL}/login")
    
    # Fill in login form with invalid credentials
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    email_input.send_keys("wrong@example.com")
    password_input.send_keys("wrongpass")
    submit_button.click()
    
    # Wait for error message
    error_message = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "alert-danger")))
    assert "Invalid credentials" in error_message.text
    assert "/login" in driver.current_url

def test_register_page(driver, wait):
    """Test registration page functionality"""
    driver.get(f"{FRONTEND_URL}/register")
    
    # Test form elements exist
    name_input = wait.until(EC.presence_of_element_located((By.ID, "name")))
    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    assert name_input.is_displayed()
    assert email_input.is_displayed()
    assert password_input.is_displayed()
    assert submit_button.is_displayed()

def test_successful_registration(driver, wait):
    """Test successful registration flow"""
    driver.get(f"{FRONTEND_URL}/register")
    
    # Fill in registration form
    name_input = wait.until(EC.presence_of_element_located((By.ID, "name")))
    email_input = driver.find_element(By.ID, "email")
    password_input = driver.find_element(By.ID, "password")
    submit_button = driver.find_element(By.ID, "submit")
    
    name_input.send_keys("Test User")
    email_input.send_keys("test@example.com")
    password_input.send_keys("password123")
    submit_button.click()
    
    # Should redirect to login after successful registration
    wait.until(EC.url_contains("/login"))
    assert "/login" in driver.current_url

@pytest.fixture
def logged_in_driver(driver, test_user):
    """Setup driver with logged in user"""
    driver.get('http://localhost:5151/login')
    email_field = driver.find_element(By.NAME, 'email')
    password_field = driver.find_element(By.NAME, 'password')
    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    
    email_field.send_keys(test_user['email'])
    password_field.send_keys(test_user['password'])
    submit_button.click()
    
    WebDriverWait(driver, 10).until(
        EC.url_to_be('http://localhost:5000/dashboard')
    )
    return driver

def test_create_quiz(logged_in_driver):
    """Test quiz creation functionality"""
    driver = logged_in_driver
    driver.get('http://localhost:5000/quiz/new')
    
    # Fill quiz form
    question_field = driver.find_element(By.NAME, 'question_text')
    answer_field = driver.find_element(By.NAME, 'answer_text')
    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    
    question_field.send_keys('Test Question')
    answer_field.send_keys('Test Answer')
    submit_button.click()
    
    # Wait for redirect to dashboard
    WebDriverWait(driver, 10).until(
        EC.url_to_be('http://localhost:5000/dashboard')
    )
    assert driver.current_url == 'http://localhost:5000/dashboard'

def test_create_quiz_validation(logged_in_driver):
    """Test quiz creation validation"""
    driver = logged_in_driver
    driver.get('http://localhost:5000/quiz/new')
    
    # Submit empty form
    submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    submit_button.click()
    
    # Wait for error messages
    error_messages = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'invalid-feedback'))
    )
    assert len(error_messages) > 0
    assert any('required' in msg.text.lower() for msg in error_messages)

def test_view_themes(logged_in_driver, test_theme):
    """Test viewing themes"""
    driver = logged_in_driver
    driver.get('http://localhost:5000/themes')
    
    # Check if theme is displayed
    theme_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'theme-item'))
    )
    assert test_theme['name'] in theme_element.text
    assert test_theme['description'] in theme_element.text

def test_view_api_key(logged_in_driver):
    """Test viewing API key"""
    driver = logged_in_driver
    driver.get('http://localhost:5000/me/api-key')
    
    # Check if API key is displayed
    api_key_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'api-key'))
    )
    assert api_key_element.text.strip() != ''

def test_logout(logged_in_driver):
    """Test logout functionality"""
    driver = logged_in_driver
    
    # Click logout button/link
    logout_link = driver.find_element(By.ID, 'logout-link')
    logout_link.click()
    
    # Wait for redirect to login
    WebDriverWait(driver, 10).until(
        EC.url_to_be('http://localhost:5000/login')
    )
    assert driver.current_url == 'http://localhost:5000/login'
    
    # Verify can't access protected page
    driver.get('http://localhost:5000/dashboard')
    WebDriverWait(driver, 10).until(
        EC.url_to_be('http://localhost:5000/login')
    )
    assert driver.current_url == 'http://localhost:5000/login' 