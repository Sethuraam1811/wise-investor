
-- Nonprofit Platform - PostgreSQL Schema (DDL) and Sample Data (DML)
-- Compatible with PostgreSQL 13+
-- Run as a superuser (for CREATE EXTENSION) or remove those lines if already enabled.

BEGIN;

-- Extensions (for UUIDs and case-insensitive text if needed)
CREATE EXTENSION IF NOT EXISTS pgcrypto;  -- provides gen_random_uuid()

/* =====================
   ENUM TYPES
   ===================== */
CREATE TYPE party_type AS ENUM ('person','org');
CREATE TYPE party_role_code AS ENUM ('donor','volunteer','staff','funder','vendor','board');
CREATE TYPE address_kind AS ENUM ('home','work','billing','mailing');
CREATE TYPE contact_channel AS ENUM ('email','phone','sms','social');
CREATE TYPE consent_status AS ENUM ('opt_in','opt_out','unknown');
CREATE TYPE appeal_channel AS ENUM ('email','mail','event','digital','phone');
CREATE TYPE fund_restriction AS ENUM ('unrestricted','temporarily_restricted','permanently_restricted');
CREATE TYPE received_via AS ENUM ('online','check','cash','in_kind','wire');
CREATE TYPE payment_method_type AS ENUM ('card','ach','check','cash','wire','wallet','other');
CREATE TYPE payment_status AS ENUM ('settled','pending','failed','refunded');
CREATE TYPE pledge_schedule AS ENUM ('monthly','quarterly','annual','custom');
CREATE TYPE installment_status AS ENUM ('due','paid','late');
CREATE TYPE interval_unit AS ENUM ('week','month','year');
CREATE TYPE soft_credit_reason AS ENUM ('peer_to_peer','in_honor','solicitor');
CREATE TYPE matching_claim_status AS ENUM ('submitted','approved','denied','paid');
CREATE TYPE pii_level AS ENUM ('none','low','high');
CREATE TYPE service_role AS ENUM ('recipient','household');
CREATE TYPE metric_direction AS ENUM ('increase','decrease');

/* =====================
   CORE / ORGANIZATION
   ===================== */
CREATE TABLE organization (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  legal_name TEXT NOT NULL,
  ein TEXT,
  timezone TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE "user" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  email CITEXT NOT NULL,
  password_hash TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_login_at TIMESTAMPTZ
);
CREATE UNIQUE INDEX ux_user_org_email ON "user"(organization_id, email);

CREATE TABLE role (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  name TEXT NOT NULL
);
CREATE UNIQUE INDEX ux_role_org_name ON role(organization_id, name);

CREATE TABLE permission (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,
  description TEXT
);

