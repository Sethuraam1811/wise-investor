# models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    legal_name = Column(String, nullable=False)
    ein = Column(String, unique=True, nullable=False)
    timezone = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    programs = relationship("Program", back_populates="organization")
    campaigns = relationship("Campaign", back_populates="organization")
    parties = relationship("Party", back_populates="organization")
    donations = relationship("Donation", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    roles = relationship("UserRole", back_populates="user")

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)

    # Relationships
    users = relationship("UserRole", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text)

    # Relationships
    roles = relationship("RolePermission", back_populates="permission")

class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

class Program(Base):
    __tablename__ = "programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    code = Column(String, nullable=False)
    description = Column(Text)

    # Relationships
    organization = relationship("Organization", back_populates="programs")
    service_events = relationship("ServiceEvent", back_populates="program")
    outcome_metrics = relationship("OutcomeMetric", back_populates="program")
    funds = relationship("Fund", back_populates="program")

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    code = Column(String, nullable=False)
    start_date = Column(Date)
    goal_amount = Column(Float)
    status = Column(String)

    # Relationships
    organization = relationship("Organization", back_populates="campaigns")
    appeals = relationship("Appeal", back_populates="campaign")

class Donation(Base):
    __tablename__ = "donations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    tribute_party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"))
    appeal_package_id = Column(UUID(as_uuid=True), ForeignKey("packages.id"))
    received_date = Column(DateTime, nullable=False)
    intent_amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    match_eligible = Column(Boolean, default=False)
    ack_status = Column(String)
    memo = Column(Text)

    # Relationships
    organization = relationship("Organization", back_populates="donations")
    party = relationship("Party", foreign_keys=[party_id], back_populates="donations")
    tribute_party = relationship("Party", foreign_keys=[tribute_party_id])
    payments = relationship("Payment", back_populates="donation")
    donation_lines = relationship("DonationLine", back_populates="donation")
    soft_credits = relationship("SoftCredit", back_populates="donation")
    matching_claims = relationship("MatchingClaim", back_populates="donation")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    donation_id = Column(UUID(as_uuid=True), ForeignKey("donations.id"), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    method = Column(String, nullable=False)
    gateway_ref = Column(String)
    status = Column(String)

    # Relationships
    donation = relationship("Donation", back_populates="payments")

class Party(Base):
    __tablename__ = "parties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    type = Column(String, nullable=False)  # individual or organization
    display_name = Column(String, nullable=False)
    given_name = Column(String)
    family_name = Column(String)
    dob = Column(Date)
    ein = Column(String)
    tax_id = Column(String)
    is_deleted = Column(Boolean, default=False)
    created_updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="parties")
    donations = relationship("Donation", foreign_keys=[Donation.party_id], back_populates="party")
    pledges = relationship("Pledge", back_populates="party")
    recurring_gifts = relationship("RecurringGift", back_populates="party")
    payment_methods = relationship("PaymentMethod", back_populates="party")
    addresses = relationship("Address", back_populates="party")
    contact_points = relationship("ContactPoint", back_populates="party")
    beneficiary = relationship("Beneficiary", back_populates="party", uselist=False)

class Pledge(Base):
    __tablename__ = "pledges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    pledge_date = Column(Date, nullable=False)
    total_amount = Column(Float, nullable=False)
    frequency = Column(String)
    schedule = Column(String)
    start_end = Column(String)

    # Relationships
    party = relationship("Party", back_populates="pledges")
    installments = relationship("PledgeInstallment", back_populates="pledge")

class PledgeInstallment(Base):
    __tablename__ = "pledge_installments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    pledge_id = Column(UUID(as_uuid=True), ForeignKey("pledges.id"), nullable=False)
    due_date = Column(Date, nullable=False)
    due_amount = Column(Float, nullable=False)
    paid_payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"))

    # Relationships
    pledge = relationship("Pledge", back_populates="installments")

class Fund(Base):
    __tablename__ = "funds"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
    restriction = Column(String)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"))

    # Relationships
    program = relationship("Program", back_populates="funds")

class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    external_id = Column(String)
    pii_level = Column(String)

    # Relationships
    party = relationship("Party", back_populates="beneficiary")
    service_events = relationship("ServiceBeneficiary", back_populates="beneficiary")

