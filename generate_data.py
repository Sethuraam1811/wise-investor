# generate_data.py
"""
Database Test Data Generator
Generates 500+ rows of realistic test data for all tables
"""

from faker import Faker
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import uuid

fake = Faker()
Faker.seed(12345)
random.seed(12345)

def generate_data():
    db = SessionLocal()

    try:
        print("🚀 Starting data generation...")
        print("=" * 60)

        # Clear existing data (optional - comment out if you want to keep existing data)
        print("🗑️  Clearing existing data...")
        db.query(models.DonationLine).delete()
        db.query(models.MatchingClaim).delete()
        db.query(models.SoftCredit).delete()
        db.query(models.Payment).delete()
        db.query(models.Donation).delete()
        db.query(models.PledgeInstallment).delete()
        db.query(models.Pledge).delete()
        db.query(models.RecurringGift).delete()
        db.query(models.ServiceBeneficiary).delete()
        db.query(models.ServiceEvent).delete()
        db.query(models.OutcomeRecord).delete()
        db.query(models.OutcomeMetric).delete()
        db.query(models.Beneficiary).delete()
        db.query(models.Consent).delete()
        db.query(models.Package).delete()
        db.query(models.Appeal).delete()
        db.query(models.PartyRole).delete()
        db.query(models.Address).delete()
        db.query(models.ContactPoint).delete()
        db.query(models.PaymentMethod).delete()
        db.query(models.Party).delete()
        db.query(models.Fund).delete()
        db.query(models.Campaign).delete()
        db.query(models.Program).delete()
        db.query(models.RolePermission).delete()
        db.query(models.UserRole).delete()
        db.query(models.Permission).delete()
        db.query(models.Role).delete()
        db.query(models.User).delete()
        db.query(models.Organization).delete()
        db.commit()
        print("✅ Cleared existing data")

        # 1. Organizations (10)
        print("\n📊 Creating Organizations...")
        organizations = []
        org_types = ["Nonprofit", "Foundation", "Charity", "NGO", "Association"]

        for i in range(10):
            org = models.Organization(
                id=uuid.uuid4(),
                legal_name=f"{fake.company()} {random.choice(org_types)}",
                ein=f"{random.randint(10,99)}-{random.randint(1000000,9999999)}",
                timezone=random.choice(["America/New_York", "America/Chicago", "America/Los_Angeles", "America/Denver"]),
                status=random.choice(["active", "active", "active", "inactive"]),
                created_at=fake.date_time_between(start_date="-5y", end_date="now")
            )
            organizations.append(org)
            db.add(org)

        db.commit()
        print(f"✅ Created {len(organizations)} organizations")

        # 2. Permissions (20)
        print("\n🔐 Creating Permissions...")
        permissions = []
        permission_codes = [
            "org.read", "org.write", "org.delete", "org.admin",
            "user.read", "user.write", "user.delete", "user.admin",
            "donation.read", "donation.write", "donation.delete", "donation.admin",
            "report.read", "report.write", "report.admin",
            "program.read", "program.write", "program.delete",
            "campaign.read", "campaign.write"
        ]

        for code in permission_codes:
            perm = models.Permission(
                id=uuid.uuid4(),
                code=code,
                description=f"Permission to {code.split('.')[1]} {code.split('.')[0]}"
            )
            permissions.append(perm)
            db.add(perm)

        db.commit()
        print(f"✅ Created {len(permissions)} permissions")

        # 3. Roles (30)
        print("\n👥 Creating Roles...")
        roles = []
        role_names = ["Admin", "Manager", "User", "Donor Manager", "Program Director",
                      "Finance Manager", "Volunteer Coordinator", "Board Member"]

        for org in organizations:
            for role_name in random.sample(role_names, random.randint(3, 6)):
                role = models.Role(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    name=role_name
                )
                roles.append(role)
                db.add(role)

        db.commit()
        print(f"✅ Created {len(roles)} roles")

        # 4. Role Permissions (60)
        print("\n🔗 Creating Role-Permission mappings...")
        role_perms = []
        for role in roles:
            # Assign 3-8 random permissions to each role
            selected_perms = random.sample(permissions, random.randint(3, 8))
            for perm in selected_perms:
                rp = models.RolePermission(
                    role_id=role.id,
                    permission_id=perm.id
                )
                role_perms.append(rp)
                db.add(rp)

        db.commit()
        print(f"✅ Created {len(role_perms)} role-permission mappings")

        # 5. Users (50)
        print("\n👤 Creating Users...")
        users = []

        for i in range(50):
            org = random.choice(organizations)
            user = models.User(
                id=uuid.uuid4(),
                organization_id=org.id,
                email=fake.email(),
                password_hash=fake.sha256(),
                status=random.choice(["active", "active", "active", "inactive", "pending"]),
                created_at=fake.date_time_between(start_date="-3y", end_date="now"),
                last_login_at=fake.date_time_between(start_date="-30d", end_date="now") if random.random() > 0.2 else None
            )
            users.append(user)
            db.add(user)

        db.commit()
        print(f"✅ Created {len(users)} users")

        # 6. User Roles (70)
        print("\n🔗 Creating User-Role mappings...")
        user_roles = []
        for user in users:
            # Get roles for this user's organization
            org_roles = [r for r in roles if r.organization_id == user.organization_id]
            if org_roles:
                selected_roles = random.sample(org_roles, random.randint(1, min(3, len(org_roles))))
                for role in selected_roles:
                    ur = models.UserRole(
                        user_id=user.id,
                        role_id=role.id
                    )
                    user_roles.append(ur)
                    db.add(ur)

        db.commit()
        print(f"✅ Created {len(user_roles)} user-role mappings")

        # 7. Programs (40)
        print("\n📋 Creating Programs...")
        programs = []
        program_types = ["Education", "Healthcare", "Environment", "Community Development",
                         "Arts & Culture", "Youth Services", "Senior Services", "Food Bank"]

        for org in organizations:
            for i in range(random.randint(3, 5)):
                program = models.Program(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    code=f"PRG-{random.randint(1000, 9999)}",
                    description=f"{random.choice(program_types)} Program - {fake.catch_phrase()}"
                )
                programs.append(program)
                db.add(program)

        db.commit()
        print(f"✅ Created {len(programs)} programs")

        # 8. Campaigns (30)
        print("\n📢 Creating Campaigns...")
        campaigns = []

        for org in organizations:
            for i in range(random.randint(2, 4)):
                start_date = fake.date_between(start_date="-2y", end_date="+6m")
                campaign = models.Campaign(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    code=f"CAMP-{random.randint(1000, 9999)}",
                    start_date=start_date,
                    goal_amount=random.uniform(10000, 500000),
                    status=random.choice(["active", "active", "completed", "planned"])
                )
                campaigns.append(campaign)
                db.add(campaign)

        db.commit()
        print(f"✅ Created {len(campaigns)} campaigns")

        # 9. Appeals (50)
        print("\n📨 Creating Appeals...")
        appeals = []
        channels = ["email", "direct_mail", "phone", "social_media", "event"]

        for campaign in campaigns:
            for i in range(random.randint(1, 3)):
                appeal = models.Appeal(
                    id=uuid.uuid4(),
                    organization_id=campaign.organization_id,
                    campaign_id=campaign.id,
                    code=f"APP-{random.randint(1000, 9999)}",
                    channel=random.choice(channels),
                    start_end=f"{fake.date_this_year()} to {fake.date_this_year()}"
                )
                appeals.append(appeal)
                db.add(appeal)

        db.commit()
        print(f"✅ Created {len(appeals)} appeals")

        # 10. Packages (80)
        print("\n📦 Creating Packages...")
        packages = []

        for appeal in appeals:
            for i in range(random.randint(1, 2)):
                package = models.Package(
                    id=uuid.uuid4(),
                    organization_id=appeal.organization_id,
                    appeal_id=appeal.id,
                    code=f"PKG-{random.randint(1000, 9999)}",
                    cost_per_unit=random.uniform(0.5, 5.0),
                    audience_size=random.randint(100, 10000)
                )
                packages.append(package)
                db.add(package)

        db.commit()
        print(f"✅ Created {len(packages)} packages")

        # 11. Parties (200 - mix of individuals and organizations)
        print("\n🎭 Creating Parties (Donors/Beneficiaries)...")
        parties = []

        for org in organizations:
            # Create individual parties
            for i in range(random.randint(15, 25)):
                party = models.Party(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    type="individual",
                    display_name=fake.name(),
                    given_name=fake.first_name(),
                    family_name=fake.last_name(),
                    dob=fake.date_of_birth(minimum_age=18, maximum_age=90),
                    tax_id=f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}",
                    is_deleted=False,
                    created_updated_at=fake.date_time_between(start_date="-5y", end_date="now")
                )
                parties.append(party)
                db.add(party)

            # Create organizational parties
            for i in range(random.randint(3, 5)):
                party = models.Party(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    type="organization",
                    display_name=fake.company(),
                    ein=f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}",
                    is_deleted=False,
                    created_updated_at=fake.date_time_between(start_date="-5y", end_date="now")
                )
                parties.append(party)
                db.add(party)

        db.commit()
        print(f"✅ Created {len(parties)} parties")

        # 12. Contact Points (400)
        print("\n📞 Creating Contact Points...")
        contact_points = []
        contact_types = ["email", "phone", "mobile"]

        for party in parties:
            # Each party gets 1-3 contact points
            for i in range(random.randint(1, 3)):
                contact_type = random.choice(contact_types)
                if contact_type == "email":
                    value = fake.email()
                else:
                    value = fake.phone_number()

                cp = models.ContactPoint(
                    id=uuid.uuid4(),
                    organization_id=party.organization_id,
                    party_id=party.id,
                    type=contact_type,
                    channel=contact_type,
                    value=value,
                    is_primary=(i == 0),
                    verified_at=fake.date_time_between(start_date="-1y", end_date="now") if random.random() > 0.3 else None
                )
                contact_points.append(cp)
                db.add(cp)

        db.commit()
        print(f"✅ Created {len(contact_points)} contact points")

        # 13. Addresses (250)
        print("\n🏠 Creating Addresses...")
        addresses = []

        for party in parties:
            if random.random() > 0.2:  # 80% of parties have addresses
                address = models.Address(
                    id=uuid.uuid4(),
                    organization_id=party.organization_id,
                    party_id=party.id,
                    addr_lines=f"{fake.street_address()}\n{fake.secondary_address()}",
                    city_region=f"{fake.city()}, {fake.state_abbr()}",
                    postal_country=f"{fake.zipcode()}, USA",
                    is_primary=True,
                    valid_from_to=f"{fake.date_this_decade()} to present"
                )
                addresses.append(address)
                db.add(address)

        db.commit()
        print(f"✅ Created {len(addresses)} addresses")

        # 14. Payment Methods (150)
        print("\n💳 Creating Payment Methods...")
        payment_methods = []
        methods = ["credit_card", "debit_card", "bank_account", "paypal"]

        for party in parties:
            if random.random() > 0.3:  # 70% have payment methods
                pm = models.PaymentMethod(
                    id=uuid.uuid4(),
                    organization_id=party.organization_id,
                    party_id=party.id,
                    method=random.choice(methods),
                    token_ref=fake.sha256()[:16],
                    exp_mo_yr=f"{random.randint(1, 12):02d}/{random.randint(24, 29)}",
                    is_default=True
                )
                payment_methods.append(pm)
                db.add(pm)

        db.commit()
        print(f"✅ Created {len(payment_methods)} payment methods")

        # 15. Funds (50)
        print("\n💰 Creating Funds...")
        funds = []
        restrictions = ["unrestricted", "temporarily_restricted", "permanently_restricted"]

        for org in organizations:
            for i in range(random.randint(4, 6)):
                fund = models.Fund(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    name=f"{fake.bs().title()} Fund",
                    restriction=random.choice(restrictions),
                    program_id=random.choice([p.id for p in programs if p.organization_id == org.id]) if random.random() > 0.3 else None
                )
                funds.append(fund)
                db.add(fund)

        db.commit()
        print(f"✅ Created {len(funds)} funds")

        # 16. Donations (500)
        print("\n💝 Creating Donations...")
        donations = []
        currencies = ["USD", "USD", "USD", "EUR", "GBP"]

        for i in range(500):
            org = random.choice(organizations)
            party = random.choice([p for p in parties if p.organization_id == org.id])

            donation = models.Donation(
                id=uuid.uuid4(),
                organization_id=org.id,
                party_id=party.id,
                tribute_party_id=random.choice([p.id for p in parties if p.organization_id == org.id]) if random.random() > 0.9 else None,
                appeal_package_id=random.choice([pkg.id for pkg in packages if pkg.organization_id == org.id]) if packages and random.random() > 0.5 else None,
                received_date=fake.date_time_between(start_date="-2y", end_date="now"),
                intent_amount=random.uniform(10, 10000),
                currency=random.choice(currencies),
                match_eligible=random.choice([True, False, False]),
                ack_status=random.choice(["pending", "sent", "sent", "sent"]),
                memo=fake.sentence() if random.random() > 0.7 else None
            )
            donations.append(donation)
            db.add(donation)

        db.commit()
        print(f"✅ Created {len(donations)} donations")

        # 17. Payments (600)
        print("\n💵 Creating Payments...")
        payments = []
        payment_statuses = ["completed", "completed", "completed", "pending", "failed"]
        payment_methods_list = ["credit_card", "check", "cash", "wire_transfer", "paypal"]

        for donation in donations:
            # Most donations have 1 payment, some have multiple installments
            num_payments = 1 if random.random() > 0.2 else random.randint(2, 4)
            amount_per_payment = donation.intent_amount / num_payments

            for i in range(num_payments):
                payment = models.Payment(
                    id=uuid.uuid4(),
                    organization_id=donation.organization_id,
                    donation_id=donation.id,
                    payment_date=donation.received_date + timedelta(days=i*30),
                    amount=amount_per_payment,
                    currency=donation.currency,
                    method=random.choice(payment_methods_list),
                    gateway_ref=f"TXN-{fake.uuid4()[:8]}",
                    status=random.choice(payment_statuses)
                )
                payments.append(payment)
                db.add(payment)

        db.commit()
        print(f"✅ Created {len(payments)} payments")

        # 18. Donation Lines (600)
        print("\n📊 Creating Donation Lines...")
        donation_lines = []

        for donation in donations:
            # Split donation across 1-3 programs
            org_programs = [p for p in programs if p.organization_id == donation.organization_id]
            if org_programs:
                num_lines = random.randint(1, min(3, len(org_programs)))
                selected_programs = random.sample(org_programs, num_lines)
                amount_per_line = donation.intent_amount / num_lines

                for program in selected_programs:
                    dl = models.DonationLine(
                        id=uuid.uuid4(),
                        organization_id=donation.organization_id,
                        donation_id=donation.id,
                        program_id=program.id,
                        amount=amount_per_line
                    )
                    donation_lines.append(dl)
                    db.add(dl)

        db.commit()
        print(f"✅ Created {len(donation_lines)} donation lines")

        # 19. Pledges (100)
        print("\n🤝 Creating Pledges...")
        pledges = []
        frequencies = ["monthly", "quarterly", "annually", "one-time"]

        for i in range(100):
            org = random.choice(organizations)
            party = random.choice([p for p in parties if p.organization_id == org.id])

            pledge = models.Pledge(
                id=uuid.uuid4(),
                organization_id=org.id,
                party_id=party.id,
                pledge_date=fake.date_between(start_date="-1y", end_date="now"),
                total_amount=random.uniform(1000, 50000),
                frequency=random.choice(frequencies),
                schedule=f"Payments due on the 1st of the month",
                start_end=f"{fake.date_this_year()} to {fake.date_between(start_date='now', end_date='+2y')}"
            )
            pledges.append(pledge)
            db.add(pledge)

        db.commit()
        print(f"✅ Created {len(pledges)} pledges")

        # 20. Pledge Installments (300)
        print("\n📅 Creating Pledge Installments...")
        pledge_installments = []

        for pledge in pledges:
            # Create installments based on frequency
            num_installments = {"monthly": 12, "quarterly": 4, "annually": 1, "one-time": 1}
            num = num_installments.get(pledge.frequency, 1)
            amount_per_installment = pledge.total_amount / num

            for i in range(num):
                pi = models.PledgeInstallment(
                    id=uuid.uuid4(),
                    organization_id=pledge.organization_id,
                    pledge_id=pledge.id,
                    due_date=pledge.pledge_date + timedelta(days=30*i),
                    due_amount=amount_per_installment,
                    paid_payment_id=random.choice([p.id for p in payments if p.organization_id == pledge.organization_id]) if random.random() > 0.5 else None
                )
                pledge_installments.append(pi)
                db.add(pi)

        db.commit()
        print(f"✅ Created {len(pledge_installments)} pledge installments")

        # 21. Recurring Gifts (80)
        print("\n🔄 Creating Recurring Gifts...")
        recurring_gifts = []

        for i in range(80):
            org = random.choice(organizations)
            party = random.choice([p for p in parties if p.organization_id == org.id])
            pm = random.choice([pm for pm in payment_methods if pm.organization_id == org.id]) if payment_methods else None

            rg = models.RecurringGift(
                id=uuid.uuid4(),
                organization_id=org.id,
                party_id=party.id,
                amount=random.uniform(10, 500),
                currency="USD",
                frequency_amount_count=random.randint(1, 12),
                next_charge_on=fake.date_between(start_date="now", end_date="+60d"),
                payment_method_id=pm.id if pm else None
            )
            recurring_gifts.append(rg)
            db.add(rg)

        db.commit()
        print(f"✅ Created {len(recurring_gifts)} recurring gifts")

        # 22. Soft Credits (100)
        print("\n🎁 Creating Soft Credits...")
        soft_credits = []
        reasons = ["Solicitor", "In Honor Of", "In Memory Of", "Team Captain"]

        for i in range(100):
            donation = random.choice(donations)
            influencer = random.choice([p for p in parties if p.organization_id == donation.organization_id])

            sc = models.SoftCredit(
                id=uuid.uuid4(),
                organization_id=donation.organization_id,
                donation_id=donation.id,
                influencer_party_id=influencer.id,
                amount=donation.intent_amount * random.uniform(0.2, 1.0),
                reason=random.choice(reasons),
                notes=fake.sentence() if random.random() > 0.5 else None
            )
            soft_credits.append(sc)
            db.add(sc)

        db.commit()
        print(f"✅ Created {len(soft_credits)} soft credits")

        # 23. Matching Claims (50)
        print("\n🤲 Creating Matching Claims...")
        matching_claims = []

        for i in range(50):
            donation = random.choice([d for d in donations if d.match_eligible])
            matcher = random.choice([p for p in parties if p.organization_id == donation.organization_id and p.type == "organization"])

            mc = models.MatchingClaim(
                id=uuid.uuid4(),
                organization_id=donation.organization_id,
                donation_id=donation.id,
                matcher_party_id=matcher.id,
                submitted_at=donation.received_date + timedelta(days=random.randint(1, 30)),
                status=random.choice(["submitted", "approved", "paid", "rejected"]),
                paid_payment_id=random.choice([p.id for p in payments]) if random.random() > 0.5 else None
            )
            matching_claims.append(mc)
            db.add(mc)

        db.commit()
        print(f"✅ Created {len(matching_claims)} matching claims")

        # 24. Beneficiaries (120)
        print("\n🙋 Creating Beneficiaries...")
        beneficiaries = []
        pii_levels = ["public", "restricted", "confidential"]

        for org in organizations:
            org_parties = [p for p in parties if p.organization_id == org.id and p.type == "individual"]
            selected_parties = random.sample(org_parties, min(12, len(org_parties)))

            for party in selected_parties:
                beneficiary = models.Beneficiary(
                    id=uuid.uuid4(),
                    organization_id=org.id,
                    party_id=party.id,
                    external_id=f"EXT-{random.randint(10000, 99999)}",
                    pii_level=random.choice(pii_levels)
                )
                beneficiaries.append(beneficiary)
                db.add(beneficiary)

        db.commit()
        print(f"✅ Created {len(beneficiaries)} beneficiaries")

        # 25. Service Events (150)
        print("\n🎯 Creating Service Events...")
        service_events = []

        for program in programs:
            for i in range(random.randint(2, 5)):
                se = models.ServiceEvent(
                    id=uuid.uuid4(),
                    organization_id=program.organization_id,
                    program_id=program.id,
                    date=fake.date_between(start_date="-1y", end_date="now"),
                    location=f"{fake.city()}, {fake.state_abbr()}",
                    units_delivered=random.uniform(10, 500),
                    notes=fake.sentence() if random.random() > 0.5 else None
                )
                service_events.append(se)
                db.add(se)

        db.commit()
        print(f"✅ Created {len(service_events)} service events")

        # 26. Service Beneficiaries (300)
        print("\n🤝 Creating Service-Beneficiary Links...")
        service_beneficiaries = []
        roles = ["participant", "volunteer", "recipient", "coordinator"]

        for se in service_events:
            org_beneficiaries = [b for b in beneficiaries if b.organization_id == se.organization_id]
            if org_beneficiaries:
                selected_beneficiaries = random.sample(org_beneficiaries, min(random.randint(1, 5), len(org_beneficiaries)))

                for beneficiary in selected_beneficiaries:
                    sb = models.ServiceBeneficiary(
                        service_event_id=se.id,
                        beneficiary_id=beneficiary.id,
                        role=random.choice(roles)
                    )
                    service_beneficiaries.append(sb)
                    db.add(sb)

        db.commit()
        print(f"✅ Created {len(service_beneficiaries)} service-beneficiary links")

        # 27. Outcome Metrics (80)
        print("\n📈 Creating Outcome Metrics...")
        outcome_metrics = []
        metric_names = ["Completion Rate", "Satisfaction Score", "Attendance", "Improvement Rate",
                        "Graduation Rate", "Retention Rate", "Impact Score"]
        directions = ["increase", "decrease", "maintain"]

        for program in programs:
            for i in range(random.randint(1, 3)):
                om = models.OutcomeMetric(
                    id=uuid.uuid4(),
                    organization_id=program.organization_id,
                    program_id=program.id,
                    name=random.choice(metric_names),
                    unit=random.choice(["percentage", "count", "score", "days"]),
                    direction=random.choice(directions),
                    target_value=random.uniform(50, 100)
                )
                outcome_metrics.append(om)
                db.add(om)

        db.commit()
        print(f"✅ Created {len(outcome_metrics)} outcome metrics")

        # 28. Outcome Records (400)
        print("\n📊 Creating Outcome Records...")
        outcome_records = []

        for metric in outcome_metrics:
            for i in range(random.randint(3, 8)):
                or_record = models.OutcomeRecord(
                    id=uuid.uuid4(),
                    organization_id=metric.organization_id,
                    outcome_metric_id=metric.id,
                    value=random.uniform(0, 100),
                    source=random.choice(["survey", "assessment", "observation", "report"]),
                    recorded_at=fake.date_time_between(start_date="-1y", end_date="now")
                )
                outcome_records.append(or_record)
                db.add(or_record)

        db.commit()
        print(f"✅ Created {len(outcome_records)} outcome records")

        # 29. Consents (200)
        print("\n✉️ Creating Consents...")
        consents = []
        consent_channels = ["email", "sms", "phone", "mail"]
        consent_statuses = ["opted_in", "opted_out", "pending"]
        opt_in_bases = ["explicit", "implicit", "legitimate_interest"]

        for party in parties:
            if random.random() > 0.3:  # 70% have consents
                for channel in random.sample(consent_channels, random.randint(1, 3)):
                    consent = models.Consent(
                        id=uuid.uuid4(),
                        organization_id=party.organization_id,
                        party_id=party.id,
                        channel=channel,
                        status=random.choice(consent_statuses),
                        opt_in_basis=random.choice(opt_in_bases),
                        captured_at_by=f"Captured at {fake.date_time_between(start_date='-2y', end_date='now')} by {fake.name()}",
                        source=random.choice(["website", "event", "phone_call", "form"])
                    )
                    consents.append(consent)
                    db.add(consent)

        db.commit()
        print(f"✅ Created {len(consents)} consents")

        # 30. Party Roles (150)
        print("\n🎭 Creating Party Roles...")
        party_roles = []
        role_codes = ["donor", "volunteer", "board_member", "staff", "beneficiary", "partner"]

        for party in parties:
            if random.random() > 0.3:  # 70% have roles
                for role_code in random.sample(role_codes, random.randint(1, 2)):
                    start_date = fake.date_between(start_date="-5y", end_date="now")
                    pr = models.PartyRole(
                        party_id=party.id,
                        role_code=role_code,
                        start_date=start_date,
                        end_date=fake.date_between(start_date=start_date, end_date="+2y") if random.random() > 0.7 else None
                    )
                    party_roles.append(pr)
                    db.add(pr)

        db.commit()
        print(f"✅ Created {len(party_roles)} party roles")

        # Summary
        print("\n" + "=" * 60)
        print("🎉 DATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   Organizations: {len(organizations)}")
        print(f"   Permissions: {len(permissions)}")
        print(f"   Roles: {len(roles)}")
        print(f"   Role Permissions: {len(role_perms)}")
        print(f"   Users: {len(users)}")
        print(f"   User Roles: {len(user_roles)}")
        print(f"   Programs: {len(programs)}")
        print(f"   Campaigns: {len(campaigns)}")
        print(f"   Appeals: {len(appeals)}")
        print(f"   Packages: {len(packages)}")
        print(f"   Parties: {len(parties)}")
        print(f"   Contact Points: {len(contact_points)}")
        print(f"   Addresses: {len(addresses)}")
        print(f"   Payment Methods: {len(payment_methods)}")
        print(f"   Funds: {len(funds)}")
        print(f"   Donations: {len(donations)}")
        print(f"   Payments: {len(payments)}")
        print(f"   Donation Lines: {len(donation_lines)}")
        print(f"   Pledges: {len(pledges)}")
        print(f"   Pledge Installments: {len(pledge_installments)}")
        print(f"   Recurring Gifts: {len(recurring_gifts)}")
        print(f"   Soft Credits: {len(soft_credits)}")
        print(f"   Matching Claims: {len(matching_claims)}")
        print(f"   Beneficiaries: {len(beneficiaries)}")
        print(f"   Service Events: {len(service_events)}")
        print(f"   Service Beneficiaries: {len(service_beneficiaries)}")
        print(f"   Outcome Metrics: {len(outcome_metrics)}")
        print(f"   Outcome Records: {len(outcome_records)}")
        print(f"   Consents: {len(consents)}")
        print(f"   Party Roles: {len(party_roles)}")

        total_records = (len(organizations) + len(permissions) + len(roles) + len(role_perms) +
                         len(users) + len(user_roles) + len(programs) + len(campaigns) +
                         len(appeals) + len(packages) + len(parties) + len(contact_points) +
                         len(addresses) + len(payment_methods) + len(funds) + len(donations) +
                         len(payments) + len(donation_lines) + len(pledges) + len(pledge_installments) +
                         len(recurring_gifts) + len(soft_credits) + len(matching_claims) +
                         len(beneficiaries) + len(service_events) + len(service_beneficiaries) +
                         len(outcome_metrics) + len(outcome_records) + len(consents) + len(party_roles))

        print(f"\n   🎯 TOTAL RECORDS: {total_records}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("   DATABASE TEST DATA GENERATOR")
    print("=" * 60)
    generate_data()
    print("\n✅ All done! Your database is now populated with test data.")
    print("🌐 Access your API at: http://localhost:8000/docs")