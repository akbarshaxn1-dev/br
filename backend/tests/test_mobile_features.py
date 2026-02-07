"""
Test suite for Mobile Responsive Features - Iteration 3
Tests: Week Archive, Department CRUD, WebSocket status
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestWeekArchive:
    """Week Archive endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Get a department ID for testing
        factions_response = requests.get(f"{BASE_URL}/api/factions/", headers=self.headers)
        assert factions_response.status_code == 200
        
        # Get FSB departments
        depts_response = requests.get(f"{BASE_URL}/api/departments/faction/fsb", headers=self.headers)
        assert depts_response.status_code == 200
        depts = depts_response.json()
        if depts:
            self.department_id = depts[0]["id"]
        else:
            self.department_id = None
    
    def test_get_department_weeks(self):
        """Test GET /api/weeks/department/{department_id} - Get all weeks for a department"""
        if not self.department_id:
            pytest.skip("No department available for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/weeks/department/{self.department_id}",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Failed to get weeks: {response.text}"
        weeks = response.json()
        assert isinstance(weeks, list), "Response should be a list"
        
        # Verify week structure if weeks exist
        if weeks:
            week = weeks[0]
            assert "id" in week, "Week should have id"
            assert "week_start" in week, "Week should have week_start"
            assert "week_end" in week, "Week should have week_end"
            assert "is_current" in week, "Week should have is_current flag"
            print(f"SUCCESS: Found {len(weeks)} weeks for department")
    
    def test_get_current_week(self):
        """Test GET /api/weeks/department/{department_id}/current - Get or create current week"""
        if not self.department_id:
            pytest.skip("No department available for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/weeks/department/{self.department_id}/current",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Failed to get current week: {response.text}"
        week = response.json()
        
        assert "id" in week, "Week should have id"
        assert "week_start" in week, "Week should have week_start"
        assert "week_end" in week, "Week should have week_end"
        assert week.get("is_current") == True, "Current week should have is_current=True"
        print(f"SUCCESS: Current week ID: {week['id']}")
    
    def test_get_week_table_data(self):
        """Test GET /api/weeks/{week_id}/table-data - Get table data for a week"""
        if not self.department_id:
            pytest.skip("No department available for testing")
        
        # First get current week
        week_response = requests.get(
            f"{BASE_URL}/api/weeks/department/{self.department_id}/current",
            headers=self.headers
        )
        assert week_response.status_code == 200
        week_id = week_response.json()["id"]
        
        # Get table data
        response = requests.get(
            f"{BASE_URL}/api/weeks/{week_id}/table-data",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Failed to get table data: {response.text}"
        table_data = response.json()
        
        assert "rows" in table_data, "Table data should have rows"
        assert isinstance(table_data["rows"], list), "Rows should be a list"
        print(f"SUCCESS: Table data has {len(table_data['rows'])} rows")


class TestDepartmentCRUD:
    """Department Create/Delete tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_department(self):
        """Test POST /api/departments/faction/{faction_code} - Create new department"""
        unique_id = str(uuid.uuid4())[:8]
        dept_name = f"TEST_Dept_{unique_id}"
        
        response = requests.post(
            f"{BASE_URL}/api/departments/faction/fsb",
            json={"name": dept_name},
            headers=self.headers
        )
        
        assert response.status_code in [200, 201], f"Failed to create department: {response.text}"
        dept = response.json()
        
        assert "id" in dept, "Department should have id"
        assert dept["name"] == dept_name, "Department name should match"
        print(f"SUCCESS: Created department {dept_name} with ID {dept['id']}")
        
        # Store for cleanup
        self.created_dept_id = dept["id"]
        return dept["id"]
    
    def test_delete_department(self):
        """Test DELETE /api/departments/{department_id} - Delete department"""
        # First create a department to delete
        unique_id = str(uuid.uuid4())[:8]
        dept_name = f"TEST_DeleteDept_{unique_id}"
        
        create_response = requests.post(
            f"{BASE_URL}/api/departments/faction/fsb",
            json={"name": dept_name},
            headers=self.headers
        )
        
        assert create_response.status_code in [200, 201], f"Failed to create department: {create_response.text}"
        dept_id = create_response.json()["id"]
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/departments/{dept_id}",
            headers=self.headers
        )
        
        assert delete_response.status_code in [200, 204], f"Failed to delete department: {delete_response.text}"
        print(f"SUCCESS: Deleted department {dept_id}")
        
        # Verify it's deleted
        get_response = requests.get(
            f"{BASE_URL}/api/departments/{dept_id}",
            headers=self.headers
        )
        assert get_response.status_code == 404, "Deleted department should return 404"
        print("SUCCESS: Verified department is deleted")
    
    def test_get_faction_departments(self):
        """Test GET /api/departments/faction/{faction_code} - Get departments for faction"""
        response = requests.get(
            f"{BASE_URL}/api/departments/faction/fsb",
            headers=self.headers
        )
        
        assert response.status_code == 200, f"Failed to get departments: {response.text}"
        depts = response.json()
        
        assert isinstance(depts, list), "Response should be a list"
        print(f"SUCCESS: Found {len(depts)} departments in FSB faction")
        
        # Verify department structure
        if depts:
            dept = depts[0]
            assert "id" in dept, "Department should have id"
            assert "name" in dept, "Department should have name"


class TestFactionEndpoints:
    """Faction endpoints tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_all_factions(self):
        """Test GET /api/factions/ - Get all factions"""
        response = requests.get(f"{BASE_URL}/api/factions/", headers=self.headers)
        
        assert response.status_code == 200, f"Failed to get factions: {response.text}"
        factions = response.json()
        
        assert isinstance(factions, list), "Response should be a list"
        assert len(factions) == 8, f"Expected 8 factions, got {len(factions)}"
        
        # Verify faction structure
        faction = factions[0]
        assert "id" in faction, "Faction should have id"
        assert "code" in faction, "Faction should have code"
        assert "name" in faction, "Faction should have name"
        print(f"SUCCESS: Found {len(factions)} factions")
    
    def test_get_faction_by_code(self):
        """Test GET /api/factions/{code} - Get specific faction"""
        response = requests.get(f"{BASE_URL}/api/factions/fsb", headers=self.headers)
        
        assert response.status_code == 200, f"Failed to get faction: {response.text}"
        faction = response.json()
        
        assert faction["code"] == "fsb", "Faction code should be fsb"
        assert "name" in faction, "Faction should have name"
        print(f"SUCCESS: Got faction {faction['name']}")


class TestAdminEndpoints:
    """Admin panel endpoints tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_get_admin_stats(self):
        """Test GET /api/admin/stats - Get admin statistics"""
        response = requests.get(f"{BASE_URL}/api/admin/stats", headers=self.headers)
        
        assert response.status_code == 200, f"Failed to get stats: {response.text}"
        stats = response.json()
        
        assert "total_users" in stats, "Stats should have total_users"
        assert "total_factions" in stats, "Stats should have total_factions"
        assert "total_departments" in stats, "Stats should have total_departments"
        print(f"SUCCESS: Stats - Users: {stats['total_users']}, Factions: {stats['total_factions']}, Departments: {stats['total_departments']}")
    
    def test_get_admin_users(self):
        """Test GET /api/admin/users - Get all users"""
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=self.headers)
        
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        users = response.json()
        
        assert isinstance(users, list), "Response should be a list"
        print(f"SUCCESS: Found {len(users)} users")
    
    def test_get_admin_roles(self):
        """Test GET /api/admin/roles - Get available roles"""
        response = requests.get(f"{BASE_URL}/api/admin/roles", headers=self.headers)
        
        assert response.status_code == 200, f"Failed to get roles: {response.text}"
        roles = response.json()
        
        assert isinstance(roles, list), "Response should be a list"
        assert len(roles) > 0, "Should have at least one role"
        
        # Verify role structure
        role = roles[0]
        assert "value" in role, "Role should have value"
        assert "label" in role, "Role should have label"
        print(f"SUCCESS: Found {len(roles)} roles")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
