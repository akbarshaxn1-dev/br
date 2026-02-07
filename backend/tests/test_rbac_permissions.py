"""
Test RBAC permissions for 'Единый Портал Управления Отделами':
1. Leader creates/deletes departments
2. Head of department can change topics
3. Deputy can ONLY mark attendance (NOT change topics)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestRBACPermissions:
    """Test RBAC permissions logic"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with developer authentication"""
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
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_01_developer_can_access_all_factions(self):
        """Developer can access all factions"""
        factions = ["gov", "fsb", "gibdd", "umvd", "army", "hospital", "smi", "fsin"]
        for faction in factions:
            response = self.session.get(f"{BASE_URL}/api/factions/{faction}")
            assert response.status_code == 200, f"Developer cannot access faction {faction}"
        print("✓ Developer can access all 8 factions")
    
    def test_02_developer_can_manage_departments(self):
        """Developer can create and delete departments"""
        # Create department
        response = self.session.post(f"{BASE_URL}/api/departments/faction/gov", json={
            "name": "TEST_Правительственный отдел"
        })
        assert response.status_code == 200, f"Developer cannot create department: {response.text}"
        dept_id = response.json().get("id")
        print(f"✓ Developer created department: {dept_id}")
        
        # Delete department
        response = self.session.delete(f"{BASE_URL}/api/departments/{dept_id}")
        assert response.status_code == 200, f"Developer cannot delete department: {response.text}"
        print("✓ Developer deleted department")
    
    def test_03_developer_can_manage_topics(self):
        """Developer can create and delete topics"""
        # Create lecture topic
        response = self.session.post(f"{BASE_URL}/api/topics/lectures/faction/gov", json={
            "topic": "TEST_Тестовая лекция"
        })
        assert response.status_code == 200, f"Developer cannot create lecture topic: {response.text}"
        topic_id = response.json().get("id")
        print(f"✓ Developer created lecture topic: {topic_id}")
        
        # Delete lecture topic
        response = self.session.delete(f"{BASE_URL}/api/topics/lectures/{topic_id}")
        assert response.status_code == 200, f"Developer cannot delete lecture topic: {response.text}"
        print("✓ Developer deleted lecture topic")
        
        # Create training topic
        response = self.session.post(f"{BASE_URL}/api/topics/trainings/faction/gov", json={
            "topic": "TEST_Тестовая тренировка"
        })
        assert response.status_code == 200, f"Developer cannot create training topic: {response.text}"
        topic_id = response.json().get("id")
        print(f"✓ Developer created training topic: {topic_id}")
        
        # Delete training topic
        response = self.session.delete(f"{BASE_URL}/api/topics/trainings/{topic_id}")
        assert response.status_code == 200, f"Developer cannot delete training topic: {response.text}"
        print("✓ Developer deleted training topic")
    
    def test_04_developer_can_view_audit_logs(self):
        """Developer can view audit logs"""
        response = self.session.get(f"{BASE_URL}/api/audit/logs")
        assert response.status_code == 200, f"Developer cannot view audit logs: {response.text}"
        logs = response.json()
        print(f"✓ Developer can view audit logs: {len(logs)} entries")
    
    def test_05_developer_can_manage_users(self):
        """Developer can view and manage users"""
        response = self.session.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code == 200, f"Developer cannot view users: {response.text}"
        users = response.json()
        print(f"✓ Developer can view users: {len(users)} users")
    
    def test_06_permissions_module_exists(self):
        """Verify permissions module has correct methods"""
        # This is a code review test - verify the permissions.py has correct logic
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.permissions import Permissions
        
        # Test can_manage_topics for different roles
        # Developer can manage all
        assert Permissions.can_manage_topics('developer', None, 'fsb', 'dept1', None) == True
        
        # Leader can manage their faction
        assert Permissions.can_manage_topics('leader_fsb', 'fsb', 'fsb', 'dept1', None) == True
        assert Permissions.can_manage_topics('leader_gov', 'gov', 'fsb', 'dept1', None) == False
        
        # Head of department can manage their department
        assert Permissions.can_manage_topics('head_of_department', 'fsb', 'fsb', 'dept1', 'dept1') == True
        assert Permissions.can_manage_topics('head_of_department', 'fsb', 'fsb', 'dept1', 'dept2') == False
        
        # Deputy CANNOT manage topics
        assert Permissions.can_manage_topics('deputy_head', 'fsb', 'fsb', 'dept1', 'dept1') == False
        
        print("✓ Permissions module logic verified")
    
    def test_07_deputy_can_edit_table_but_not_topics(self):
        """Deputy can edit table (mark attendance) but NOT manage topics"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.permissions import Permissions
        
        # Deputy CAN edit table (mark attendance)
        assert Permissions.can_edit_table('deputy_head', 'fsb', 'fsb', 'dept1', 'dept1') == True
        
        # Deputy CANNOT manage topics
        assert Permissions.can_manage_topics('deputy_head', 'fsb', 'fsb', 'dept1', 'dept1') == False
        
        print("✓ Deputy permissions verified: can mark attendance, cannot change topics")
    
    def test_08_head_can_edit_table_and_topics(self):
        """Head of department can edit table AND manage topics"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.permissions import Permissions
        
        # Head CAN edit table
        assert Permissions.can_edit_table('head_of_department', 'fsb', 'fsb', 'dept1', 'dept1') == True
        
        # Head CAN manage topics for their department
        assert Permissions.can_manage_topics('head_of_department', 'fsb', 'fsb', 'dept1', 'dept1') == True
        
        # Head CANNOT manage topics for other departments
        assert Permissions.can_manage_topics('head_of_department', 'fsb', 'fsb', 'dept2', 'dept1') == False
        
        print("✓ Head of department permissions verified: can mark attendance AND change topics")
    
    def test_09_leader_can_manage_faction_departments(self):
        """Leader can create/delete departments in their faction"""
        import sys
        sys.path.insert(0, '/app/backend')
        from utils.permissions import Permissions
        
        # Leader CAN manage departments in their faction
        assert Permissions.can_manage_department('leader_fsb', 'fsb', 'fsb', 'dept1', None) == True
        
        # Leader CANNOT manage departments in other factions
        assert Permissions.can_manage_department('leader_fsb', 'fsb', 'gov', 'dept1', None) == False
        
        print("✓ Leader permissions verified: can manage departments in their faction only")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
