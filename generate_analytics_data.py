# generate_analytics_data.py
"""
Analytics Test Data Generator
Generates comprehensive test data for all Analytics API endpoints
Extends the base data with strategic planning, metrics, and advanced analytics data
"""

from faker import Faker
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine
import models
import uuid

fake = Faker()
Faker.seed(12345)
random.seed(12345)

def create_analytics_tables():
    """Create additional tables needed for analytics endpoints"""

    with engine.connect() as conn:
        # Strategic Planning table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS strategic_planning (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL REFERENCES organizations(id),
                mission TEXT,
                vision TEXT,
                brand_promise TEXT,
                owner VARCHAR(255),
                last_updated TIMESTAMP,
                north_star_objective TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # SWOT Analysis table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS swot_analysis (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL REFERENCES organizations(id),
                category VARCHAR(50) NOT NULL,
                item TEXT NOT NULL,
                detail_link TEXT,
                rank INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Digital Metrics table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS digital_metrics (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL REFERENCES organizations(id),
                metric_date DATE NOT NULL,
                sessions INTEGER,
                avg_session_duration FLOAT,
                bounce_rate FLOAT,
                email_sends INTEGER,
                email_opens INTEGER,
                email_clicks INTEGER,
                email_ctr FLOAT,
                conversion_to_donation FLOAT,
                conversion_to_volunteer FLOAT,
                conversion_to_newsletter FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Strategic Initiatives table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS strategic_initiatives (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL REFERENCES organizations(id),
                title TEXT NOT NULL,
                owner VARCHAR(255),
                due_date DATE,
                timeframe VARCHAR(20),
                status VARCHAR(1),
                expected_lift FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Initiative Milestones table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS initiative_milestones (
                id UUID PRIMARY KEY,
                initiative_id UUID NOT NULL REFERENCES strategic_initiatives(id),
                name TEXT NOT NULL,
                due_date DATE,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Audience Tracking table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audience_tracking (
                id UUID PRIMARY KEY,
                organization_id UUID NOT NULL REFERENCES organizations(id),
                tracking_date DATE NOT NULL,
                email_list_size INTEGER,
                social_followers INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Add channel field to donations if not exists
        try:
            conn.execute(text("""
                ALTER TABLE donations 
                ADD COLUMN IF NOT EXISTS channel VARCHAR(50)
            """))
        except:
            pass

        conn.commit()
        print("✅ Analytics tables created/verified")

def generate_analytics_data():
    db = SessionLocal()

    try:
        print("🚀 Starting analytics data generation...")
        print("=" * 60)

        # Create analytics tables first
        create_analytics_tables()

        # Get existing organizations
        organizations = db.query(models.Organization).all()
        parties = db.query(models.Party).all()
        programs = db.query(models.Program).all()
        campaigns = db.query(models.Campaign).all()
        donations = db.query(models.Donation).all()

        print(f"\nFound {len(organizations)} organizations to enhance with analytics data")

        # 1. Strategic Planning Data
        print("\n🎯 Creating Strategic Planning data...")
        strategic_plans = []

        mission_templates = [
            "Transform lives through {} and community support",
            "Empower individuals through {} and advocacy",
            "Build stronger communities through {} and collaboration",
            "Create lasting change through {} and innovation"
        ]

        vision_templates = [
            "A world where every individual has access to {}",
            "Communities thriving with {} for all",
            "A future where {} creates opportunities for everyone",
            "Universal access to {} and human dignity"
        ]

        north_star_objectives = [
            "Diversify revenue streams and achieve sustainable growth",
            "Double program impact while maintaining quality",
            "Expand geographic reach to underserved communities",
            "Build endowment to $10M for long-term sustainability",
            "Achieve 80% donor retention rate",
            "Launch three new programs in high-impact areas"
        ]

        for org in organizations:
            focus_areas = ["education", "healthcare", "housing", "employment", "nutrition"]
            focus = random.choice(focus_areas)

            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO strategic_planning 
                    (id, organization_id, mission, vision, brand_promise, owner, last_updated, north_star_objective)
                    VALUES (:id, :org_id, :mission, :vision, :brand_promise, :owner, :updated, :north_star)
                """), {
                    "id": str(uuid.uuid4()),
                    "org_id": str(org.id),
                    "mission": random.choice(mission_templates).format(focus),
                    "vision": random.choice(vision_templates).format(focus),
                    "brand_promise": "Committed to measurable impact and transparency",
                    "owner": "CEO / Board Chair",
                    "updated": fake.date_time_between(start_date="-6m", end_date="now"),
                    "north_star": random.choice(north_star_objectives)
                })
                conn.commit()

        print(f"✅ Created strategic planning data for {len(organizations)} organizations")

        # 2. SWOT Analysis Data
        print("\n📊 Creating SWOT Analysis data...")

        swot_items = {
            "strengths": [
                "Strong donor retention ({}%)",
                "Established community presence ({} years)",
                "Skilled volunteer base ({}+ active)",
                "Diversified funding sources",
                "Experienced leadership team",
                "Strong brand recognition",
                "Proven program outcomes",
                "Strategic partnerships with corporations",
                "Technology-enabled operations",
                "Dedicated board of directors"
            ],
            "weaknesses": [
                "Limited digital fundraising capability",
                "Aging donor base (avg {} years)",
                "Single-source funding dependency ({}%)",
                "Outdated technology infrastructure",
                "Limited staff capacity",
                "Geographic concentration",
                "Low social media engagement",
                "Inconsistent donor communication",
                "Limited major gift pipeline",
                "High staff turnover in development"
            ],
            "opportunities": [
                "Growing corporate partnership interest",
                "Untapped monthly giving program",
                "Expansion into adjacent service areas",
                "Grant funding from new foundations",
                "Digital marketing channels",
                "Strategic mergers or collaborations",
                "Planned giving program launch",
                "New demographic segments",
                "Government funding opportunities",
                "Impact investing partnerships"
            ],
            "threats": [
                "Increased competition for grants",
                "Economic uncertainty affecting giving",
                "Regulatory changes in nonprofit sector",
                "Donor fatigue from competing causes",
                "Rising operational costs",
                "Talent retention challenges",
                "Declining foundation giving",
                "Public trust in nonprofits declining",
                "Technology disruption",
                "Political uncertainty"
            ]
        }

        for org in organizations:
            for category, items in swot_items.items():
                selected_items = random.sample(items, 3)
                for rank, item in enumerate(selected_items, 1):
                    # Format items with random values
                    if "{}" in item:
                        if "retention" in item:
                            formatted_item = item.format(random.randint(75, 92))
                        elif "years" in item and "presence" in item:
                            formatted_item = item.format(random.randint(5, 25))
                        elif "years" in item and "aging" in item:
                            formatted_item = item.format(random.randint(58, 68))
                        elif "volunteer" in item:
                            formatted_item = item.format(random.randint(200, 800))
                        elif "dependency" in item:
                            formatted_item = item.format(random.randint(35, 55))
                        else:
                            formatted_item = item
                    else:
                        formatted_item = item

                    with engine.connect() as conn:
                        conn.execute(text("""
                            INSERT INTO swot_analysis 
                            (id, organization_id, category, item, detail_link, rank)
                            VALUES (:id, :org_id, :category, :item, :link, :rank)
                        """), {
                            "id": str(uuid.uuid4()),
                            "org_id": str(org.id),
                            "category": category,
                            "item": formatted_item,
                            "link": f"/strategic-plan/swot#{category}",
                            "rank": rank
                        })
                        conn.commit()

        print(f"✅ Created SWOT analysis data for {len(organizations)} organizations")

        # 3. Digital Metrics Data (monthly data for past 12 months)
        print("\n💻 Creating Digital Metrics data...")

        today = datetime.now().date()
        for org in organizations:
            base_sessions = random.randint(30000, 60000)
            base_email_list = random.randint(8000, 15000)

            for i in range(12):
                metric_date = today - timedelta(days=30*i)

                # Add growth trend
                growth_factor = 1 + (i * 0.02)  # 2% monthly growth
                sessions = int(base_sessions * growth_factor * random.uniform(0.9, 1.1))
                email_sends = int(base_email_list * random.uniform(0.8, 1.2))
                email_opens = int(email_sends * random.uniform(0.25, 0.35))
                email_clicks = int(email_opens * random.uniform(0.15, 0.25))

                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO digital_metrics 
                        (id, organization_id, metric_date, sessions, avg_session_duration, 
                         bounce_rate, email_sends, email_opens, email_clicks, email_ctr,
                         conversion_to_donation, conversion_to_volunteer, conversion_to_newsletter)
                        VALUES (:id, :org_id, :date, :sessions, :duration, :bounce, 
                                :sends, :opens, :clicks, :ctr, :conv_don, :conv_vol, :conv_news)
                    """), {
                        "id": str(uuid.uuid4()),
                        "org_id": str(org.id),
                        "date": metric_date,
                        "sessions": sessions,
                        "duration": random.uniform(120, 180),
                        "bounce": random.uniform(38, 52),
                        "sends": email_sends,
                        "opens": email_opens,
                        "clicks": email_clicks,
                        "ctr": (email_clicks / email_sends * 100) if email_sends > 0 else 0,
                        "conv_don": random.uniform(1.5, 4.0),
                        "conv_vol": random.uniform(0.8, 2.0),
                        "conv_news": random.uniform(6.0, 12.0)
                    })
                    conn.commit()

        print(f"✅ Created digital metrics data for {len(organizations)} organizations")

        # 4. Audience Tracking Data
        print("\n👥 Creating Audience Tracking data...")

        for org in organizations:
            base_email = random.randint(8000, 15000)
            base_social = random.randint(10000, 20000)

            for i in range(24):  # 24 months of data
                tracking_date = today - timedelta(days=30*i)

                # Add growth
                email_size = int(base_email * (1 + i * 0.03) * random.uniform(0.95, 1.05))
                social_followers = int(base_social * (1 + i * 0.04) * random.uniform(0.95, 1.05))

                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO audience_tracking 
                        (id, organization_id, tracking_date, email_list_size, social_followers)
                        VALUES (:id, :org_id, :date, :email, :social)
                    """), {
                        "id": str(uuid.uuid4()),
                        "org_id": str(org.id),
                        "date": tracking_date,
                        "email": email_size,
                        "social": social_followers
                    })
                    conn.commit()

        print(f"✅ Created audience tracking data for {len(organizations)} organizations")

        # 5. Strategic Initiatives (90-day bets and 1-year objectives)
        print("\n🎯 Creating Strategic Initiatives...")

        initiative_templates = {
            "90_day": [
                ("Launch Monthly Giving Program", "Development Director", 125000),
                ("Diversify Corporate Partnerships", "Partnerships Manager", 200000),
                ("Upgrade CRM System", "Technology Director", 50000),
                ("Launch Email Automation", "Marketing Manager", 30000),
                ("Expand Social Media Presence", "Communications Director", 15000),
                ("Major Donor Cultivation Event", "Executive Director", 75000),
                ("Volunteer Recruitment Campaign", "Volunteer Coordinator", 10000),
                ("Program Impact Study", "Program Director", 25000)
            ],
            "1_year": [
                ("Build $5M Endowment", "Board Development Committee", 5000000),
                ("Launch Three New Programs", "Chief Program Officer", 500000),
                ("Expand to Two New Cities", "Executive Director", 750000),
                ("Achieve 80% Donor Retention", "Chief Development Officer", 300000),
                ("Double Social Media Following", "Marketing Director", 50000),
                ("Implement Data Analytics Platform", "CTO", 150000),
                ("Strategic Partnership with University", "CEO", 250000),
                ("Launch Planned Giving Program", "Development Director", 100000)
            ]
        }

        for org in organizations:
            # Create 2-3 90-day initiatives
            for title, owner, lift in random.sample(initiative_templates["90_day"], random.randint(2, 3)):
                due_date = today + timedelta(days=random.randint(30, 90))
                status = random.choice(["G", "G", "A", "R"])

                initiative_id = uuid.uuid4()

                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO strategic_initiatives 
                        (id, organization_id, title, owner, due_date, timeframe, status, expected_lift)
                        VALUES (:id, :org_id, :title, :owner, :due, :timeframe, :status, :lift)
                    """), {
                        "id": str(initiative_id),
                        "org_id": str(org.id),
                        "title": title,
                        "owner": owner,
                        "due": due_date,
                        "timeframe": "90_day",
                        "status": status,
                        "lift": lift
                    })

                    # Create milestones
                    milestones = [
                        ("Planning & Research", 15, "complete"),
                        ("Execution Phase 1", 30, "in_progress" if status == "G" else "delayed"),
                        ("Execution Phase 2", 60, "pending"),
                        ("Completion & Review", 90, "pending")
                    ]

                    for milestone_name, days_offset, milestone_status in milestones:
                        conn.execute(text("""
                            INSERT INTO initiative_milestones 
                            (id, initiative_id, name, due_date, status)
                            VALUES (:id, :init_id, :name, :due, :status)
                        """), {
                            "id": str(uuid.uuid4()),
                            "init_id": str(initiative_id),
                            "name": milestone_name,
                            "due": today + timedelta(days=days_offset),
                            "status": milestone_status
                        })

                    conn.commit()

            # Create 1-2 1-year initiatives
            for title, owner, lift in random.sample(initiative_templates["1_year"], random.randint(1, 2)):
                due_date = today + timedelta(days=random.randint(180, 365))
                status = random.choice(["G", "G", "A"])

                initiative_id = uuid.uuid4()

                with engine.connect() as conn:
                    conn.execute(text("""
                        INSERT INTO strategic_initiatives 
                        (id, organization_id, title, owner, due_date, timeframe, status, expected_lift)
                        VALUES (:id, :org_id, :title, :owner, :due, :timeframe, :status, :lift)
                    """), {
                        "id": str(initiative_id),
                        "org_id": str(org.id),
                        "title": title,
                        "owner": owner,
                        "due": due_date,
                        "timeframe": "1_year",
                        "status": status,
                        "lift": lift
                    })

                    # Create quarterly milestones
                    milestones = [
                        ("Q1: Foundation & Planning", 90, "complete"),
                        ("Q2: Implementation Phase 1", 180, "in_progress"),
                        ("Q3: Implementation Phase 2", 270, "pending"),
                        ("Q4: Completion & Assessment", 365, "pending")
                    ]

                    for milestone_name, days_offset, milestone_status in milestones:
                        conn.execute(text("""
                            INSERT INTO initiative_milestones 
                            (id, initiative_id, name, due_date, status)
                            VALUES (:id, :init_id, :name, :due, :status)
                        """), {
                            "id": str(uuid.uuid4()),
                            "init_id": str(initiative_id),
                            "name": milestone_name,
                            "due": today + timedelta(days=days_offset),
                            "status": milestone_status
                        })

                    conn.commit()

        print(f"✅ Created strategic initiatives for {len(organizations)} organizations")

        # 6. Update existing donations with channel information
        print("\n📊 Updating donations with channel data...")

        channels = ["online", "offline", "event"]
        channel_weights = [0.35, 0.45, 0.20]  # Distribution of channels

        donation_count = 0
        for donation in donations:
            channel = random.choices(channels, weights=channel_weights)[0]

            with engine.connect() as conn:
                conn.execute(text("""
                    UPDATE donations 
                    SET channel = :channel
                    WHERE id = :id
                """), {
                    "channel": channel,
                    "id": str(donation.id)
                })
                conn.commit()
                donation_count += 1

        print(f"✅ Updated {donation_count} donations with channel data")

        # 7. Add variance_vs_plan to campaigns
        print("\n📈 Adding campaign performance metrics...")

        try:
            with engine.connect() as conn:
                conn.execute(text("""
                    ALTER TABLE campaigns 
                    ADD COLUMN IF NOT EXISTS variance_vs_plan FLOAT
                """))
                conn.commit()
        except:
            pass

        for campaign in campaigns:
            variance = random.uniform(-15.0, 25.0)  # -15% to +25% variance

            with engine.connect() as conn:
                conn.execute(text("""
                    UPDATE campaigns 
                    SET variance_vs_plan = :variance
                    WHERE id = :id
                """), {
                    "variance": variance,
                    "id": str(campaign.id)
                })
                conn.commit()

        print(f"✅ Updated {len(campaigns)} campaigns with variance data")

        # Summary
        print("\n" + "=" * 60)
        print("🎉 ANALYTICS DATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Analytics Data Summary:")
        print(f"   Strategic Plans: {len(organizations)}")
        print(f"   SWOT Items: {len(organizations) * 12}")
        print(f"   Digital Metrics: {len(organizations) * 12}")
        print(f"   Audience Tracking: {len(organizations) * 24}")
        print(f"   Strategic Initiatives: ~{len(organizations) * 4}")
        print(f"   Initiative Milestones: ~{len(organizations) * 16}")
        print(f"   Updated Donations: {donation_count}")
        print(f"   Updated Campaigns: {len(campaigns)}")

        print("\n✅ Your database is now ready to test all Analytics API endpoints!")
        print("🌐 Access your API at: http://localhost:8000/docs")
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("   ANALYTICS DATA GENERATOR")
    print("   Extending base data for Analytics API testing")
    print("=" * 60)
    generate_analytics_data()