"""
Complete Authentication Testing Script

Tests all authentication endpoints:
1. POST /auth/register - Register new user
2. POST /auth/login - Login with credentials
3. GET /auth/me - Get current user info (authenticated)
4. POST /auth/refresh - Refresh access token
5. POST /auth/change-password - Change password (authenticated)

Usage:
    python examples/test_auth_complete.py
"""
import sys
import io
import requests
import json
from datetime import datetime

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
AUTH_ENDPOINT = f"{API_BASE_URL}/auth"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(success, message, data=None):
    """Print test result"""
    status = "PASS" if success else "FAIL"
    symbol = "✓" if success else "✗"
    print(f"\n{symbol} [{status}] {message}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)}")


def test_register():
    """Test 1: Register new user"""
    print_section("TEST 1: Register New User")

    # Generate unique username with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {
        "email": f"testuser_{timestamp}@example.com",
        "username": f"testuser_{timestamp}",
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "student_id": f"student_{timestamp}"
    }

    print(f"Registering user: {user_data['email']}")

    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/register",
            json=user_data,
            timeout=10
        )

        if response.status_code == 201:
            data = response.json()
            if data["success"]:
                user_info = data["data"]["user"]
                tokens = data["data"]["tokens"]
                print_result(True, "User registered successfully", {
                    "user_id": user_info["id"],
                    "email": user_info["email"],
                    "username": user_info["username"],
                    "has_access_token": bool(tokens["access_token"]),
                    "has_refresh_token": bool(tokens["refresh_token"]),
                })
                return {
                    "user": user_info,
                    "tokens": tokens,
                    "credentials": user_data
                }
            else:
                print_result(False, f"Registration failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print_result(False, "Cannot connect to API server. Is it running? (python scripts/run_api.py)")
        return None
    except Exception as e:
        print_result(False, f"Registration error: {str(e)}")
        return None


def test_login(credentials):
    """Test 2: Login with credentials"""
    print_section("TEST 2: Login with Email/Password")

    login_data = {
        "email": credentials["email"],
        "password": credentials["password"]
    }

    print(f"Logging in as: {login_data['email']}")

    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/login",
            json=login_data,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                user_info = data["data"]["user"]
                tokens = data["data"]["tokens"]
                print_result(True, "Login successful", {
                    "user_id": user_info["id"],
                    "email": user_info["email"],
                    "login_count": user_info.get("login_count", "N/A"),
                    "has_access_token": bool(tokens["access_token"]),
                })
                return tokens
            else:
                print_result(False, f"Login failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print_result(False, f"Login error: {str(e)}")
        return None


def test_get_me(access_token):
    """Test 3: Get current user info"""
    print_section("TEST 3: Get Current User Info (Authenticated)")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    print("Fetching current user info with access token...")

    try:
        response = requests.get(
            f"{AUTH_ENDPOINT}/me",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                user_info = data["data"]
                print_result(True, "User info retrieved successfully", {
                    "user_id": user_info["id"],
                    "email": user_info["email"],
                    "username": user_info["username"],
                    "roles": user_info["roles"],
                    "is_active": user_info["is_active"],
                })
                return True
            else:
                print_result(False, f"Failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def test_refresh_token(refresh_token):
    """Test 4: Refresh access token"""
    print_section("TEST 4: Refresh Access Token")

    refresh_data = {
        "refresh_token": refresh_token
    }

    print("Refreshing access token...")

    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/refresh",
            json=refresh_data,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                new_tokens = data["data"]
                print_result(True, "Access token refreshed successfully", {
                    "new_access_token_length": len(new_tokens["access_token"]),
                    "token_type": new_tokens["token_type"],
                    "expires_in": new_tokens.get("expires_in", "N/A"),
                })
                return new_tokens["access_token"]
            else:
                print_result(False, f"Refresh failed: {data.get('error', 'Unknown error')}")
                return None
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return None

    except Exception as e:
        print_result(False, f"Refresh error: {str(e)}")
        return None


def test_change_password(access_token, old_password):
    """Test 5: Change password"""
    print_section("TEST 5: Change Password (Authenticated)")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    password_data = {
        "current_password": old_password,
        "new_password": "NewSecurePassword456!"
    }

    print("Changing password...")

    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/change-password",
            headers=headers,
            json=password_data,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print_result(True, "Password changed successfully", {
                    "message": data["data"]["message"]
                })
                return True
            else:
                print_result(False, f"Password change failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print_result(False, f"Password change error: {str(e)}")
        return False


def test_login_with_new_password(email, new_password):
    """Test 6: Verify login with new password"""
    print_section("TEST 6: Login with New Password (Verification)")

    login_data = {
        "email": email,
        "password": new_password
    }

    print(f"Verifying login with new password for: {email}")

    try:
        response = requests.post(
            f"{AUTH_ENDPOINT}/login",
            json=login_data,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print_result(True, "Login with new password successful")
                return True
            else:
                print_result(False, f"Login failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False

    except Exception as e:
        print_result(False, f"Login error: {str(e)}")
        return False


def main():
    """Run all authentication tests"""
    print("\n" + "=" * 80)
    print("  AI-Native MVP - Complete Authentication Testing")
    print("=" * 80)
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    results = {
        "total": 6,
        "passed": 0,
        "failed": 0
    }

    # Test 1: Register
    register_result = test_register()
    if register_result:
        results["passed"] += 1

        # Test 2: Login
        tokens = test_login(register_result["credentials"])
        if tokens:
            results["passed"] += 1

            # Test 3: Get Me
            if test_get_me(tokens["access_token"]):
                results["passed"] += 1
            else:
                results["failed"] += 1

            # Test 4: Refresh Token
            new_access_token = test_refresh_token(tokens["refresh_token"])
            if new_access_token:
                results["passed"] += 1
            else:
                results["failed"] += 1

            # Test 5: Change Password
            if test_change_password(tokens["access_token"], register_result["credentials"]["password"]):
                results["passed"] += 1

                # Test 6: Login with new password
                if test_login_with_new_password(register_result["credentials"]["email"], "NewSecurePassword456!"):
                    results["passed"] += 1
                else:
                    results["failed"] += 1
            else:
                results["failed"] += 2  # Both test 5 and 6 failed
        else:
            results["failed"] += 5  # Tests 2-6 failed
    else:
        results["failed"] += 6  # All tests failed

    # Summary
    print_section("TEST SUMMARY")
    print(f"\nTotal Tests: {results['total']}")
    print(f"Passed: {results['passed']} / {results['total']}")
    print(f"Failed: {results['failed']} / {results['total']}")

    success_rate = (results['passed'] / results['total']) * 100
    print(f"Success Rate: {success_rate:.1f}%")

    if results['passed'] == results['total']:
        print("\n✓ ALL TESTS PASSED - JWT Authentication is working correctly!")
        print("\nYou can now:")
        print("1. Access Swagger UI: http://localhost:8000/docs")
        print("2. Test endpoints in /auth section")
        print("3. Register users, login, and use authenticated endpoints")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Review errors above")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
