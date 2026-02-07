"""
Test system logic for 'Единый Портал Управления Отделами':
1. Login as developer
2. Dashboard stats verification
3. Admin panel user verification
4. FSB faction and department verification
5. Topics management
6. Department CRUD operations
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSystemLogic:
    """Test system logic and RBAC"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login as developer
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "vadim@emergent.dev",
            "password": "admin123"
        })
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        data = login_response.json()
        self.token = data.get("access_token")
        self.user = data.get("user")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        
        print(f"Logged in as: {self.user.get('full_name')} ({self.user.get('role')})")
    
    def test_01_login_as_developer(self):
        """Test login as developer (vadim@emergent.dev/admin123)"""
        assert self.user is not None
        assert self.user.get("email") == "vadim@emergent.dev"
        assert self.user.get("role") == "developer"
        assert self.user.get("full_name") == "Vadim Smirnov"
        print("✓ Login as developer successful")
    
    def test_02_admin_stats(self):
        """Test dashboard shows correct stats (1 user, 8 factions, 1 department)"""
        response = self.session.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code == 200, f"Failed to get stats: {response.text}"
        
        stats = response.json()
        assert stats.get("total_users") == 1, f"Expected 1 user, got {stats.get('total_users')}"
        assert stats.get("total_factions") == 8, f"Expected 8 factions, got {stats.get('total_factions')}"
        assert stats.get("total_departments") == 1, f"Expected 1 department, got {stats.get('total_departments')}"
        print(f"✓ Stats verified: {stats.get('total_users')} users, {stats.get('total_factions')} factions, {stats.get('total_departments')} departments")
    
    def test_03_admin_users_list(self):
        """Test admin panel shows only Vadim Smirnov"""
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        
        users = response.json()
        assert len(users) == 1, f"Expected 1 user, got {len(users)}"
        assert users[0].get("full_name") == "Vadim Smirnov"
        assert users[0].get("email") == "vadim@emergent.dev"
        assert users[0].get("role") == "developer"
        print(f"✓ Admin panel shows only: {users[0].get('full_name')}")
    
    def test_04_factions_list(self):
        """Test all 8 factions are available"""
        response = self.session.get(f"{BASE_URL}/api/factions/")
        assert response.status_code == 200, f"Failed to get factions: {response.text}"
        
        factions = response.json()
        assert len(factions) == 8, f"Expected 8 factions, got {len(factions)}"
        
        faction_codes = [f.get("code") for f in factions]
        expected_codes = ["gov", "fsb", "gibdd", "umvd", "army", "hospital", "smi", "fsin"]
        for code in expected_codes:
            assert code in faction_codes, f"Missing faction: {code}"
        print(f"✓ All 8 factions present: {faction_codes}")
    
    def test_05_fsb_faction_departments(self):
        """Test FSB faction page shows 'Отдел контрразведки' department"""
        response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        assert response.status_code == 200, f"Failed to get FSB departments: {response.text}"
        
        departments = response.json()
        assert len(departments) == 1, f"Expected 1 department, got {len(departments)}"
        assert departments[0].get("name") == "Отдел контрразведки"
        
        self.department_id = departments[0].get("id")
        print(f"✓ FSB department found: {departments[0].get('name')} (ID: {self.department_id})")
    
    def test_06_department_details(self):
        """Test department details"""
        # First get department ID
        response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        departments = response.json()
        department_id = departments[0].get("id")
        
        response = self.session.get(f"{BASE_URL}/api/departments/{department_id}")
        assert response.status_code == 200, f"Failed to get department: {response.text}"
        
        dept = response.json()
        assert dept.get("name") == "Отдел контрразведки"
        print(f"✓ Department details verified: {dept.get('name')}")
    
    def test_07_lecture_topics(self):
        """Test lecture topics for FSB (УК РФ, КоАП, ФЗ, УПК, Устав)"""
        response = self.session.get(f"{BASE_URL}/api/topics/lectures/faction/fsb")
        assert response.status_code == 200, f"Failed to get lecture topics: {response.text}"
        
        topics = response.json()
        topic_names = [t.get("topic") for t in topics]
        expected_topics = ["УК РФ", "КоАП", "ФЗ", "УПК", "Устав"]
        
        for expected in expected_topics:
            assert expected in topic_names, f"Missing lecture topic: {expected}"
        print(f"✓ Lecture topics verified: {topic_names}")
    
    def test_08_training_topics(self):
        """Test training topics for FSB (Закрепление, Доверс, Писпен, Обыск)"""
        response = self.session.get(f"{BASE_URL}/api/topics/trainings/faction/fsb")
        assert response.status_code == 200, f"Failed to get training topics: {response.text}"
        
        topics = response.json()
        topic_names = [t.get("topic") for t in topics]
        expected_topics = ["Закрепление", "Доверс", "Писпен", "Обыск"]
        
        for expected in expected_topics:
            assert expected in topic_names, f"Missing training topic: {expected}"
        print(f"✓ Training topics verified: {topic_names}")
    
    def test_09_current_week(self):
        """Test current week for department"""
        # Get department ID
        response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        departments = response.json()
        department_id = departments[0].get("id")
        
        response = self.session.get(f"{BASE_URL}/api/weeks/department/{department_id}/current")
        assert response.status_code == 200, f"Failed to get current week: {response.text}"
        
        week = response.json()
        assert week.get("id") is not None
        assert week.get("week_start") is not None
        assert week.get("week_end") is not None
        print(f"✓ Current week: {week.get('week_start')} - {week.get('week_end')}")
    
    def test_10_table_data(self):
        """Test table data for current week"""
        # Get department ID
        response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        departments = response.json()
        department_id = departments[0].get("id")
        
        # Get current week
        response = self.session.get(f"{BASE_URL}/api/weeks/department/{department_id}/current")
        week = response.json()
        week_id = week.get("id")
        
        response = self.session.get(f"{BASE_URL}/api/weeks/{week_id}/table-data")
        assert response.status_code == 200, f"Failed to get table data: {response.text}"
        
        table_data = response.json()
        assert "rows" in table_data
        print(f"✓ Table data retrieved: {len(table_data.get('rows', []))} rows")
    
    def test_11_create_department(self):
        """Test create department for admin"""
        response = self.session.post(f"{BASE_URL}/api/departments/faction/fsb", json={
            "name": "TEST_Тестовый отдел"
        })
        assert response.status_code == 200, f"Failed to create department: {response.text}"
        
        dept = response.json()
        assert dept.get("name") == "TEST_Тестовый отдел"
        self.test_dept_id = dept.get("id")
        print(f"✓ Department created: {dept.get('name')} (ID: {self.test_dept_id})")
        
        # Cleanup - delete the test department
        delete_response = self.session.delete(f"{BASE_URL}/api/departments/{self.test_dept_id}")
        assert delete_response.status_code == 200, f"Failed to delete test department: {delete_response.text}"
        print(f"✓ Test department deleted")
    
    def test_12_delete_department_button_exists(self):
        """Test delete department functionality exists"""
        # Create a test department
        response = self.session.post(f"{BASE_URL}/api/departments/faction/fsb", json={
            "name": "TEST_Отдел для удаления"
        })
        assert response.status_code == 200
        dept_id = response.json().get("id")
        
        # Delete the department
        delete_response = self.session.delete(f"{BASE_URL}/api/departments/{dept_id}")
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        # Verify it's deleted
        get_response = self.session.get(f"{BASE_URL}/api/departments/{dept_id}")
        assert get_response.status_code == 404, "Department should be deleted"
        print("✓ Delete department functionality works")
    
    def test_13_weeks_archive(self):
        """Test weeks archive for department"""
        # Get department ID
        response = self.session.get(f"{BASE_URL}/api/departments/faction/fsb")
        departments = response.json()
        department_id = departments[0].get("id")
        
        response = self.session.get(f"{BASE_URL}/api/weeks/department/{department_id}")
        assert response.status_code == 200, f"Failed to get weeks: {response.text}"
        
        weeks = response.json()
        assert len(weeks) >= 1, "Should have at least 1 week"
        print(f"✓ Weeks archive: {len(weeks)} weeks found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
