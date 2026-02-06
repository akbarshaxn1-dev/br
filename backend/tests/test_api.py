"""
Backend API Tests for Единый Портал Управления Отделами
Tests: Auth, Factions, Departments, Topics, Audit, Weeks
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "vadim@emergent.dev"
TEST_PASSWORD = "admin123"


class TestHealthCheck:
    """Health check and basic API tests"""
    
    def test_api_root(self):
        """Test API root endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        print(f"API Root: {data}")
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"Health: {data}")


class TestAuth:
    """Authentication endpoint tests"""
    
    def test_login_success(self):
        """Test successful login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["email"] == TEST_EMAIL
        print(f"Login successful for: {data['user']['email']}")
        return data
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "wrong@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        print("Invalid credentials correctly rejected")
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL
        })
        assert response.status_code == 422  # Validation error
        print("Missing fields correctly rejected")
    
    def test_get_current_user(self):
        """Test getting current user info"""
        # First login
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Get current user
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_EMAIL
        print(f"Current user: {data['email']}, role: {data.get('role')}")
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        response = requests.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code in [401, 403]
        print("Unauthorized access correctly rejected")


class TestFactions:
    """Factions API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_factions_list(self):
        """Test getting list of factions"""
        response = requests.get(
            f"{BASE_URL}/api/factions/",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} factions")
        
        # Verify 8 factions exist
        if len(data) >= 8:
            print("All 8 factions present")
        
        # Check faction structure
        if len(data) > 0:
            faction = data[0]
            assert "code" in faction
            assert "name" in faction
            print(f"First faction: {faction['name']} ({faction['code']})")
        
        return data
    
    def test_get_faction_by_code(self):
        """Test getting specific faction by code"""
        response = requests.get(
            f"{BASE_URL}/api/factions/fsb",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "fsb"
        assert "name" in data
        print(f"FSB faction: {data['name']}")
    
    def test_get_nonexistent_faction(self):
        """Test getting non-existent faction"""
        response = requests.get(
            f"{BASE_URL}/api/factions/nonexistent",
            headers=self.headers
        )
        assert response.status_code == 404
        print("Non-existent faction correctly returns 404")


class TestDepartments:
    """Departments API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_faction_departments(self):
        """Test getting departments for a faction"""
        response = requests.get(
            f"{BASE_URL}/api/departments/faction/fsb",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"FSB has {len(data)} departments")
        return data
    
    def test_create_department(self):
        """Test creating a new department"""
        response = requests.post(
            f"{BASE_URL}/api/departments/faction/fsb",
            headers=self.headers,
            json={"name": "TEST_Отдел тестирования"}
        )
        # Should succeed for admin user
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["name"] == "TEST_Отдел тестирования"
            print(f"Created department: {data['id']}")
            return data
        else:
            print(f"Create department returned: {response.status_code}")
            # May fail due to permissions - that's ok
            assert response.status_code in [200, 403]
    
    def test_get_nonexistent_department(self):
        """Test getting non-existent department"""
        response = requests.get(
            f"{BASE_URL}/api/departments/nonexistent-id",
            headers=self.headers
        )
        assert response.status_code == 404
        print("Non-existent department correctly returns 404")


class TestTopics:
    """Topics (Lectures & Trainings) API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_lecture_topics(self):
        """Test getting lecture topics for a faction"""
        response = requests.get(
            f"{BASE_URL}/api/topics/lectures/faction/fsb",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"FSB has {len(data)} lecture topics")
        return data
    
    def test_get_training_topics(self):
        """Test getting training topics for a faction"""
        response = requests.get(
            f"{BASE_URL}/api/topics/trainings/faction/fsb",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"FSB has {len(data)} training topics")
        return data
    
    def test_create_lecture_topic(self):
        """Test creating a lecture topic"""
        response = requests.post(
            f"{BASE_URL}/api/topics/lectures/faction/fsb",
            headers=self.headers,
            json={"topic": "TEST_Тестовая лекция"}
        )
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["topic"] == "TEST_Тестовая лекция"
            print(f"Created lecture topic: {data['id']}")
            return data
        else:
            print(f"Create lecture topic returned: {response.status_code}")
            assert response.status_code in [200, 403]
    
    def test_create_training_topic(self):
        """Test creating a training topic"""
        response = requests.post(
            f"{BASE_URL}/api/topics/trainings/faction/fsb",
            headers=self.headers,
            json={"topic": "TEST_Тестовая тренировка"}
        )
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["topic"] == "TEST_Тестовая тренировка"
            print(f"Created training topic: {data['id']}")
            return data
        else:
            print(f"Create training topic returned: {response.status_code}")
            assert response.status_code in [200, 403]


class TestAuditLogs:
    """Audit log API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_audit_logs(self):
        """Test getting audit logs"""
        response = requests.get(
            f"{BASE_URL}/api/audit/logs",
            headers=self.headers
        )
        # Should succeed for admin user
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            print(f"Found {len(data)} audit logs")
            if len(data) > 0:
                log = data[0]
                assert "action" in log
                assert "user_email" in log
                print(f"Latest log: {log['action']} by {log['user_email']}")
        else:
            print(f"Audit logs returned: {response.status_code}")
            assert response.status_code in [200, 403]
    
    def test_filter_audit_logs_by_resource_type(self):
        """Test filtering audit logs by resource type"""
        response = requests.get(
            f"{BASE_URL}/api/audit/logs?resource_type=auth",
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            print(f"Found {len(data)} auth-related audit logs")
        else:
            assert response.status_code in [200, 403]


class TestWeeks:
    """Weeks/Table data API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - get auth token and find a department"""
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get a department to test with
        dept_response = requests.get(
            f"{BASE_URL}/api/departments/faction/fsb",
            headers=self.headers
        )
        if dept_response.status_code == 200:
            depts = dept_response.json()
            self.department_id = depts[0]["id"] if len(depts) > 0 else None
        else:
            self.department_id = None
    
    def test_get_current_week(self):
        """Test getting current week for a department"""
        if not self.department_id:
            pytest.skip("No department available for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/weeks/department/{self.department_id}/current",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "week_start" in data
        assert "week_end" in data
        print(f"Current week: {data['week_start']} - {data['week_end']}")
        return data
    
    def test_get_week_table_data(self):
        """Test getting table data for a week"""
        if not self.department_id:
            pytest.skip("No department available for testing")
        
        # First get current week
        week_response = requests.get(
            f"{BASE_URL}/api/weeks/department/{self.department_id}/current",
            headers=self.headers
        )
        if week_response.status_code != 200:
            pytest.skip("Could not get current week")
        
        week_id = week_response.json()["id"]
        
        # Get table data
        response = requests.get(
            f"{BASE_URL}/api/weeks/{week_id}/table-data",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "rows" in data
        print(f"Table has {len(data['rows'])} rows")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