CREATE TABLE user_role (
  user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  role_id UUID NOT NULL REFERENCES role(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

CREATE TABLE role_permission (
  role_id UUID NOT NULL REFERENCES role(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL REFERENCES permission(id) ON DELETE CASCADE,
  PRIMARY KEY (role_id, permission_id)
);

/* =====================
   MEMBER / PARTY
   ===================== */
CREATE TABLE party (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  type party_type NOT NULL,
  display_name TEXT NOT NULL,
  given_name TEXT,
  family_name TEXT,
  org_name TEXT,
  date_of_birth DATE,
  tax_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX ix_party_org ON party(organization_id);
CREATE INDEX ix_party_name ON party(display_name);

CREATE TABLE party_role (
  party_id UUID NOT NULL REFERENCES party(id) ON DELETE CASCADE,
  role_code party_role_code NOT NULL,
  start_date DATE,
  end_date DATE,
  PRIMARY KEY (party_id, role_code, start_date)
);

CREATE TABLE address (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  party_id UUID NOT NULL REFERENCES party(id) ON DELETE CASCADE,
  kind address_kind NOT NULL,
  line1 TEXT NOT NULL,
  line2 TEXT,
  line3 TEXT,
  city TEXT NOT NULL,
  region TEXT,
  postal_code TEXT,
  country TEXT NOT NULL,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  valid_from DATE,
  valid_to DATE
);
CREATE INDEX ix_address_party ON address(party_id);

CREATE TABLE contact_point (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  party_id UUID NOT NULL REFERENCES party(id) ON DELETE CASCADE,
  channel contact_channel NOT NULL,
  value TEXT NOT NULL,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  verified_at TIMESTAMPTZ
);
CREATE INDEX ix_contact_point_party ON contact_point(party_id);
CREATE UNIQUE INDEX ux_contact_primary_unique ON contact_point (party_id, channel) WHERE is_primary;

CREATE TABLE consent (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  party_id UUID NOT NULL REFERENCES party(id) ON DELETE CASCADE,
  channel contact_channel NOT NULL,
  status consent_status NOT NULL,
  legal_basis TEXT,
  captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  captured_by UUID,
  source TEXT
);
CREATE INDEX ix_consent_party_channel ON consent(party_id, channel);

/* =====================
   CAMPAIGN / FUNDRAISING SETUP
   ===================== */
CREATE TABLE campaign (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  start_date DATE,
  end_date DATE,
  goal_amount NUMERIC(14,2),
  status TEXT
);
CREATE UNIQUE INDEX ux_campaign_org_code ON campaign(organization_id, code);

CREATE TABLE appeal (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  campaign_id UUID NOT NULL REFERENCES campaign(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  channel appeal_channel NOT NULL,
  start_date DATE,
  end_date DATE
);
CREATE UNIQUE INDEX ux_appeal_org_code ON appeal(organization_id, code);

CREATE TABLE package (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  appeal_id UUID NOT NULL REFERENCES appeal(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  cost_per_unit NUMERIC(12,4),
  audience_size INTEGER
);
CREATE UNIQUE INDEX ux_package_org_code ON package(organization_id, code);

CREATE TABLE fund (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  restriction fund_restriction NOT NULL,
  program_id UUID NULL REFERENCES program(id)  -- forward ref, will add FK after program table creation
);
-- defer FK for program; we'll attach after program is created
CREATE UNIQUE INDEX ux_fund_org_code ON fund(organization_id, code);

/* =====================
   DONATION / PAYMENTS
   ===================== */
CREATE TABLE donation (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  donor_party_id UUID NOT NULL REFERENCES party(id) ON DELETE RESTRICT,
  tribute_for_party_id UUID NULL REFERENCES party(id) ON DELETE SET NULL,
  appeal_id UUID NULL REFERENCES appeal(id) ON DELETE SET NULL,
  package_id UUID NULL REFERENCES package(id) ON DELETE SET NULL,
  donation_date DATE NOT NULL,
  intent_amount NUMERIC(12,2) NOT NULL CHECK (intent_amount >= 0),
  currency CHAR(3) NOT NULL,
  received_via received_via NOT NULL,
  acknowledgement_status TEXT,
  memo TEXT
);
CREATE INDEX ix_donation_org_date ON donation(organization_id, donation_date);
CREATE INDEX ix_donation_donor ON donation(donor_party_id);

CREATE TABLE donation_line (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  donation_id UUID NOT NULL REFERENCES donation(id) ON DELETE CASCADE,
  fund_id UUID NOT NULL REFERENCES fund(id) ON DELETE RESTRICT,
  amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  program_id UUID NULL REFERENCES program(id) ON DELETE SET NULL,
  notes TEXT
);
CREATE INDEX ix_donation_line_donation ON donation_line(donation_id);
CREATE INDEX ix_donation_line_fund ON donation_line(fund_id);

CREATE TABLE payment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  donation_id UUID NOT NULL REFERENCES donation(id) ON DELETE CASCADE,
  payment_date TIMESTAMPTZ NOT NULL,
  amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  currency CHAR(3) NOT NULL,
  method payment_method_type NOT NULL,
  external_ref TEXT,
  status payment_status NOT NULL
);
CREATE INDEX ix_payment_donation ON payment(donation_id);
CREATE INDEX ix_payment_status ON payment(status);

CREATE TABLE payment_method (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  party_id UUID NOT NULL REFERENCES party(id) ON DELETE CASCADE,
  method payment_method_type NOT NULL,
  token_ref TEXT,
  last4 TEXT,
  expiry_month INTEGER CHECK (expiry_month BETWEEN 1 AND 12),
  expiry_year INTEGER,
  is_default BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX ix_payment_method_party ON payment_method(party_id);

/* =====================
   PLEDGE / RECURRING / CREDITS / MATCHING
   ===================== */
CREATE TABLE pledge (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  donor_party_id UUID NOT NULL REFERENCES party(id) ON DELETE RESTRICT,
  pledge_date DATE NOT NULL,
  total_amount NUMERIC(12,2) NOT NULL CHECK (total_amount >= 0),
  currency CHAR(3) NOT NULL,
  schedule pledge_schedule NOT NULL,
  start_date DATE,
  end_date DATE,
  status TEXT
);
CREATE INDEX ix_pledge_donor ON pledge(donor_party_id);

CREATE TABLE pledge_installment (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  pledge_id UUID NOT NULL REFERENCES pledge(id) ON DELETE CASCADE,
  due_date DATE NOT NULL,
  due_amount NUMERIC(12,2) NOT NULL CHECK (due_amount >= 0),
  status installment_status NOT NULL,
  paid_payment_id UUID NULL REFERENCES payment(id) ON DELETE SET NULL
);
CREATE INDEX ix_pli_pledge ON pledge_installment(pledge_id);

CREATE TABLE recurring_gift (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  donor_party_id UUID NOT NULL REFERENCES party(id) ON DELETE RESTRICT,
  amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
  currency CHAR(3) NOT NULL,
  interval_unit interval_unit NOT NULL,
  interval_count INTEGER NOT NULL CHECK (interval_count > 0),
  next_charge_on DATE,
  payment_method_id UUID NOT NULL REFERENCES payment_method(id) ON DELETE RESTRICT,
  active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX ix_recurring_donor ON recurring_gift(donor_party_id);

CREATE TABLE soft_credit (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  donation_id UUID NOT NULL REFERENCES donation(id) ON DELETE CASCADE,
  influencer_party_id UUID NOT NULL REFERENCES party(id) ON DELETE RESTRICT,
  amount NUMERIC(12,2) NOT NULL CHECK (amount >= 0),
  reason soft_credit_reason NOT NULL,
  notes TEXT
);
CREATE INDEX ix_soft_credit_donation ON soft_credit(donation_id);

CREATE TABLE matching_claim (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  donation_id UUID NOT NULL REFERENCES donation(id) ON DELETE CASCADE,
  employer_party_id UUID NOT NULL REFERENCES party(id) ON DELETE RESTRICT,
  submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  status matching_claim_status NOT NULL,
  paid_payment_id UUID NULL REFERENCES payment(id) ON DELETE SET NULL
);
CREATE INDEX ix_matching_claim_donation ON matching_claim(donation_id);

/* =====================
   PROGRAMS / EVENTS / OUTCOMES
   ===================== */
CREATE TABLE program (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  description TEXT,
  active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE UNIQUE INDEX ux_program_org_code ON program(organization_id, code);

-- Now attach deferred FK from fund.program_id -> program.id
ALTER TABLE fund
  ADD CONSTRAINT fund_program_fk
  FOREIGN KEY (program_id) REFERENCES program(id) ON DELETE SET NULL;

CREATE TABLE beneficiary (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  party_id UUID NULL REFERENCES party(id) ON DELETE SET NULL,
  external_id TEXT,
  cohort_key TEXT,
  pii_level pii_level NOT NULL DEFAULT 'low'
);
CREATE UNIQUE INDEX ux_beneficiary_org_external ON beneficiary(organization_id, external_id);

CREATE TABLE service_event (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  program_id UUID NOT NULL REFERENCES program(id) ON DELETE CASCADE,
  occurred_at TIMESTAMPTZ NOT NULL,
  location TEXT,
  units_delivered NUMERIC(12,2),
  unit_type TEXT,
  notes TEXT
);
CREATE INDEX ix_service_event_program ON service_event(program_id);

CREATE TABLE service_beneficiary (
  service_event_id UUID NOT NULL REFERENCES service_event(id) ON DELETE CASCADE,
  beneficiary_id UUID NOT NULL REFERENCES beneficiary(id) ON DELETE CASCADE,
  role service_role NOT NULL,
  PRIMARY KEY (service_event_id, beneficiary_id)
);

CREATE TABLE outcome_metric (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  program_id UUID NOT NULL REFERENCES program(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  unit TEXT NOT NULL,
  direction metric_direction NOT NULL,
  target_value NUMERIC(12,2)
);
CREATE UNIQUE INDEX ux_metric_org_code ON outcome_metric(organization_id, code);

CREATE TABLE outcome_record (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,
  outcome_metric_id UUID NOT NULL REFERENCES outcome_metric(id) ON DELETE CASCADE,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  value NUMERIC(12,2) NOT NULL,
  source TEXT,
  collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ix_outcome_record_metric_period ON outcome_record(outcome_metric_id, period_start, period_end);

/* =====================
   SAMPLE DATA (DML)
   ===================== */
-- Organization & RBAC
INSERT INTO organization (id, legal_name, ein, timezone, status)
VALUES ('00000000-0000-0000-0000-000000000001','Helping Hands Foundation','12-3456789','America/Chicago','active');

INSERT INTO "user"(id, organization_id, email, password_hash, status)
VALUES ('00000000-0000-0000-0000-000000000101','00000000-0000-0000-0000-000000000001','admin@helpinghands.org','$2y$hash','active');

INSERT INTO role (id, organization_id, name)
VALUES ('00000000-0000-0000-0000-000000000201','00000000-0000-0000-0000-000000000001','admin');

INSERT INTO permission (id, code, description)
VALUES ('00000000-0000-0000-0000-000000000301','donation.read','Read donations');

INSERT INTO user_role (user_id, role_id)
VALUES ('00000000-0000-0000-0000-000000000101','00000000-0000-0000-0000-000000000201');

INSERT INTO role_permission (role_id, permission_id)
VALUES ('00000000-0000-0000-0000-000000000201','00000000-0000-0000-0000-000000000301');

-- Parties
INSERT INTO party (id, organization_id, type, display_name, given_name, family_name)
VALUES 
('00000000-0000-0000-0000-000000001001','00000000-0000-0000-0000-000000000001','person','Sam Lee','Sam','Lee'),
('00000000-0000-0000-0000-000000001002','00000000-0000-0000-0000-000000000001','org','Acme Corp',NULL,NULL,'Acme Corp');

INSERT INTO party_role (party_id, role_code, start_date)
VALUES ('00000000-0000-0000-0000-000000001001','donor','2025-01-01');

INSERT INTO address (organization_id, party_id, kind, line1, city, region, postal_code, country, is_primary)
VALUES ('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000001001','billing','123 Elm St','Dallas','TX','75001','US',true);

INSERT INTO contact_point (organization_id, party_id, channel, value, is_primary)
VALUES ('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000001001','email','sam.lee@example.com',true);

INSERT INTO consent (organization_id, party_id, channel, status, legal_basis, source)
VALUES ('00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000001001','email','opt_in','explicit_consent','web_form');

-- Campaign setup
INSERT INTO campaign (id, organization_id, name, code, start_date, end_date, goal_amount, status)
VALUES ('00000000-0000-0000-0000-000000002001','00000000-0000-0000-0000-000000000001','UTD Alumni Drive','ALUMNI25','2025-10-01','2025-12-31',500000,'active');

INSERT INTO appeal (id, organization_id, campaign_id, name, code, channel, start_date)
VALUES ('00000000-0000-0000-0000-000000002101','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000002001','Email Blast #1','EM1','email','2025-10-10');

INSERT INTO package (id, organization_id, appeal_id, name, code, cost_per_unit, audience_size)
VALUES ('00000000-0000-0000-0000-000000002201','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000002101','Segment A','SEG_A',0.02,25000);

-- Programs & funds
INSERT INTO program (id, organization_id, name, code, description)
VALUES ('00000000-0000-0000-0000-000000004001','00000000-0000-0000-0000-000000000001','STEM Tutoring','STEM','After-school tutoring');

INSERT INTO fund (id, organization_id, name, code, restriction, program_id)
VALUES 
('00000000-0000-0000-0000-000000003001','00000000-0000-0000-0000-000000000001','Unrestricted Operating','UNR','unrestricted',NULL),
('00000000-0000-0000-0000-000000003002','00000000-0000-0000-0000-000000000001','Scholarships','SCH','temporarily_restricted','00000000-0000-0000-0000-000000004001');

-- Payment methods
INSERT INTO payment_method (id, organization_id, party_id, method, token_ref, last4, expiry_month, expiry_year, is_default)
VALUES ('00000000-0000-0000-0000-000000005001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000001001','card','tok_visa','4242',12,2027,true);

-- Donation with lines & payment
INSERT INTO donation (id, organization_id, donor_party_id, appeal_id, package_id, donation_date, intent_amount, currency, received_via, acknowledgement_status, memo)
VALUES ('00000000-0000-0000-0000-000000006001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000001001','00000000-0000-0000-0000-000000002101','00000000-0000-0000-0000-000000002201','2025-10-06',250.00,'USD','online','pending','In honor of Prof. Shah');

INSERT INTO donation_line (id, organization_id, donation_id, fund_id, amount, program_id, notes)
VALUES 
('00000000-0000-0000-0000-000000006101','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000006001','00000000-0000-0000-0000-000000003001',200.00,NULL,NULL),
('00000000-0000-0000-0000-000000006102','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000006001','00000000-0000-0000-0000-000000003002',50.00,'00000000-0000-0000-0000-000000004001','Scholarship allocation');

INSERT INTO payment (id, organization_id, donation_id, payment_date, amount, currency, method, external_ref, status)
VALUES ('00000000-0000-0000-0000-000000006201','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000006001','2025-10-06T18:40:00Z',250.00,'USD','card','ch_1NvABCDE','settled');

-- Pledge & installment
INSERT INTO pledge (id, organization_id, donor_party_id, pledge_date, total_amount, currency, schedule, start_date, end_date, status)
VALUES ('00000000-0000-0000-0000-000000007001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000001001','2025-10-01',1200.00,'USD','monthly','2025-11-01','2026-10-31','active');

INSERT INTO pledge_installment (id, organization_id, pledge_id, due_date, due_amount, status, paid_payment_id)
VALUES ('00000000-0000-0000-0000-000000007101','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000007001','2025-11-01',100.00,'due',NULL);

-- Recurring gift
INSERT INTO recurring_gift (id, organization_id, donor_party_id, amount, currency, interval_unit, interval_count, next_charge_on, payment_method_id, active)
VALUES ('00000000-0000-0000-0000-000000008001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000001001',50.00,'USD','month',1,'2025-11-01','00000000-0000-0000-0000-000000005001',true);

-- Soft credit & matching
INSERT INTO soft_credit (id, organization_id, donation_id, influencer_party_id, amount, reason, notes)
VALUES ('00000000-0000-0000-0000-000000009001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000006001','00000000-0000-0000-0000-000000001002',250.00,'in_honor','Corporate match expected');

INSERT INTO matching_claim (id, organization_id, donation_id, employer_party_id, submitted_at, status, paid_payment_id)
VALUES ('00000000-0000-0000-0000-000000009101','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000006001','00000000-0000-0000-0000-000000001002',NOW(),'submitted',NULL);

-- Beneficiaries, events, outcomes
INSERT INTO beneficiary (id, organization_id, party_id, external_id, cohort_key, pii_level)
VALUES ('00000000-0000-0000-0000-00000000A001','00000000-0000-0000-0000-000000000001',NULL,'EXT-99001','fall-2025','low');

INSERT INTO service_event (id, organization_id, program_id, occurred_at, location, units_delivered, unit_type, notes)
VALUES ('00000000-0000-0000-0000-00000000B001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000004001','2025-10-05T16:00:00Z','Dallas, TX',3,'hours','Math tutoring');

INSERT INTO service_beneficiary (service_event_id, beneficiary_id, role)
VALUES ('00000000-0000-0000-0000-00000000B001','00000000-0000-0000-0000-00000000A001','recipient');

INSERT INTO outcome_metric (id, organization_id, program_id, name, code, unit, direction, target_value)
VALUES ('00000000-0000-0000-0000-00000000C001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-000000004001','Math proficiency','MATH_PROF','percent','increase',80);

INSERT INTO outcome_record (id, organization_id, outcome_metric_id, period_start, period_end, value, source)
VALUES ('00000000-0000-0000-0000-00000000D001','00000000-0000-0000-0000-000000000001','00000000-0000-0000-0000-00000000C001','2025-09-01','2025-09-30',62,'assessment');

COMMIT;
