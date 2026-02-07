"""
Test Senior Staff API endpoints
- GET /api/senior-staff/faction/{code} - Get senior staff table
- PUT /api/senior-staff/faction/{code} - Update senior staff table
- POST /api/senior-staff/faction/{code}/row - Add row
- DELETE /api/senior-staff/faction/{code}/row/{index} - Delete row
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSeniorStaffAPI:
    """Senior Staff API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and get token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as developer
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.token = token
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_01_login_success(self):
        """Test login works"""
        assert hasattr(self, 'token'), "Token should be set after login"
        print(f"Login successful, token obtained")
    
    def test_02_get_senior_staff_table_fsb(self):
        """Test GET /api/senior-staff/faction/fsb"""
        response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/fsb")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "faction_id" in data, "Response should have faction_id"
        assert "rows" in data, "Response should have rows"
        assert isinstance(data["rows"], list), "Rows should be a list"
        
        print(f"Senior staff table for FSB: {len(data['rows'])} rows")
    
    def test_03_get_senior_staff_table_nonexistent_faction(self):
        """Test GET /api/senior-staff/faction/invalid returns 404"""
        response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/invalid_faction")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for non-existent faction")
    
    def test_04_add_row_to_senior_staff(self):
        """Test POST /api/senior-staff/faction/fsb/row"""
        new_row = {
            "employee_name": "TEST_Employee_1",
            "points": 75,
            "norm_status": "met",
            "penalties": [],
            "notes": "Test employee added by pytest"
        }
        
        response = self.session.post(f"{BASE_URL}/api/senior-staff/faction/fsb/row", json=new_row)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Response should have message"
        print(f"Row added successfully: {data['message']}")
        
        # Verify row was added
        get_response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/fsb")
        assert get_response.status_code == 200
        
        table_data = get_response.json()
        employee_names = [row["employee_name"] for row in table_data["rows"]]
        assert "TEST_Employee_1" in employee_names, "New employee should be in the table"
        print(f"Verified: TEST_Employee_1 is in the table")
    
    def test_05_update_senior_staff_table(self):
        """Test PUT /api/senior-staff/faction/fsb"""
        # First get current data
        get_response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/fsb")
        assert get_response.status_code == 200
        
        current_data = get_response.json()
        rows = current_data.get("rows", [])
        
        # Add a new test row
        rows.append({
            "employee_name": "TEST_Employee_2",
            "points": 100,
            "norm_status": "exceeded",
            "penalties": [{"reason": "Test penalty"}],
            "notes": "Updated via PUT"
        })
        
        # Update the table
        update_response = self.session.put(f"{BASE_URL}/api/senior-staff/faction/fsb", json={
            "rows": rows
        })
        
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        data = update_response.json()
        assert "message" in data, "Response should have message"
        print(f"Table updated successfully: {data['message']}")
        
        # Verify update
        verify_response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/fsb")
        verify_data = verify_response.json()
        employee_names = [row["employee_name"] for row in verify_data["rows"]]
        assert "TEST_Employee_2" in employee_names, "TEST_Employee_2 should be in the table"
        print(f"Verified: TEST_Employee_2 is in the table")
    
    def test_06_delete_row_from_senior_staff(self):
        """Test DELETE /api/senior-staff/faction/fsb/row/{index}"""
        # First get current data to find TEST_ rows
        get_response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/fsb")
        assert get_response.status_code == 200
        
        current_data = get_response.json()
        rows = current_data.get("rows", [])
        
        # Find index of TEST_Employee_1
        test_index = None
        for i, row in enumerate(rows):
            if row["employee_name"] == "TEST_Employee_1":
                test_index = i
                break
        
        if test_index is not None:
            # Delete the row
            delete_response = self.session.delete(f"{BASE_URL}/api/senior-staff/faction/fsb/row/{test_index}")
            
            assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
            
            data = delete_response.json()
            assert "message" in data, "Response should have message"
            print(f"Row deleted successfully: {data['message']}")
            
            # Verify deletion
            verify_response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/fsb")
            verify_data = verify_response.json()
            employee_names = [row["employee_name"] for row in verify_data["rows"]]
            assert "TEST_Employee_1" not in employee_names, "TEST_Employee_1 should be deleted"
            print(f"Verified: TEST_Employee_1 is deleted")
        else:
            print("TEST_Employee_1 not found, skipping delete test")
    
    def test_07_delete_invalid_row_index(self):
        """Test DELETE with invalid row index returns 404"""
        response = self.session.delete(f"{BASE_URL}/api/senior-staff/faction/fsb/row/9999")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Correctly returns 404 for invalid row index")
    
    def test_08_permission_check_for_other_factions(self):
        """Test that developer can access all factions"""
        factions = ["gov", "gibdd", "umvd", "army", "hospital", "smi", "fsin"]
        
        for faction in factions:
            response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/{faction}")
            assert response.status_code == 200, f"Developer should access {faction}, got {response.status_code}"
            print(f"Developer can access {faction} senior staff")
    
    def test_09_cleanup_test_data(self):
        """Cleanup TEST_ prefixed data"""
        # Get current data
        get_response = self.session.get(f"{BASE_URL}/api/senior-staff/faction/fsb")
        if get_response.status_code != 200:
            print("Could not get data for cleanup")
            return
        
        current_data = get_response.json()
        rows = current_data.get("rows", [])
        
        # Filter out TEST_ rows
        clean_rows = [row for row in rows if not row["employee_name"].startswith("TEST_")]
        
        # Update with clean data
        update_response = self.session.put(f"{BASE_URL}/api/senior-staff/faction/fsb", json={
            "rows": clean_rows
        })
        
        assert update_response.status_code == 200, f"Cleanup failed: {update_response.status_code}"
        print(f"Cleanup complete: removed {len(rows) - len(clean_rows)} TEST_ rows")


