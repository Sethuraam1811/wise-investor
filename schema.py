# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

# ==================== ORGANIZATION SCHEMAS ====================

class OrganizationBase(BaseModel):
    legal_name: str
    ein: str
    timezone: Optional[str] = None
    status: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    legal_name: Optional[str] = None
    timezone: Optional[str] = None
    status: Optional[str] = None

class Organization(OrganizationBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class OrganizationListResponse(BaseModel):
    data: List[Organization]
    total: int
    limit: int
    offset: int

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    organization_id: UUID
    email: EmailStr
    status: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    status: Optional[str] = None

class User(UserBase):
    id: UUID
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== ROLE SCHEMAS ====================

class RoleBase(BaseModel):
    organization_id: UUID
    name: str

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[str] = None

class Role(RoleBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== PERMISSION SCHEMAS ====================

class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== USER_ROLE SCHEMAS ====================

class UserRoleCreate(BaseModel):
    user_id: UUID
    role_id: UUID

class UserRole(BaseModel):
    user_id: UUID
    role_id: UUID

    class Config:
        from_attributes = True

# ==================== ROLE_PERMISSION SCHEMAS ====================

class RolePermissionCreate(BaseModel):
    role_id: UUID
    permission_id: UUID

class RolePermission(BaseModel):
    role_id: UUID
    permission_id: UUID

    class Config:
        from_attributes = True

# ==================== PROGRAM SCHEMAS ====================

class ProgramBase(BaseModel):
    organization_id: UUID
    code: str
    description: Optional[str] = None

class ProgramCreate(ProgramBase):
    pass

class ProgramUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None

class Program(ProgramBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== CAMPAIGN SCHEMAS ====================

class CampaignBase(BaseModel):
    organization_id: UUID
    code: str
    start_date: Optional[date] = None
    goal_amount: Optional[float] = None
    status: Optional[str] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    code: Optional[str] = None
    start_date: Optional[date] = None
    goal_amount: Optional[float] = None
    status: Optional[str] = None

class Campaign(CampaignBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== DONATION SCHEMAS ====================

class DonationBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    tribute_party_id: Optional[UUID] = None
    appeal_package_id: Optional[UUID] = None
    received_date: datetime
    intent_amount: float
    currency: str
    match_eligible: Optional[bool] = False
    memo: Optional[str] = None

class DonationCreate(DonationBase):
    pass

class DonationUpdate(BaseModel):
    received_date: Optional[datetime] = None
    intent_amount: Optional[float] = None
    ack_status: Optional[str] = None
    memo: Optional[str] = None

class Donation(DonationBase):
    id: UUID
    ack_status: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== PAYMENT SCHEMAS ====================

class PaymentBase(BaseModel):
    organization_id: UUID
    donation_id: UUID
    payment_date: datetime
    amount: float
    currency: str
    method: str
    gateway_ref: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    gateway_ref: Optional[str] = None

class Payment(PaymentBase):
    id: UUID
    status: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== PARTY SCHEMAS ====================

class PartyBase(BaseModel):
    organization_id: UUID
    type: str  # individual or organization
    display_name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    dob: Optional[date] = None
    ein: Optional[str] = None
    tax_id: Optional[str] = None

class PartyCreate(PartyBase):
    pass

class PartyUpdate(BaseModel):
    display_name: Optional[str] = None
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    dob: Optional[date] = None

class Party(PartyBase):
    id: UUID
    is_deleted: bool
    created_updated_at: datetime

    class Config:
        from_attributes = True

# ==================== PLEDGE SCHEMAS ====================

class PledgeBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    pledge_date: date
    total_amount: float
    frequency: Optional[str] = None
    schedule: Optional[str] = None

class PledgeCreate(PledgeBase):
    pass

class PledgeUpdate(BaseModel):
    total_amount: Optional[float] = None
    frequency: Optional[str] = None
    schedule: Optional[str] = None

class Pledge(PledgeBase):
    id: UUID
    start_end: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== PLEDGE_INSTALLMENT SCHEMAS ====================

class PledgeInstallmentBase(BaseModel):
    organization_id: UUID
    pledge_id: UUID
    due_date: date
    due_amount: float

class PledgeInstallmentCreate(PledgeInstallmentBase):
    pass

class PledgeInstallmentUpdate(BaseModel):
    paid_payment_id: Optional[UUID] = None

class PledgeInstallment(PledgeInstallmentBase):
    id: UUID
    paid_payment_id: Optional[UUID] = None

    class Config:
        from_attributes = True

# ==================== FUND SCHEMAS ====================

class FundBase(BaseModel):
    organization_id: UUID
    name: str
    restriction: Optional[str] = None
    program_id: Optional[UUID] = None

class FundCreate(FundBase):
    pass

class FundUpdate(BaseModel):
    name: Optional[str] = None
    restriction: Optional[str] = None
    program_id: Optional[UUID] = None

class Fund(FundBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== BENEFICIARY SCHEMAS ====================

class BeneficiaryBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    external_id: Optional[str] = None
    pii_level: Optional[str] = None

class BeneficiaryCreate(BeneficiaryBase):
    pass

class BeneficiaryUpdate(BaseModel):
    external_id: Optional[str] = None
    pii_level: Optional[str] = None

class Beneficiary(BeneficiaryBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== SERVICE_EVENT SCHEMAS ====================

class ServiceEventBase(BaseModel):
    organization_id: UUID
    program_id: UUID
    date: date
    location: Optional[str] = None
    units_delivered: Optional[float] = None
    notes: Optional[str] = None

class ServiceEventCreate(ServiceEventBase):
    pass

class ServiceEventUpdate(BaseModel):
    date: Optional[date] = None
    location: Optional[str] = None
    units_delivered: Optional[float] = None
    notes: Optional[str] = None

class ServiceEvent(ServiceEventBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== SERVICE_BENEFICIARY SCHEMAS ====================

class ServiceBeneficiaryCreate(BaseModel):
    service_event_id: UUID
    beneficiary_id: UUID
    role: Optional[str] = None

class ServiceBeneficiary(BaseModel):
    service_event_id: UUID
    beneficiary_id: UUID
    role: Optional[str] = None

    class Config:
        from_attributes = True

# ==================== OUTCOME_METRIC SCHEMAS ====================

class OutcomeMetricBase(BaseModel):
    organization_id: UUID
    program_id: UUID
    name: str
    unit: Optional[str] = None
    direction: Optional[str] = None
    target_value: Optional[float] = None

class OutcomeMetricCreate(OutcomeMetricBase):
    pass

class OutcomeMetricUpdate(BaseModel):
    name: Optional[str] = None
    unit: Optional[str] = None
    direction: Optional[str] = None
    target_value: Optional[float] = None

class OutcomeMetric(OutcomeMetricBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== OUTCOME_RECORD SCHEMAS ====================

class OutcomeRecordBase(BaseModel):
    organization_id: UUID
    outcome_metric_id: UUID
    value: float
    source: Optional[str] = None

class OutcomeRecordCreate(OutcomeRecordBase):
    pass

class OutcomeRecord(OutcomeRecordBase):
    id: UUID
    recorded_at: datetime

    class Config:
        from_attributes = True

# ==================== RECURRING_GIFT SCHEMAS ====================

class RecurringGiftBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    amount: float
    currency: str
    frequency_amount_count: Optional[int] = None
    next_charge_on: Optional[date] = None
    payment_method_id: Optional[UUID] = None

class RecurringGiftCreate(RecurringGiftBase):
    pass

class RecurringGiftUpdate(BaseModel):
    amount: Optional[float] = None
    frequency_amount_count: Optional[int] = None
    next_charge_on: Optional[date] = None
    payment_method_id: Optional[UUID] = None

class RecurringGift(RecurringGiftBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== PAYMENT_METHOD SCHEMAS ====================

class PaymentMethodBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    method: str
    token_ref: Optional[str] = None
    exp_mo_yr: Optional[str] = None
    is_default: Optional[bool] = False

class PaymentMethodCreate(PaymentMethodBase):
    pass

class PaymentMethodUpdate(BaseModel):
    token_ref: Optional[str] = None
    exp_mo_yr: Optional[str] = None
    is_default: Optional[bool] = None

class PaymentMethod(PaymentMethodBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== SOFT_CREDIT SCHEMAS ====================

class SoftCreditBase(BaseModel):
    organization_id: UUID
    donation_id: UUID
    influencer_party_id: UUID
    amount: float
    reason: Optional[str] = None
    notes: Optional[str] = None

class SoftCreditCreate(SoftCreditBase):
    pass

class SoftCredit(SoftCreditBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== MATCHING_CLAIM SCHEMAS ====================

class MatchingClaimBase(BaseModel):
    organization_id: UUID
    donation_id: UUID
    matcher_party_id: UUID
    status: Optional[str] = None
    paid_payment_id: Optional[UUID] = None

class MatchingClaimCreate(MatchingClaimBase):
    pass

class MatchingClaimUpdate(BaseModel):
    status: Optional[str] = None
    paid_payment_id: Optional[UUID] = None

class MatchingClaim(MatchingClaimBase):
    id: UUID
    submitted_at: datetime

    class Config:
        from_attributes = True

# ==================== DONATION_LINE SCHEMAS ====================

class DonationLineBase(BaseModel):
    organization_id: UUID
    donation_id: UUID
    program_id: UUID
    amount: float

class DonationLineCreate(DonationLineBase):
    pass

class DonationLine(DonationLineBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== CONTACT_POINT SCHEMAS ====================

class ContactPointBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    type: str
    channel: str
    value: str
    is_primary: Optional[bool] = False

class ContactPointCreate(ContactPointBase):
    pass

class ContactPointUpdate(BaseModel):
    value: Optional[str] = None
    is_primary: Optional[bool] = None

class ContactPoint(ContactPointBase):
    id: UUID
    verified_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== ADDRESS SCHEMAS ====================

class AddressBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    addr_lines: Optional[str] = None
    city_region: Optional[str] = None
    postal_country: Optional[str] = None
    is_primary: Optional[bool] = False
    valid_from_to: Optional[str] = None

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    addr_lines: Optional[str] = None
    city_region: Optional[str] = None
    postal_country: Optional[str] = None
    is_primary: Optional[bool] = None
    valid_from_to: Optional[str] = None

class Address(AddressBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== PARTY_ROLE SCHEMAS ====================

class PartyRoleCreate(BaseModel):
    party_id: UUID
    role_code: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class PartyRole(BaseModel):
    party_id: UUID
    role_code: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        from_attributes = True

# ==================== APPEAL SCHEMAS ====================

class AppealBase(BaseModel):
    organization_id: UUID
    campaign_id: UUID
    code: str
    channel: Optional[str] = None
    start_end: Optional[str] = None

class AppealCreate(AppealBase):
    pass

class AppealUpdate(BaseModel):
    code: Optional[str] = None
    channel: Optional[str] = None
    start_end: Optional[str] = None

class Appeal(AppealBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== PACKAGE SCHEMAS ====================

class PackageBase(BaseModel):
    organization_id: UUID
    appeal_id: UUID
    code: str
    cost_per_unit: Optional[float] = None
    audience_size: Optional[int] = None

class PackageCreate(PackageBase):
    pass

class PackageUpdate(BaseModel):
    code: Optional[str] = None
    cost_per_unit: Optional[float] = None
    audience_size: Optional[int] = None

class Package(PackageBase):
    id: UUID

    class Config:
        from_attributes = True

# ==================== CONSENT SCHEMAS ====================

class ConsentBase(BaseModel):
    organization_id: UUID
    party_id: UUID
    channel: str
    status: str
    opt_in_basis: Optional[str] = None
    captured_at_by: Optional[str] = None
    source: Optional[str] = None

class ConsentCreate(ConsentBase):
    pass

class ConsentUpdate(BaseModel):
    status: Optional[str] = None
    opt_in_basis: Optional[str] = None
    source: Optional[str] = None

class Consent(ConsentBase):
    id: UUID

    class Config:
        from_attributes = True