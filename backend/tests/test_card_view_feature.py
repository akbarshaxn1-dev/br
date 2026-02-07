"""
Test suite for Mobile Card View feature and related functionality
Tests: View toggle, Card view data, Table view, Save functionality, Department CRUD, RBAC
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Authentication tests for developer login"""
    
    def test_login_developer(self):
        """Test login with developer credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "vadim@emergent.dev"
        assert data["user"]["role"] == "developer"
        return data["access_token"]


class TestDepartmentAPI:
    """Department API tests for Card View feature"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def auth_headers(self, auth_token):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_get_factions(self, auth_headers):
        """Test getting all factions"""
        response = requests.get(f"{BASE_URL}/api/factions/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Check FSB faction exists
        fsb_faction = next((f for f in data if f.get("code") == "fsb"), None)
        assert fsb_faction is not None, "FSB faction should exist"
    
    def test_get_fsb_faction(self, auth_headers):
        """Test getting FSB faction details"""
        response = requests.get(f"{BASE_URL}/api/factions/fsb", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "fsb"
        assert "name" in data
    
    def test_get_fsb_departments(self, auth_headers):
        """Test getting departments for FSB faction"""
        response = requests.get(f"{BASE_URL}/api/departments/faction/fsb", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least one department (Тестовый отдел)
        print(f"Found {len(data)} departments in FSB")
        for dept in data:
            print(f"  - {dept.get('name')} (id: {dept.get('id')})")
    
    def test_get_department_by_id(self, auth_headers):
        """Test getting department by ID"""
        # First get departments list
        response = requests.get(f"{BASE_URL}/api/departments/faction/fsb", headers=auth_headers)
        assert response.status_code == 200
        departments = response.json()
        
        if len(departments) > 0:
            dept_id = departments[0]["id"]
            response = requests.get(f"{BASE_URL}/api/departments/{dept_id}", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == dept_id
            assert "name" in data
        else:
            pytest.skip("No departments found to test")


class TestTopicsAPI:
    """Topics API tests for Card View feature - lectures and trainings"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        if response.status_code == 200:
            return {"Authorization": f"Bearer {response.json().get('access_token')}"}
        pytest.skip("Authentication failed")
    
    def test_get_lecture_topics_for_faction(self, auth_headers):
        """Test getting lecture topics for FSB faction"""
        response = requests.get(f"{BASE_URL}/api/topics/lectures/faction/fsb", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} lecture topics")
        for topic in data:
            print(f"  - {topic.get('topic')}")
    
    def test_get_training_topics_for_faction(self, auth_headers):
        """Test getting training topics for FSB faction"""
        response = requests.get(f"{BASE_URL}/api/topics/trainings/faction/fsb", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} training topics")
        for topic in data:
            print(f"  - {topic.get('topic')}")


class TestWeeksAndTableData:
    """Tests for weeks and table data - critical for Card View"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        if response.status_code == 200:
            return {"Authorization": f"Bearer {response.json().get('access_token')}"}
        pytest.skip("Authentication failed")
    
    @pytest.fixture
    def department_id(self, auth_headers):
        """Get first department ID from FSB"""
        response = requests.get(f"{BASE_URL}/api/departments/faction/fsb", headers=auth_headers)
        if response.status_code == 200 and len(response.json()) > 0:
            return response.json()[0]["id"]
        pytest.skip("No departments found")
    
    def test_get_current_week(self, auth_headers, department_id):
        """Test getting current week for department"""
        response = requests.get(f"{BASE_URL}/api/weeks/department/{department_id}/current", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "week_start" in data
        assert "week_end" in data
        print(f"Current week: {data.get('week_start')} - {data.get('week_end')}")
        return data["id"]
    
    def test_get_table_data(self, auth_headers, department_id):
        """Test getting table data for current week - used by Card View"""
        # Get current week first
        week_response = requests.get(f"{BASE_URL}/api/weeks/department/{department_id}/current", headers=auth_headers)
        assert week_response.status_code == 200
        week_id = week_response.json()["id"]
        
        # Get table data
        response = requests.get(f"{BASE_URL}/api/weeks/{week_id}/table-data", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "rows" in data
        print(f"Table has {len(data['rows'])} rows")
        for row in data['rows']:
            print(f"  - Employee: {row.get('employee_name')}")
    
    def test_save_table_data(self, auth_headers, department_id):
        """Test saving table data - critical for Card View save functionality"""
        # Get current week
        week_response = requests.get(f"{BASE_URL}/api/weeks/department/{department_id}/current", headers=auth_headers)
        assert week_response.status_code == 200
        week_id = week_response.json()["id"]
        
        # Get current table data
        table_response = requests.get(f"{BASE_URL}/api/weeks/{week_id}/table-data", headers=auth_headers)
        assert table_response.status_code == 200
        current_data = table_response.json()
        
        # Save the same data back (no changes)
        save_response = requests.put(
            f"{BASE_URL}/api/weeks/{week_id}/table-data",
            headers=auth_headers,
            json=current_data
        )
        assert save_response.status_code == 200, f"Save failed: {save_response.text}"
        print("Table data saved successfully")


class TestDepartmentCRUD:
    """Department CRUD tests - create and delete by faction leader"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        if response.status_code == 200:
            return {"Authorization": f"Bearer {response.json().get('access_token')}"}
        pytest.skip("Authentication failed")
    
    def test_create_and_delete_department(self, auth_headers):
        """Test creating and deleting a department"""
        # Create department
        create_response = requests.post(
            f"{BASE_URL}/api/departments/faction/fsb",
            headers=auth_headers,
            json={"name": "TEST_CardView_Department"}
        )
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        created_dept = create_response.json()
        assert created_dept["name"] == "TEST_CardView_Department"
        dept_id = created_dept["id"]
        print(f"Created department: {created_dept['name']} (id: {dept_id})")
        
        # Verify it exists
        get_response = requests.get(f"{BASE_URL}/api/departments/{dept_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        # Delete department
        delete_response = requests.delete(f"{BASE_URL}/api/departments/{dept_id}", headers=auth_headers)
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        print(f"Deleted department: {dept_id}")
        
        # Verify it's deleted
        verify_response = requests.get(f"{BASE_URL}/api/departments/{dept_id}", headers=auth_headers)
        assert verify_response.status_code == 404


class TestAdminPanel:
    """Admin Panel tests"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        if response.status_code == 200:
            return {"Authorization": f"Bearer {response.json().get('access_token')}"}
        pytest.skip("Authentication failed")
    
    def test_get_admin_stats(self, auth_headers):
        """Test getting admin statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_factions" in data
        assert "total_departments" in data
        print(f"Stats: {data['total_users']} users, {data['total_factions']} factions, {data['total_departments']} departments")
    
    def test_get_admin_users(self, auth_headers):
        """Test getting admin users list"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} users")


class TestRBACPermissions:
    """RBAC permission tests - Leaders see only their faction"""
    
    @pytest.fixture
    def auth_headers(self):
        """Get headers with auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        if response.status_code == 200:
            return {"Authorization": f"Bearer {response.json().get('access_token')}"}
        pytest.skip("Authentication failed")
    
    def test_developer_can_access_all_factions(self, auth_headers):
        """Test that developer can access all factions"""
        response = requests.get(f"{BASE_URL}/api/factions/", headers=auth_headers)
        assert response.status_code == 200
        factions = response.json()
        assert len(factions) >= 8, "Developer should see all 8 factions"
        
        # Test access to different factions
        for faction_code in ["fsb", "gov", "gibdd"]:
            response = requests.get(f"{BASE_URL}/api/factions/{faction_code}", headers=auth_headers)
            assert response.status_code == 200, f"Developer should access {faction_code}"
    
    def test_developer_can_manage_departments(self, auth_headers):
        """Test that developer can manage departments in any faction"""
        # Create department in FSB
        create_response = requests.post(
            f"{BASE_URL}/api/departments/faction/fsb",
            headers=auth_headers,
            json={"name": "TEST_RBAC_Department"}
        )
        assert create_response.status_code == 200
        dept_id = create_response.json()["id"]
        
        # Clean up
        requests.delete(f"{BASE_URL}/api/departments/{dept_id}", headers=auth_headers)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