class TestDepartmentTableSave:
    """Test department table save still works"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login and get token"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as developer
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        
        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip(f"Login failed: {login_response.status_code}")
    
    def test_01_get_departments_for_fsb(self):
        """Test GET /api/departments/faction/fsb"""
        response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"FSB has {len(data)} departments")
        
        if len(data) > 0:
            self.department_id = data[0]["id"]
            print(f"First department ID: {self.department_id}")
    
    def test_02_get_current_week(self):
        """Test GET /api/weeks/department/{id}/current"""
        # First get department
        dept_response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        if dept_response.status_code != 200 or len(dept_response.json()) == 0:
            pytest.skip("No departments found")
        
        dept_id = dept_response.json()[0]["id"]
        
        response = self.session.get(f"{BASE_URL}/api/weeks/department/{dept_id}/current")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "id" in data, "Response should have id"
        assert "week_start" in data, "Response should have week_start"
        print(f"Current week ID: {data['id']}")
    
    def test_03_get_table_data(self):
        """Test GET /api/weeks/{id}/table-data"""
        # Get department and week
        dept_response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        if dept_response.status_code != 200 or len(dept_response.json()) == 0:
            pytest.skip("No departments found")
        
        dept_id = dept_response.json()[0]["id"]
        
        week_response = self.session.get(f"{BASE_URL}/api/weeks/department/{dept_id}/current")
        if week_response.status_code != 200:
            pytest.skip("No current week found")
        
        week_id = week_response.json()["id"]
        
        response = self.session.get(f"{BASE_URL}/api/weeks/{week_id}/table-data")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "rows" in data, "Response should have rows"
        print(f"Table has {len(data['rows'])} rows")
    
    def test_04_save_table_data(self):
        """Test PUT /api/weeks/{id}/table-data"""
        # Get department and week
        dept_response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        if dept_response.status_code != 200 or len(dept_response.json()) == 0:
            pytest.skip("No departments found")
        
        dept_id = dept_response.json()[0]["id"]
        
        week_response = self.session.get(f"{BASE_URL}/api/weeks/department/{dept_id}/current")
        if week_response.status_code != 200:
            pytest.skip("No current week found")
        
        week_id = week_response.json()["id"]
        
        # Get current data
        get_response = self.session.get(f"{BASE_URL}/api/weeks/{week_id}/table-data")
        current_data = get_response.json()
        
        # Save the same data (no changes)
        save_response = self.session.put(f"{BASE_URL}/api/weeks/{week_id}/table-data", json={
            "rows": current_data.get("rows", [])
        })
        
        assert save_response.status_code == 200, f"Expected 200, got {save_response.status_code}: {save_response.text}"
        print("Department table save works correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