class ServiceEvent(Base):
    __tablename__ = "service_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String)
    units_delivered = Column(Float)
    notes = Column(Text)

    # Relationships
    program = relationship("Program", back_populates="service_events")
    beneficiaries = relationship("ServiceBeneficiary", back_populates="service_event")

class ServiceBeneficiary(Base):
    __tablename__ = "service_beneficiaries"

    service_event_id = Column(UUID(as_uuid=True), ForeignKey("service_events.id"), primary_key=True)
    beneficiary_id = Column(UUID(as_uuid=True), ForeignKey("beneficiaries.id"), primary_key=True)
    role = Column(String)

    # Relationships
    service_event = relationship("ServiceEvent", back_populates="beneficiaries")
    beneficiary = relationship("Beneficiary", back_populates="service_events")

class OutcomeMetric(Base):
    __tablename__ = "outcome_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    name = Column(String, nullable=False)
    unit = Column(String)
    direction = Column(String)
    target_value = Column(Float)

    # Relationships
    program = relationship("Program", back_populates="outcome_metrics")
    records = relationship("OutcomeRecord", back_populates="outcome_metric")

class OutcomeRecord(Base):
    __tablename__ = "outcome_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    outcome_metric_id = Column(UUID(as_uuid=True), ForeignKey("outcome_metrics.id"), nullable=False)
    value = Column(Float, nullable=False)
    source = Column(String)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    outcome_metric = relationship("OutcomeMetric", back_populates="records")

class RecurringGift(Base):
    __tablename__ = "recurring_gifts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False)
    frequency_amount_count = Column(Integer)
    next_charge_on = Column(Date)
    payment_method_id = Column(UUID(as_uuid=True), ForeignKey("payment_methods.id"))

    # Relationships
    party = relationship("Party", back_populates="recurring_gifts")

class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    method = Column(String, nullable=False)
    token_ref = Column(String)
    exp_mo_yr = Column(String)
    is_default = Column(Boolean, default=False)

    # Relationships
    party = relationship("Party", back_populates="payment_methods")

class SoftCredit(Base):
    __tablename__ = "soft_credits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    donation_id = Column(UUID(as_uuid=True), ForeignKey("donations.id"), nullable=False)
    influencer_party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String)
    notes = Column(Text)

    # Relationships
    donation = relationship("Donation", back_populates="soft_credits")

class MatchingClaim(Base):
    __tablename__ = "matching_claims"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    donation_id = Column(UUID(as_uuid=True), ForeignKey("donations.id"), nullable=False)
    matcher_party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    paid_payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id"))

    # Relationships
    donation = relationship("Donation", back_populates="matching_claims")

class DonationLine(Base):
    __tablename__ = "donation_lines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    donation_id = Column(UUID(as_uuid=True), ForeignKey("donations.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    amount = Column(Float, nullable=False)

    # Relationships
    donation = relationship("Donation", back_populates="donation_lines")

class ContactPoint(Base):
    __tablename__ = "contact_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    type = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    value = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    verified_at = Column(DateTime)

    # Relationships
    party = relationship("Party", back_populates="contact_points")

class Address(Base):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    addr_lines = Column(Text)
    city_region = Column(String)
    postal_country = Column(String)
    is_primary = Column(Boolean, default=False)
    valid_from_to = Column(String)

    # Relationships
    party = relationship("Party", back_populates="addresses")

class PartyRole(Base):
    __tablename__ = "party_roles"

    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), primary_key=True)
    role_code = Column(String, primary_key=True)
    start_date = Column(Date)
    end_date = Column(Date)

class Appeal(Base):
    __tablename__ = "appeals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    code = Column(String, nullable=False)
    channel = Column(String)
    start_end = Column(String)

    # Relationships
    campaign = relationship("Campaign", back_populates="appeals")
    packages = relationship("Package", back_populates="appeal")

class Package(Base):
    __tablename__ = "packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    appeal_id = Column(UUID(as_uuid=True), ForeignKey("appeals.id"), nullable=False)
    code = Column(String, nullable=False)
    cost_per_unit = Column(Float)
    audience_size = Column(Integer)

    # Relationships
    appeal = relationship("Appeal", back_populates="packages")

class Consent(Base):
    __tablename__ = "consents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    party_id = Column(UUID(as_uuid=True), ForeignKey("parties.id"), nullable=False)
    channel = Column(String, nullable=False)
    status = Column(String, nullable=False)
    opt_in_basis = Column(String)
    captured_at_by = Column(String)
    source = Column(String)