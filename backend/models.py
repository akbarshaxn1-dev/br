from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

class RoleEnum(str, Enum):
    DEVELOPER = "developer"
    GS = "gs"
    ZGS = "zgs"
    LEADER_GOV = "leader_gov"
    LEADER_FSB = "leader_fsb"
    LEADER_GIBDD = "leader_gibdd"
    LEADER_UMVD = "leader_umvd"
    LEADER_ARMY = "leader_army"
    LEADER_HOSPITAL = "leader_hospital"
    LEADER_SMI = "leader_smi"
    LEADER_FSIN = "leader_fsin"
    HEAD_OF_DEPARTMENT = "head_of_department"
    DEPUTY_HEAD = "deputy_head"

class FactionEnum(str, Enum):
    GOV = "gov"
    FSB = "fsb"
    GIBDD = "gibdd"
    UMVD = "umvd"
    ARMY = "army"
    HOSPITAL = "hospital"
    SMI = "smi"
    FSIN = "fsin"

class NotificationTypeEnum(str, Enum):
    TABLE_STRUCTURE_CHANGED = "table_structure_changed"
    ROLE_ASSIGNED = "role_assigned"
    DEPARTMENT_DELETED = "department_deleted"
    EMPLOYEE_ADDED = "employee_added"
    WARNING = "warning"
    DATA_RESTORED = "data_restored"

# Base response models
class UserBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    full_name: str
    vk_url: Optional[str] = None
    role: RoleEnum
    faction: Optional[FactionEnum] = None
    department_id: Optional[str] = None
    is_active: bool = True
    two_fa_enabled: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    vk_url: Optional[str] = None
    role: RoleEnum
    faction: Optional[FactionEnum] = None
    department_id: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    otp_code: Optional[str] = None

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    full_name: str
    vk_url: Optional[str]
    role: str
    faction: Optional[str]
    department_id: Optional[str]
    is_active: bool
    two_fa_enabled: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class TwoFASetupResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: List[str]

class FactionBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: FactionEnum
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FactionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    code: str
    name: str
    description: Optional[str]
    created_at: datetime

class DepartmentBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faction_id: str
    name: str
    head_user_id: Optional[str] = None
    deputy_user_ids: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DepartmentCreate(BaseModel):
    name: str
    head_user_id: Optional[str] = None
    deputy_user_ids: List[str] = []

class DepartmentResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    faction_id: str
    faction_code: Optional[str] = None
    name: str
    head_user_id: Optional[str]
    deputy_user_ids: List[str]
    created_at: datetime

class TableStructureColumn(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # 'text', 'checkbox', 'lecture', 'training', 'date', 'number'
    order: int
    editable: bool = True

class TableStructure(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    department_id: str
    columns: List[TableStructureColumn]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WeekBase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    department_id: str
    week_start: datetime
    week_end: datetime
    is_current: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WeekResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    department_id: str
    week_start: datetime
    week_end: datetime
    is_current: bool
    created_at: datetime

class TableRowData(BaseModel):
    employee_name: str
    cells: Dict[str, Any]  # column_id -> value

class TableData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    week_id: str
    department_id: str
    rows: List[TableRowData]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TableDataUpdate(BaseModel):
    rows: List[TableRowData]

class LectureTopic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faction_id: str
    topic: str
    order: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LectureTopicCreate(BaseModel):
    topic: str
    order: Optional[int] = None

class LectureTopicResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    faction_id: str
    topic: str
    order: int
    created_at: datetime

class TrainingTopic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faction_id: str
    topic: str
    order: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrainingTopicCreate(BaseModel):
    topic: str
    order: Optional[int] = None

class TrainingTopicResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    faction_id: str
    topic: str
    order: int
    created_at: datetime

class SeniorStaffRow(BaseModel):
    employee_name: str
    points: int = 0
    norm_status: str = "not_met"  # 'met', 'not_met', 'exceeded'
    penalties: List[Dict[str, Any]] = []
    notes: Optional[str] = None

class SeniorStaffTable(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    faction_id: str
    rows: List[SeniorStaffRow]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SeniorStaffTableUpdate(BaseModel):
    rows: List[SeniorStaffRow]

class AuditLog(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_email: str
    action: str
    resource_type: str
    resource_id: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    user_email: str
    action: str
    resource_type: str
    resource_id: str
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: NotificationTypeEnum
    title: str
    message: str
    read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NotificationResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    type: str
    title: str
    message: str
    read: bool
    created_at: datetime

class RecoverySnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collection_name: str
    snapshot_data: Dict[str, Any]
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: Optional[str] = None
