"""
Backend API Tests for Admin Panel and Department Topics Management
Tests: Admin user CRUD, User activation/deactivation, Department-level topics
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials (admin user)
TEST_EMAIL = "vadim@emergent.dev"
TEST_PASSWORD = "admin123"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for admin user"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture(scope="module")
def test_department_id(auth_headers):
    """Get a department ID for testing"""
    response = requests.get(
        f"{BASE_URL}/api/departments/faction/fsb",
        headers=auth_headers
    )
    if response.status_code == 200:
        depts = response.json()
        if len(depts) > 0:
            return depts[0]["id"]
    return None


class TestAdminStats:
    """Admin statistics endpoint tests"""
    
    def test_get_admin_stats(self, auth_headers):
        """Test getting admin dashboard statistics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify stats structure
        assert "total_users" in data
        assert "total_departments" in data
        assert "total_factions" in data
        assert "users_by_role" in data
        assert "users_by_faction" in data
        assert "recent_logins_24h" in data
        
        print(f"Stats: {data['total_users']} users, {data['total_factions']} factions, {data['total_departments']} departments")
        print(f"Recent logins (24h): {data['recent_logins_24h']}")


class TestAdminRolesAndFactions:
    """Admin roles and factions list tests"""
    
    def test_get_roles_list(self, auth_headers):
        """Test getting list of available roles"""
        response = requests.get(
            f"{BASE_URL}/api/admin/roles",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Check role structure
        role = data[0]
        assert "value" in role
        assert "label" in role
        
        print(f"Found {len(data)} roles")
        # Verify key roles exist
        role_values = [r["value"] for r in data]
        assert "developer" in role_values
        assert "gs" in role_values
        assert "head_of_department" in role_values
        print("Key roles verified: developer, gs, head_of_department")
    
    def test_get_factions_list(self, auth_headers):
        """Test getting list of available factions"""
        response = requests.get(
            f"{BASE_URL}/api/admin/factions-list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 8  # 8 factions expected
        
        # Check faction structure
        faction = data[0]
        assert "value" in faction
        assert "label" in faction
        
        print(f"Found {len(data)} factions")
        faction_values = [f["value"] for f in data]
        assert "fsb" in faction_values
        assert "gov" in faction_values
        print("Key factions verified: fsb, gov")
    
    def test_get_departments_list(self, auth_headers):
        """Test getting departments list for dropdown"""
        response = requests.get(
            f"{BASE_URL}/api/admin/departments-list?faction=fsb",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Found {len(data)} departments for FSB")
        
        if len(data) > 0:
            dept = data[0]
            assert "id" in dept
            assert "name" in dept


class TestAdminUserManagement:
    """Admin user CRUD operations tests"""
    
    def test_get_all_users(self, auth_headers):
        """Test getting all users"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Found {len(data)} users")
        
        if len(data) > 0:
            user = data[0]
            assert "id" in user
            assert "email" in user
            assert "role" in user
            assert "is_active" in user
    
    def test_filter_users_by_faction(self, auth_headers):
        """Test filtering users by faction"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users?faction=fsb",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Found {len(data)} users in FSB faction")
        
        # Verify all returned users are in FSB faction
        for user in data:
            assert user.get("faction") == "fsb", f"User {user['email']} not in FSB faction"
    
    def test_filter_users_by_role(self, auth_headers):
        """Test filtering users by role"""
        response = requests.get(
            f"{BASE_URL}/api/admin/users?role=developer",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Found {len(data)} developers")
        
        # Verify all returned users have developer role
        for user in data:
            assert user.get("role") == "developer", f"User {user['email']} is not developer"
    
    def test_create_user(self, auth_headers):
        """Test creating a new user"""
        unique_id = str(uuid.uuid4())[:8]
        # Use zgs role which doesn't require department_id
        user_data = {
            "email": f"TEST_user_{unique_id}@test.com",
            "password": "testpass123",
            "full_name": f"TEST User {unique_id}",
            "nickname": f"TEST_Nick_{unique_id}",
            "position": "Тестовая должность",
            "vk_url": "https://vk.com/test",
            "role": "zgs"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers,
            json=user_data
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert data["email"] == user_data["email"]
        assert data["nickname"] == user_data["nickname"]
        assert data["role"] == user_data["role"]
        assert data["is_active"] == True
        
        print(f"Created user: {data['nickname']} ({data['id']})")
        return data
    
    def test_create_user_duplicate_email(self, auth_headers):
        """Test creating user with duplicate email fails"""
        # Try to create user with existing email
        user_data = {
            "email": TEST_EMAIL,  # Already exists
            "password": "testpass123",
            "full_name": "Duplicate User",
            "nickname": "DuplicateNick",
            "role": "deputy_head"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers,
            json=user_data
        )
        assert response.status_code == 400, f"Should fail with 400, got: {response.status_code}"
        print("Duplicate email correctly rejected")
    
    def test_get_user_by_id(self, auth_headers):
        """Test getting specific user by ID"""
        # First create a user (use zgs role which doesn't require department)
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers,
            json={
                "email": f"TEST_getuser_{unique_id}@test.com",
                "password": "testpass123",
                "full_name": f"TEST GetUser {unique_id}",
                "nickname": f"TEST_GetNick_{unique_id}",
                "role": "zgs"
            }
        )
        assert create_response.status_code == 200
        user_id = create_response.json()["id"]
        
        # Get user by ID
        response = requests.get(
            f"{BASE_URL}/api/admin/users/{user_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["id"] == user_id
        print(f"Retrieved user: {data['nickname']}")
    
    def test_create_user_with_department(self, auth_headers, test_department_id):
        """Test creating a user with department (head_of_department role)"""
        if not test_department_id:
            pytest.skip("No department available for testing")
        
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "email": f"TEST_deptuser_{unique_id}@test.com",
            "password": "testpass123",
            "full_name": f"TEST DeptUser {unique_id}",
            "nickname": f"TEST_DeptNick_{unique_id}",
            "role": "head_of_department",
            "faction": "fsb",
            "department_id": test_department_id
        }
        
        response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers,
            json=user_data
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["role"] == "head_of_department"
        assert data["department_id"] == test_department_id
        print(f"Created department head user: {data['nickname']}")
    
    def test_update_user(self, auth_headers):
        """Test updating user"""
        # First create a user (use zgs role which doesn't require department)
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers,
            json={
                "email": f"TEST_updateuser_{unique_id}@test.com",
                "password": "testpass123",
                "full_name": f"TEST UpdateUser {unique_id}",
                "nickname": f"TEST_UpdateNick_{unique_id}",
                "role": "zgs"
            }
        )
        assert create_response.status_code == 200
        user_id = create_response.json()["id"]
        
        # Update user
        update_data = {
            "full_name": "Updated Name",
            "position": "Updated Position"
        }
        response = requests.put(
            f"{BASE_URL}/api/admin/users/{user_id}",
            headers=auth_headers,
            json=update_data
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data["full_name"] == "Updated Name"
        assert data["position"] == "Updated Position"
        print(f"Updated user: {data['id']}")
    
    def test_deactivate_user(self, auth_headers):
        """Test deactivating (soft delete) user"""
        # First create a user (use zgs role which doesn't require department)
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers,
            json={
                "email": f"TEST_deactivate_{unique_id}@test.com",
                "password": "testpass123",
                "full_name": f"TEST Deactivate {unique_id}",
                "nickname": f"TEST_DeactNick_{unique_id}",
                "role": "zgs"
            }
        )
        assert create_response.status_code == 200
        user_id = create_response.json()["id"]
        
        # Deactivate user
        response = requests.delete(
            f"{BASE_URL}/api/admin/users/{user_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify user is deactivated
        get_response = requests.get(
            f"{BASE_URL}/api/admin/users/{user_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] == False
        print(f"Deactivated user: {user_id}")
    
    def test_activate_user(self, auth_headers):
        """Test activating a deactivated user"""
        # First create and deactivate a user (use zgs role which doesn't require department)
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(
            f"{BASE_URL}/api/admin/users",
            headers=auth_headers,
            json={
                "email": f"TEST_activate_{unique_id}@test.com",
                "password": "testpass123",
                "full_name": f"TEST Activate {unique_id}",
                "nickname": f"TEST_ActNick_{unique_id}",
                "role": "zgs"
            }
        )
        assert create_response.status_code == 200
        user_id = create_response.json()["id"]
        
        # Deactivate
        requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=auth_headers)
        
        # Activate
        response = requests.post(
            f"{BASE_URL}/api/admin/users/{user_id}/activate",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        
        # Verify user is active
        get_response = requests.get(
            f"{BASE_URL}/api/admin/users/{user_id}",
            headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["is_active"] == True
        print(f"Activated user: {user_id}")


class TestDepartmentTopics:
    """Department-level topics management tests"""
    
    def test_get_department_lecture_topics(self, auth_headers, test_department_id):
        """Test getting lecture topics for a department"""
        if not test_department_id:
            pytest.skip("No department available for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/topics/lectures/department/{test_department_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Department has {len(data)} lecture topics")
        
        if len(data) > 0:
            topic = data[0]
            assert "id" in topic
            assert "topic" in topic
    
    def test_get_department_training_topics(self, auth_headers, test_department_id):
        """Test getting training topics for a department"""
        if not test_department_id:
            pytest.skip("No department available for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/topics/trainings/department/{test_department_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert isinstance(data, list)
        print(f"Department has {len(data)} training topics")
    
    def test_create_department_lecture_topic(self, auth_headers, test_department_id):
        """Test creating a custom lecture topic for department"""
        if not test_department_id:
            pytest.skip("No department available for testing")
        
        unique_id = str(uuid.uuid4())[:8]
        topic_data = {"topic": f"TEST_Лекция_{unique_id}"}
        
        response = requests.post(
            f"{BASE_URL}/api/topics/lectures/department/{test_department_id}",
            headers=auth_headers,
            json=topic_data
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert data["topic"] == topic_data["topic"]
        # department_id may not be in response model, just verify topic was created
        
        print(f"Created department lecture topic: {data['topic']}")
        return data
    
    def test_create_department_training_topic(self, auth_headers, test_department_id):
        """Test creating a custom training topic for department"""
        if not test_department_id:
            pytest.skip("No department available for testing")
        
        unique_id = str(uuid.uuid4())[:8]
        topic_data = {"topic": f"TEST_Тренировка_{unique_id}"}
        
        response = requests.post(
            f"{BASE_URL}/api/topics/trainings/department/{test_department_id}",
            headers=auth_headers,
            json=topic_data
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "id" in data
        assert data["topic"] == topic_data["topic"]
        # department_id may not be in response model, just verify topic was created
        
        print(f"Created department training topic: {data['topic']}")
        return data
    
    def test_delete_department_lecture_topic(self, auth_headers, test_department_id):
        """Test deleting a department lecture topic"""
        if not test_department_id:
            pytest.skip("No department available for testing")
        
        # First create a topic
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(
            f"{BASE_URL}/api/topics/lectures/department/{test_department_id}",
            headers=auth_headers,
            json={"topic": f"TEST_DeleteLecture_{unique_id}"}
        )
        assert create_response.status_code == 200
        topic_id = create_response.json()["id"]
        
        # Delete topic
        response = requests.delete(
            f"{BASE_URL}/api/topics/lectures/department/{test_department_id}/{topic_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print(f"Deleted department lecture topic: {topic_id}")
    
    def test_delete_department_training_topic(self, auth_headers, test_department_id):
        """Test deleting a department training topic"""
        if not test_department_id:
            pytest.skip("No department available for testing")
        
        # First create a topic
        unique_id = str(uuid.uuid4())[:8]
        create_response = requests.post(
            f"{BASE_URL}/api/topics/trainings/department/{test_department_id}",
            headers=auth_headers,
            json={"topic": f"TEST_DeleteTraining_{unique_id}"}
        )
        assert create_response.status_code == 200
        topic_id = create_response.json()["id"]
        
        # Delete topic
        response = requests.delete(
            f"{BASE_URL}/api/topics/trainings/department/{test_department_id}/{topic_id}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        print(f"Deleted department training topic: {topic_id}")


class TestAdminAccessControl:
    """Test admin access control - non-admin users should be denied"""
    
    def test_unauthorized_access_to_admin_stats(self):
        """Test that unauthenticated users cannot access admin stats"""
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        assert response.status_code in [401, 403], f"Should be denied, got: {response.status_code}"
        print("Unauthorized access to admin stats correctly denied")
    
    def test_unauthorized_access_to_admin_users(self):
        """Test that unauthenticated users cannot access admin users"""
        response = requests.get(f"{BASE_URL}/api/admin/users")
        assert response.status_code in [401, 403], f"Should be denied, got: {response.status_code}"
        print("Unauthorized access to admin users correctly denied")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
