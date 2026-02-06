from models import RoleEnum, FactionEnum
from typing import Optional

class Permissions:
    """Permission checking system based on RBAC"""
    
    @staticmethod
    def can_access_all_factions(role: str) -> bool:
        """Check if role can access all factions"""
        return role in [RoleEnum.DEVELOPER, RoleEnum.GS, RoleEnum.ZGS]
    
    @staticmethod
    def can_manage_factions(role: str) -> bool:
        """Check if role can manage factions"""
        return role in [RoleEnum.DEVELOPER, RoleEnum.GS, RoleEnum.ZGS]
    
    @staticmethod
    def can_manage_users(role: str) -> bool:
        """Check if role can manage users"""
        return role in [RoleEnum.DEVELOPER, RoleEnum.GS, RoleEnum.ZGS]
    
    @staticmethod
    def can_view_audit_logs(role: str) -> bool:
        """Check if role can view audit logs"""
        return role in [RoleEnum.DEVELOPER, RoleEnum.GS, RoleEnum.ZGS]
    
    @staticmethod
    def can_restore_data(role: str) -> bool:
        """Check if role can restore data"""
        return role == RoleEnum.DEVELOPER
    
    @staticmethod
    def can_switch_role(role: str) -> bool:
        """Check if role can switch to other roles"""
        return role == RoleEnum.DEVELOPER
    
    @staticmethod
    def can_manage_department(role: str, user_faction: Optional[str], 
                             department_faction: str, department_id: str,
                             user_department_id: Optional[str]) -> bool:
        """Check if user can manage specific department"""
        # Developer, GS, ZGS can manage all
        if role in [RoleEnum.DEVELOPER, RoleEnum.GS, RoleEnum.ZGS]:
            return True
        
        # Leaders can manage departments in their faction
        if role.startswith("leader_") and user_faction == department_faction:
            return True
        
        # Head of department can manage their own department
        if role == RoleEnum.HEAD_OF_DEPARTMENT and user_department_id == department_id:
            return True
        
        return False
    
    @staticmethod
    def can_edit_table(role: str, user_faction: Optional[str],
                      department_faction: str, department_id: str,
                      user_department_id: Optional[str]) -> bool:
        """Check if user can edit table data"""
        # Developer, GS, ZGS can edit all
        if role in [RoleEnum.DEVELOPER, RoleEnum.GS, RoleEnum.ZGS]:
            return True
        
        # Leaders can edit tables in their faction
        if role.startswith("leader_") and user_faction == department_faction:
            return True
        
        # Head and deputy can edit their department tables
        if role in [RoleEnum.HEAD_OF_DEPARTMENT, RoleEnum.DEPUTY_HEAD] and user_department_id == department_id:
            return True
        
        return False
    
    @staticmethod
    def can_view_faction(role: str, user_faction: Optional[str], 
                        target_faction: str) -> bool:
        """Check if user can view specific faction data"""
        # Developer, GS, ZGS can view all factions
        if role in [RoleEnum.DEVELOPER, RoleEnum.GS, RoleEnum.ZGS]:
            return True
        
        # Users can only view their own faction
        return user_faction == target_faction
    
    @staticmethod
    def requires_2fa(role: str) -> bool:
        """Check if role requires 2FA"""
        return role in [
            RoleEnum.DEVELOPER,
            RoleEnum.GS,
            RoleEnum.ZGS,
            RoleEnum.LEADER_GOV,
            RoleEnum.LEADER_FSB,
            RoleEnum.LEADER_GIBDD,
            RoleEnum.LEADER_UMVD,
            RoleEnum.LEADER_ARMY,
            RoleEnum.LEADER_HOSPITAL,
            RoleEnum.LEADER_SMI,
            RoleEnum.LEADER_FSIN,
        ]
