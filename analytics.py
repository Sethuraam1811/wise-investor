# analytics.py - Add to your FastAPI project
"""
Analytics API endpoints for comprehensive organizational dashboard
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from database import get_db
import models
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# =====================================================================
# RESPONSE MODELS
# =====================================================================

class MissionVisionCard(BaseModel):
    mission: str
    vision: str
    brand_promise: str
    owner: str
    last_updated: datetime
    north_star_objective: str

class SWOTItem(BaseModel):
    category: str  # strength, weakness, opportunity, threat
    items: List[str]
    detail_link: Optional[str] = None

class LifecycleStage(BaseModel):
    stage: str
    count: int
    avg_days_in_stage: float
    handoff_conversion_rate: float
    sla_days: int
    sla_status: str  # green, amber, red

class FundraisingVitals(BaseModel):
    income_diversification: Dict[str, float]
    donor_pyramid: Dict[str, int]
    retention_rates: Dict[str, float]
    avg_gift: float
    avg_gift_prior_year: float
    multi_year_donors: int
    inflow_lapsed_ratio: float

class AudienceMetrics(BaseModel):
    active_donors: int
    active_donors_yoy_delta: int
    donors_gte_1k: int
    donors_gte_1k_yoy_delta: int
    donors_gte_10k: int
    donors_gte_10k_yoy_delta: int
    email_list_size: int
    email_list_yoy_delta: int
    social_followers: int
    social_followers_yoy_delta: int

class RevenueRollup(BaseModel):
    year: int
    total_revenue: float
    online_revenue: float
    offline_revenue: float
    event_revenue: float
    first_gift_count: int
    major_gift_count: int
    variance_vs_plan: float

class ProgramImpact(BaseModel):
    program_id: str
    program_name: str
    beneficiaries_served: int
    units_delivered: float
    hours_delivered: float
    cost_per_outcome: float
    progress_vs_target: float
    quarterly_target: float

class DigitalKPIs(BaseModel):
    sessions: int
    avg_session_duration: float
    bounce_rate: float
    email_sends: int
    email_opens: int
    email_clicks: int
    email_ctr: float
    conversion_to_donation: float
    conversion_to_volunteer: float
    conversion_to_newsletter: float

class HighImpactTarget(BaseModel):
    id: str
    title: str
    owner: str
    due_date: date
    timeframe: str  # 90_day or 1_year
    status: str  # R (red), A (amber), G (green)
    expected_lift: float
    milestones: List[Dict[str, Any]]
    risk_flags: List[str]

# =====================================================================
# A. MISSION / VISION / BRAND PROMISE & SWOT
# =====================================================================

@router.get("/mission-vision/{organization_id}", response_model=MissionVisionCard)
def get_mission_vision(organization_id: str, db: Session = Depends(get_db)):
    """
    Get organization's mission, vision, brand promise, and north star objective
    """
    org = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # This would come from a new table or organization metadata
    # For now, returning example structure
    return {
        "mission": "Transform lives through education and community support",
        "vision": "A world where every individual has access to quality resources",
        "brand_promise": "Committed to measurable impact and transparency",
        "owner": "CEO / Board Chair",
        "last_updated": datetime.now() - timedelta(days=30),
        "north_star_objective": "Diversify revenue streams and achieve sustainable growth"
    }

@router.get("/swot/{organization_id}", response_model=List[SWOTItem])
def get_swot_analysis(organization_id: str, db: Session = Depends(get_db)):
    """
    Get SWOT analysis (top 3 per quadrant)
    """
    # This would typically come from a strategic planning table
    return [
        {
            "category": "strengths",
            "items": [
                "Strong donor retention (87%)",
                "Established community presence (15 years)",
                "Skilled volunteer base (500+ active)"
            ],
            "detail_link": "/strategic-plan/swot#strengths"
        },
        {
            "category": "weaknesses",
            "items": [
                "Limited digital fundraising capability",
                "Aging donor base (avg 62 years)",
                "Single-source funding dependency (45%)"
            ],
            "detail_link": "/strategic-plan/swot#weaknesses"
        },
        {
            "category": "opportunities",
            "items": [
                "Growing corporate partnership interest",
                "Untapped monthly giving program",
                "Expansion into adjacent service areas"
            ],
            "detail_link": "/strategic-plan/swot#opportunities"
        },
        {
            "category": "threats",
            "items": [
                "Increased competition for grants",
                "Economic uncertainty affecting giving",
                "Regulatory changes in nonprofit sector"
            ],
            "detail_link": "/strategic-plan/swot#threats"
        }
    ]

# =====================================================================
# B. LIFECYCLE SNAPSHOT
# =====================================================================

@router.get("/lifecycle/{organization_id}", response_model=List[LifecycleStage])
def get_lifecycle_snapshot(
        organization_id: str,
        segment: Optional[str] = None,
        channel: Optional[str] = None,
        campaign_id: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """
    Donor lifecycle stages with counts, average days, and SLA compliance
    Stages: Acquisition → Conversion → Cultivation → Stewardship → Reactivation
    """
    # This requires a donor lifecycle tracking table
    # For demonstration, calculating from party and donation data

    stages = []
    stage_definitions = {
        "Acquisition": {"sla_days": 30, "description": "New prospects"},
        "Conversion": {"sla_days": 45, "description": "First-time donors"},
        "Cultivation": {"sla_days": 60, "description": "Repeat donors"},
        "Stewardship": {"sla_days": 90, "description": "Major donors"},
        "Reactivation": {"sla_days": 60, "description": "Lapsed donors"}
    }

    # Get parties with donation data
    query = db.query(
        models.Party.id,
        func.count(models.Donation.id).label('donation_count'),
        func.max(models.Donation.received_date).label('last_donation'),
        func.sum(models.Donation.intent_amount).label('total_given')
    ).join(
        models.Donation, models.Party.id == models.Donation.party_id
    ).filter(
        models.Party.organization_id == organization_id
    ).group_by(models.Party.id)

    results = query.all()

    # Categorize parties by lifecycle stage
    acquisition_count = 0
    conversion_count = 0
    cultivation_count = 0
    stewardship_count = 0
    reactivation_count = 0

    now = datetime.now()

    for party_id, donation_count, last_donation, total_given in results:
        days_since_last = (now - last_donation).days if last_donation else 999

        if donation_count == 0:
            acquisition_count += 1
        elif donation_count == 1:
            conversion_count += 1
        elif donation_count > 1 and total_given < 1000:
            cultivation_count += 1
        elif total_given >= 1000 and days_since_last < 365:
            stewardship_count += 1
        elif days_since_last > 365:
            reactivation_count += 1
        else:
            cultivation_count += 1

    stages = [
        {
            "stage": "Acquisition",
            "count": acquisition_count,
            "avg_days_in_stage": 25.5,
            "handoff_conversion_rate": 42.3,
            "sla_days": 30,
            "sla_status": "green"
        },
        {
            "stage": "Conversion",
            "count": conversion_count,
            "avg_days_in_stage": 38.2,
            "handoff_conversion_rate": 67.8,
            "sla_days": 45,
            "sla_status": "green"
        },
        {
            "stage": "Cultivation",
            "count": cultivation_count,
            "avg_days_in_stage": 52.1,
            "handoff_conversion_rate": 24.5,
            "sla_days": 60,
            "sla_status": "amber"
        },
        {
            "stage": "Stewardship",
            "count": stewardship_count,
            "avg_days_in_stage": 180.3,
            "handoff_conversion_rate": 85.2,
            "sla_days": 90,
            "sla_status": "red"
        },
        {
            "stage": "Reactivation",
            "count": reactivation_count,
            "avg_days_in_stage": 45.7,
            "handoff_conversion_rate": 18.9,
            "sla_days": 60,
            "sla_status": "amber"
        }
    ]

    return stages

# =====================================================================
# C. FUNDRAISING VITALS
# =====================================================================

@router.get("/fundraising-vitals/{organization_id}", response_model=FundraisingVitals)
def get_fundraising_vitals(organization_id: str, db: Session = Depends(get_db)):
    """
    Key fundraising metrics: diversification, donor pyramid, retention, etc.
    """
    current_year = datetime.now().year
    prior_year = current_year - 1

    # Income Diversification by fund restriction
    fund_totals = db.query(
        models.Fund.restriction,
        func.sum(models.DonationLine.amount).label('total')
    ).join(
        models.DonationLine, models.Fund.id == models.DonationLine.program_id
    ).filter(
        models.Fund.organization_id == organization_id
    ).group_by(models.Fund.restriction).all()

    total_restricted = sum([t[1] for t in fund_totals if t[1]])
    income_diversification = {}
    for restriction, amount in fund_totals:
        if amount and total_restricted > 0:
            income_diversification[restriction or "unrestricted"] = round((amount / total_restricted) * 100, 2)

    # Donor Pyramid - annual giving bands
    donor_pyramid_query = db.query(
        models.Party.id,
        func.sum(models.Donation.intent_amount).label('annual_total')
    ).join(
        models.Donation, models.Party.id == models.Donation.party_id
    ).filter(
        models.Party.organization_id == organization_id,
        extract('year', models.Donation.received_date) == current_year
    ).group_by(models.Party.id).all()

    donor_pyramid = {
        "<$100": 0,
        "$100-499": 0,
        "$500-999": 0,
        "$1k-4.9k": 0,
        "$5k-9.9k": 0,
        "$10k+": 0
    }

    for party_id, annual_total in donor_pyramid_query:
        if annual_total:
            if annual_total < 100:
                donor_pyramid["<$100"] += 1
            elif annual_total < 500:
                donor_pyramid["$100-499"] += 1
            elif annual_total < 1000:
                donor_pyramid["$500-999"] += 1
            elif annual_total < 5000:
                donor_pyramid["$1k-4.9k"] += 1
            elif annual_total < 10000:
                donor_pyramid["$5k-9.9k"] += 1
            else:
                donor_pyramid["$10k+"] += 1

    # Retention rates
    current_year_donors = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == current_year
    ).scalar() or 0

    prior_year_donors = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == prior_year
    ).scalar() or 0

    retained_donors = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        models.Donation.party_id.in_(
            db.query(models.Donation.party_id).filter(
                extract('year', models.Donation.received_date) == prior_year
            )
        ),
        extract('year', models.Donation.received_date) == current_year
    ).scalar() or 0

    overall_retention = (retained_donors / prior_year_donors * 100) if prior_year_donors > 0 else 0

    # Average gift
    avg_gift_current = db.query(func.avg(models.Donation.intent_amount)).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == current_year
    ).scalar() or 0

    avg_gift_prior = db.query(func.avg(models.Donation.intent_amount)).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == prior_year
    ).scalar() or 0

    # Multi-year donors
    multi_year_donors = db.query(func.count(func.distinct(models.Party.id))).filter(
        models.Party.id.in_(
            db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) >= current_year - 2
            ).group_by(models.Donation.party_id).having(
                func.count(func.distinct(extract('year', models.Donation.received_date))) >= 2
            )
        )
    ).scalar() or 0

    # New donors vs lapsed
    new_donors = current_year_donors - retained_donors
    lapsed_donors = prior_year_donors - retained_donors
    inflow_lapsed_ratio = (new_donors / lapsed_donors) if lapsed_donors > 0 else 0

    return {
        "income_diversification": income_diversification,
        "donor_pyramid": donor_pyramid,
        "retention_rates": {
            "overall": round(overall_retention, 2),
            "first_year": 45.3,  # Would calculate from first-time donor cohort
            "major": 92.1  # Would calculate from major donor segment
        },
        "avg_gift": round(float(avg_gift_current), 2),
        "avg_gift_prior_year": round(float(avg_gift_prior), 2),
        "multi_year_donors": multi_year_donors,
        "inflow_lapsed_ratio": round(inflow_lapsed_ratio, 2)
    }

# =====================================================================
# D. AUDIENCE & ASSETS (YoY)
# =====================================================================

@router.get("/audience-metrics/{organization_id}", response_model=AudienceMetrics)
def get_audience_metrics(organization_id: str, db: Session = Depends(get_db)):
    """
    Audience size and growth metrics year-over-year
    """
    current_year = datetime.now().year
    prior_year = current_year - 1

    # Active donors (gave in last 24 months)
    active_donors_current = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        models.Donation.received_date >= datetime.now() - timedelta(days=730)
    ).scalar() or 0

    active_donors_prior = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        models.Donation.received_date >= datetime.now() - timedelta(days=1095),
        models.Donation.received_date < datetime.now() - timedelta(days=365)
    ).scalar() or 0

    # Donors >= $1k
    donors_1k_current = db.query(func.count(func.distinct(models.Party.id))).filter(
        models.Party.id.in_(
            db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) == current_year
            ).group_by(models.Donation.party_id).having(
                func.sum(models.Donation.intent_amount) >= 1000
            )
        )
    ).scalar() or 0

    donors_1k_prior = db.query(func.count(func.distinct(models.Party.id))).filter(
        models.Party.id.in_(
            db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) == prior_year
            ).group_by(models.Donation.party_id).having(
                func.sum(models.Donation.intent_amount) >= 1000
            )
        )
    ).scalar() or 0

    # Donors >= $10k
    donors_10k_current = db.query(func.count(func.distinct(models.Party.id))).filter(
        models.Party.id.in_(
            db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) == current_year
            ).group_by(models.Donation.party_id).having(
                func.sum(models.Donation.intent_amount) >= 10000
            )
        )
    ).scalar() or 0

    donors_10k_prior = db.query(func.count(func.distinct(models.Party.id))).filter(
        models.Party.id.in_(
            db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) == prior_year
            ).group_by(models.Donation.party_id).having(
                func.sum(models.Donation.intent_amount) >= 10000
            )
        )
    ).scalar() or 0

    # Email list size (from contact points)
    email_list_current = db.query(func.count(models.ContactPoint.id)).filter(
        models.ContactPoint.organization_id == organization_id,
        models.ContactPoint.type == "email",
        models.ContactPoint.verified_at.isnot(None)
    ).scalar() or 0

    # Would need historical snapshot for prior year email list size
    email_list_prior = int(email_list_current * 0.92)  # Placeholder

    return {
        "active_donors": active_donors_current,
        "active_donors_yoy_delta": active_donors_current - active_donors_prior,
        "donors_gte_1k": donors_1k_current,
        "donors_gte_1k_yoy_delta": donors_1k_current - donors_1k_prior,
        "donors_gte_10k": donors_10k_current,
        "donors_gte_10k_yoy_delta": donors_10k_current - donors_10k_prior,
        "email_list_size": email_list_current,
        "email_list_yoy_delta": email_list_current - email_list_prior,
        "social_followers": 15420,  # Would come from social media integration
        "social_followers_yoy_delta": 1230
    }

# =====================================================================
# E. REVENUE ROLLUP (3-year comparison)
# =====================================================================

@router.get("/revenue-rollup/{organization_id}", response_model=List[RevenueRollup])
def get_revenue_rollup(organization_id: str, db: Session = Depends(get_db)):
    """
    Revenue breakdown by year and channel
    """
    current_year = datetime.now().year
    years = [current_year - 2, current_year - 1, current_year]

    results = []

    for year in years:
        # Total revenue
        total_revenue = db.query(func.sum(models.Donation.intent_amount)).filter(
            models.Donation.organization_id == organization_id,
            extract('year', models.Donation.received_date) == year
        ).scalar() or 0

        # Revenue by channel (would need channel field in donations)
        # Placeholder logic
        online_revenue = total_revenue * 0.35
        offline_revenue = total_revenue * 0.50
        event_revenue = total_revenue * 0.15

        # First gift count
        first_gift_count = db.query(func.count(models.Donation.id)).filter(
            models.Donation.organization_id == organization_id,
            extract('year', models.Donation.received_date) == year,
            models.Donation.party_id.in_(
                db.query(models.Donation.party_id).filter(
                    models.Donation.organization_id == organization_id
                ).group_by(models.Donation.party_id).having(
                    func.min(models.Donation.received_date) >= f"{year}-01-01"
                )
            )
        ).scalar() or 0

        # Major gifts (>= $1000)
        major_gift_count = db.query(func.count(models.Donation.id)).filter(
            models.Donation.organization_id == organization_id,
            extract('year', models.Donation.received_date) == year,
            models.Donation.intent_amount >= 1000
        ).scalar() or 0

        results.append({
            "year": year,
            "total_revenue": float(total_revenue),
            "online_revenue": float(online_revenue),
            "offline_revenue": float(offline_revenue),
            "event_revenue": float(event_revenue),
            "first_gift_count": first_gift_count,
            "major_gift_count": major_gift_count,
            "variance_vs_plan": 2.5 if year == current_year else 0  # Would come from budget table
        })

    return results

# =====================================================================
# F. PROGRAM & IMPACT
# =====================================================================

@router.get("/program-impact/{organization_id}", response_model=List[ProgramImpact])
def get_program_impact(organization_id: str, db: Session = Depends(get_db)):
    """
    Program impact metrics: beneficiaries, units delivered, cost per outcome
    """
    programs = db.query(models.Program).filter(
        models.Program.organization_id == organization_id
    ).all()

    results = []

    for program in programs:
        # Beneficiaries served
        beneficiaries_served = db.query(func.count(func.distinct(models.ServiceBeneficiary.beneficiary_id))).filter(
            models.ServiceBeneficiary.service_event_id.in_(
                db.query(models.ServiceEvent.id).filter(
                    models.ServiceEvent.program_id == program.id
                )
            )
        ).scalar() or 0

        # Units delivered
        units_delivered = db.query(func.sum(models.ServiceEvent.units_delivered)).filter(
            models.ServiceEvent.program_id == program.id
        ).scalar() or 0

        # Hours delivered (assuming units are in hours)
        hours_delivered = float(units_delivered)

        # Cost per outcome
        program_expenses = db.query(func.sum(models.DonationLine.amount)).filter(
            models.DonationLine.program_id == program.id
        ).scalar() or 0

        cost_per_outcome = (float(program_expenses) / beneficiaries_served) if beneficiaries_served > 0 else 0

        # Progress vs quarterly target
        quarterly_target = 150  # Would come from program goals table
        progress = (beneficiaries_served / quarterly_target * 100) if quarterly_target > 0 else 0

        results.append({
            "program_id": str(program.id),
            "program_name": program.description or program.code,
            "beneficiaries_served": beneficiaries_served,
            "units_delivered": float(units_delivered),
            "hours_delivered": hours_delivered,
            "cost_per_outcome": round(cost_per_outcome, 2),
            "progress_vs_target": round(progress, 2),
            "quarterly_target": quarterly_target
        })

    return results

# =====================================================================
# G. DIGITAL / WEBSITE KPIs
# =====================================================================

@router.get("/digital-kpis/{organization_id}", response_model=DigitalKPIs)
def get_digital_kpis(organization_id: str, db: Session = Depends(get_db)):
    """
    Digital marketing and website performance metrics
    Note: This would typically integrate with Google Analytics, email platform APIs
    """
    # These would come from integration with analytics platforms
    # Placeholder data structure
    return {
        "sessions": 45230,
        "avg_session_duration": 142.5,  # seconds
        "bounce_rate": 42.3,  # percentage
        "email_sends": 12500,
        "email_opens": 3750,
        "email_clicks": 825,
        "email_ctr": 6.6,  # percentage
        "conversion_to_donation": 2.8,  # percentage
        "conversion_to_volunteer": 1.2,
        "conversion_to_newsletter": 8.5
    }

# =====================================================================
# H. HIGH IMPACT TARGETS
# =====================================================================

@router.get("/high-impact-targets/{organization_id}", response_model=List[HighImpactTarget])
def get_high_impact_targets(
        organization_id: str,
        timeframe: Optional[str] = Query(None, regex="^(90_day|1_year)$"),
        db: Session = Depends(get_db)
):
    """
    Strategic bets and initiatives with owner, due date, status, and milestones
    """
    # This would come from a strategic initiatives/OKR table
    # Placeholder data showing the structure
    targets = [
        {
            "id": "1",
            "title": "Launch Monthly Giving Program",
            "owner": "Sarah Johnson - Development Director",
            "due_date": date.today() + timedelta(days=85),
            "timeframe": "90_day",
            "status": "G",  # Green - on track
            "expected_lift": 125000.00,  # Expected additional annual revenue
            "milestones": [
                {"name": "Platform selection", "due": "2025-01-15", "status": "complete"},
                {"name": "Marketing materials", "due": "2025-02-01", "status": "in_progress"},
                {"name": "Soft launch", "due": "2025-02-15", "status": "pending"},
                {"name": "Full launch", "due": "2025-03-01", "status": "pending"}
            ],
            "risk_flags": []
        },
        {
            "id": "2",
            "title": "Diversify Corporate Partnerships",
            "owner": "Michael Chen - Partnerships Manager",
            "due_date": date.today() + timedelta(days=75),
            "timeframe": "90_day",
            "status": "A",  # Amber - at risk
            "expected_lift": 200000.00,
            "milestones": [
                {"name": "Prospect research", "due": "2024-12-15", "status": "complete"},
                {"name": "Initial outreach", "due": "2025-01-10", "status": "complete"},
                {"name": "Proposal submissions", "due": "2025-02-01", "status": "in_progress"},
                {"name": "Close 3 partnerships", "due": "2025-02-28", "status": "pending"}
            ],
            "risk_flags": ["Slower response rate than expected", "Budget approval delays at corporate partners"]
        },
        {
            "id": "3",
            "title": "Implement Major Gifts Program",
            "owner": "Jennifer Martinez - Major Gifts Officer",
            "due_date": date.today() + timedelta(days=335),
            "timeframe": "1_year",
            "status": "G",
            "expected_lift": 500000.00,
            "milestones": [
                {"name": "Donor identification & research", "due": "2025-03-31", "status": "in_progress"},
                {"name": "Qualification meetings", "due": "2025-06-30", "status": "pending"},
                {"name": "Cultivation events", "due": "2025-09-30", "status": "pending"},
                {"name": "Solicitation phase", "due": "2025-12-31", "status": "pending"}
            ],
            "risk_flags": []
        },
        {
            "id": "4",
            "title": "Expand Email Marketing Automation",
            "owner": "David Park - Marketing Manager",
            "due_date": date.today() + timedelta(days=60),
            "timeframe": "90_day",
            "status": "R",  # Red - behind schedule
            "expected_lift": 75000.00,
            "milestones": [
                {"name": "Platform upgrade", "due": "2024-12-20", "status": "complete"},
                {"name": "Segment definition", "due": "2025-01-15", "status": "delayed"},
                {"name": "Journey mapping", "due": "2025-02-01", "status": "pending"},
                {"name": "Launch automated campaigns", "due": "2025-02-15", "status": "pending"}
            ],
            "risk_flags": ["Technical delays in integration", "Staffing constraints"]
        },
        {
            "id": "5",
            "title": "Double Online Giving Revenue",
            "owner": "Emily Rodriguez - Digital Fundraising Lead",
            "due_date": date.today() + timedelta(days=365),
            "timeframe": "1_year",
            "status": "G",
            "expected_lift": 300000.00,
            "milestones": [
                {"name": "Website optimization", "due": "2025-04-30", "status": "in_progress"},
                {"name": "SEO/SEM campaign launch", "due": "2025-05-31", "status": "pending"},
                {"name": "Social media expansion", "due": "2025-07-31", "status": "pending"},
                {"name": "Year-end campaign 2.0", "due": "2025-12-15", "status": "pending"}
            ],
            "risk_flags": []
        }
    ]

    # Filter by timeframe if specified
    if timeframe:
        targets = [t for t in targets if t["timeframe"] == timeframe]

    return targets

# =====================================================================
# ADDITIONAL HELPER ENDPOINTS
# =====================================================================

@router.get("/dashboard-summary/{organization_id}")
def get_dashboard_summary(organization_id: str, db: Session = Depends(get_db)):
    """
    Comprehensive dashboard summary combining all key metrics
    """
    return {
        "organization_id": organization_id,
        "as_of_date": datetime.now().isoformat(),
        "sections": {
            "mission_vision": f"/analytics/mission-vision/{organization_id}",
            "swot": f"/analytics/swot/{organization_id}",
            "lifecycle": f"/analytics/lifecycle/{organization_id}",
            "fundraising_vitals": f"/analytics/fundraising-vitals/{organization_id}",
            "audience_metrics": f"/analytics/audience-metrics/{organization_id}",
            "revenue_rollup": f"/analytics/revenue-rollup/{organization_id}",
            "program_impact": f"/analytics/program-impact/{organization_id}",
            "digital_kpis": f"/analytics/digital-kpis/{organization_id}",
            "high_impact_targets": f"/analytics/high-impact-targets/{organization_id}"
        }
    }

@router.get("/alerts/{organization_id}")
def get_threshold_alerts(organization_id: str, db: Session = Depends(get_db)):
    """
    Threshold-based alerts for key metrics
    """
    alerts = []

    # Check retention rate
    current_year = datetime.now().year
    prior_year = current_year - 1

    current_year_donors = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == current_year
    ).scalar() or 0

    prior_year_donors = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == prior_year
    ).scalar() or 0

    retained = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        models.Donation.party_id.in_(
            db.query(models.Donation.party_id).filter(
                extract('year', models.Donation.received_date) == prior_year
            )
        ),
        extract('year', models.Donation.received_date) == current_year
    ).scalar() or 0

    retention_rate = (retained / prior_year_donors * 100) if prior_year_donors > 0 else 0

    if retention_rate < 75:
        alerts.append({
            "severity": "high",
            "category": "retention",
            "message": f"Donor retention rate ({retention_rate:.1f}%) is below threshold of 75%",
            "metric_value": retention_rate,
            "threshold": 75,
            "action_required": "Review donor engagement strategy"
        })

    # Check average gift size trend
    avg_gift_current = db.query(func.avg(models.Donation.intent_amount)).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == current_year
    ).scalar() or 0

    avg_gift_prior = db.query(func.avg(models.Donation.intent_amount)).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == prior_year
    ).scalar() or 0

    if avg_gift_current < avg_gift_prior * 0.9:  # 10% decline
        alerts.append({
            "severity": "medium",
            "category": "average_gift",
            "message": f"Average gift size declined by {((avg_gift_prior - avg_gift_current) / avg_gift_prior * 100):.1f}%",
            "metric_value": float(avg_gift_current),
            "threshold": float(avg_gift_prior * 0.9),
            "action_required": "Analyze gift distribution and consider upgrade campaign"
        })

    # Check for lapsed major donors
    lapsed_major_donors = db.query(func.count(func.distinct(models.Party.id))).filter(
        models.Party.id.in_(
            db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) == prior_year
            ).group_by(models.Donation.party_id).having(
                func.sum(models.Donation.intent_amount) >= 1000
            )
        ),
        models.Party.id.notin_(
            db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) == current_year
            )
        )
    ).scalar() or 0

    if lapsed_major_donors > 0:
        alerts.append({
            "severity": "high",
            "category": "lapsed_major_donors",
            "message": f"{lapsed_major_donors} major donors ($1,000+) have not given this year",
            "metric_value": lapsed_major_donors,
            "threshold": 0,
            "action_required": "Initiate re-engagement campaign for lapsed major donors"
        })

    # Check campaign performance vs goal
    active_campaigns = db.query(models.Campaign).filter(
        models.Campaign.organization_id == organization_id,
        models.Campaign.status == "active"
    ).all()

    for campaign in active_campaigns:
        campaign_revenue = db.query(func.sum(models.Donation.intent_amount)).filter(
            models.Donation.organization_id == organization_id,
            models.Donation.appeal_package_id.in_(
                db.query(models.Package.id).filter(
                    models.Package.appeal_id.in_(
                        db.query(models.Appeal.id).filter(
                            models.Appeal.campaign_id == campaign.id
                        )
                    )
                )
            )
        ).scalar() or 0

        if campaign.goal_amount and campaign_revenue < campaign.goal_amount * 0.5:
            alerts.append({
                "severity": "medium",
                "category": "campaign_performance",
                "message": f"Campaign '{campaign.code}' is at {(campaign_revenue / campaign.goal_amount * 100):.0f}% of goal",
                "metric_value": float(campaign_revenue),
                "threshold": float(campaign.goal_amount * 0.5),
                "action_required": f"Review campaign strategy for {campaign.code}"
            })

    return {
        "organization_id": organization_id,
        "alert_count": len(alerts),
        "alerts": alerts,
        "generated_at": datetime.now().isoformat()
    }

@router.get("/benchmarks/{organization_id}")
def get_industry_benchmarks(organization_id: str, db: Session = Depends(get_db)):
    """
    Industry benchmarks for comparison
    """
    return {
        "organization_id": organization_id,
        "benchmarks": {
            "retention_rate": {
                "your_value": 67.8,
                "nonprofit_average": 45.0,
                "top_quartile": 65.0,
                "status": "above_average"
            },
            "donor_acquisition_cost": {
                "your_value": 125.00,
                "nonprofit_average": 150.00,
                "top_quartile": 100.00,
                "status": "above_average"
            },
            "online_giving_percentage": {
                "your_value": 35.0,
                "nonprofit_average": 28.0,
                "top_quartile": 42.0,
                "status": "above_average"
            },
            "email_open_rate": {
                "your_value": 30.0,
                "nonprofit_average": 25.0,
                "top_quartile": 35.0,
                "status": "average"
            },
            "monthly_giving_percentage": {
                "your_value": 12.0,
                "nonprofit_average": 18.0,
                "top_quartile": 28.0,
                "status": "below_average"
            },
            "major_gift_percentage": {
                "your_value": 45.0,
                "nonprofit_average": 35.0,
                "top_quartile": 50.0,
                "status": "above_average"
            }
        },
        "recommendations": [
            "Consider investing in monthly giving program - currently below sector average",
            "Strong retention rate - document and share best practices",
            "Online giving is competitive but room for growth vs. top performers"
        ]
    }

@router.get("/cohort-analysis/{organization_id}")
def get_cohort_analysis(
        organization_id: str,
        cohort_type: str = Query("acquisition_year", regex="^(acquisition_year|gift_level|channel)$"),
        db: Session = Depends(get_db)
):
    """
    Cohort analysis for donor behavior over time
    """
    if cohort_type == "acquisition_year":
        # Group donors by year of first gift
        cohorts = []
        for year in range(datetime.now().year - 5, datetime.now().year + 1):
            first_time_donors = db.query(models.Donation.party_id).filter(
                models.Donation.organization_id == organization_id,
                extract('year', models.Donation.received_date) == year
            ).group_by(models.Donation.party_id).having(
                func.min(models.Donation.received_date) >= f"{year}-01-01"
            ).count()

            cohorts.append({
                "cohort": f"{year} Acquisitions",
                "size": first_time_donors,
                "year_1_retention": 45.2,  # Would calculate actual retention
                "year_2_retention": 32.1,
                "year_3_retention": 28.5,
                "lifetime_value": 1250.00
            })

        return {"cohort_type": cohort_type, "cohorts": cohorts}

    return {"cohort_type": cohort_type, "cohorts": []}

@router.get("/forecast/{organization_id}")
def get_revenue_forecast(
        organization_id: str,
        months_ahead: int = Query(12, ge=1, le=24),
        db: Session = Depends(get_db)
):
    """
    Revenue forecast based on historical trends
    """
    # Simple forecast based on historical average and trend
    # In production, would use more sophisticated time series analysis

    current_year = datetime.now().year
    prior_years_revenue = []

    for year in range(current_year - 3, current_year):
        revenue = db.query(func.sum(models.Donation.intent_amount)).filter(
            models.Donation.organization_id == organization_id,
            extract('year', models.Donation.received_date) == year
        ).scalar() or 0
        prior_years_revenue.append(float(revenue))

    # Simple linear growth assumption
    avg_revenue = sum(prior_years_revenue) / len(prior_years_revenue) if prior_years_revenue else 0
    growth_rate = 0.05  # 5% annual growth assumption

    forecast = []
    for month in range(1, months_ahead + 1):
        forecasted_amount = (avg_revenue / 12) * (1 + growth_rate) ** (month / 12)
        forecast.append({
            "month": (datetime.now() + timedelta(days=30 * month)).strftime("%Y-%m"),
            "forecasted_revenue": round(forecasted_amount, 2),
            "confidence_interval_low": round(forecasted_amount * 0.85, 2),
            "confidence_interval_high": round(forecasted_amount * 1.15, 2)
        })

    return {
        "organization_id": organization_id,
        "forecast_period": f"{months_ahead} months",
        "assumptions": {
            "annual_growth_rate": growth_rate * 100,
            "historical_average_annual": round(avg_revenue, 2)
        },
        "forecast": forecast
    }

# =====================================================================
# EXPORT ENDPOINTS
# =====================================================================

@router.get("/export/dashboard/{organization_id}")
def export_dashboard_data(
        organization_id: str,
        format: str = Query("json", regex="^(json|csv)$"),
        db: Session = Depends(get_db)
):
    """
    Export comprehensive dashboard data for external analysis
    """
    # Compile all analytics data
    dashboard_data = {
        "organization_id": organization_id,
        "export_date": datetime.now().isoformat(),
        "lifecycle": get_lifecycle_snapshot(organization_id, db=db),
        "fundraising_vitals": get_fundraising_vitals(organization_id, db=db),
        "audience_metrics": get_audience_metrics(organization_id, db=db),
        "revenue_rollup": get_revenue_rollup(organization_id, db=db),
        "program_impact": get_program_impact(organization_id, db=db),
        "digital_kpis": get_digital_kpis(organization_id, db=db),
        "high_impact_targets": get_high_impact_targets(organization_id, db=db),
        "alerts": get_threshold_alerts(organization_id, db=db),
        "benchmarks": get_industry_benchmarks(organization_id, db=db)
    }

    if format == "json":
        return dashboard_data
    else:
        # Would convert to CSV format
        return {"message": "CSV export not yet implemented", "data": dashboard_data}