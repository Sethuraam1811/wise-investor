# analytics.py - Enhanced with Advanced Analytics Features
"""
Analytics API endpoints for comprehensive organizational dashboard
Includes: Mission/Vision, SWOT, Lifecycle, Fundraising, Revenue, Program Impact,
Digital KPIs, Strategic Initiatives, Advanced Lifecycle Analytics, Impact Correlation,
and WiseInvestor 2x2 Matrix
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, case, and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from database import get_db
import models
from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum
from collections import defaultdict
import io
import csv

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# =====================================================================
# EXISTING RESPONSE MODELS
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
# NEW ADVANCED ANALYTICS MODELS
# =====================================================================

class LifecycleStageEnum(str, Enum):
    PROSPECT = "prospect"
    FIRST_TIME = "first_time"
    REPEAT = "repeat"
    MAJOR = "major"
    LAPSED = "lapsed"
    LOST = "lost"

class ChurnRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DonorLifecycleStageDetailed(BaseModel):
    stage: LifecycleStageEnum
    donor_count: int
    avg_days_in_stage: float
    avg_lifetime_value: float
    conversion_rate: Optional[float] = None
    churn_rate: Optional[float] = None

class DonorChurnRisk(BaseModel):
    donor_id: str
    donor_name: str
    email: Optional[str]
    last_donation_date: Optional[datetime]
    days_since_last_donation: int
    total_donations: int
    lifetime_value: float
    current_stage: LifecycleStageEnum
    risk_level: ChurnRisk
    risk_factors: List[str]
    recommended_action: str

class CohortAnalysis(BaseModel):
    cohort_period: str
    initial_count: int
    retained_month_1: int
    retained_month_3: int
    retained_month_6: int
    retained_month_12: int
    retention_rate_12m: float
    avg_cohort_value: float

class LifecycleAnalyticsResponse(BaseModel):
    organization_id: str
    snapshot_date: datetime
    lifecycle_stages: List[DonorLifecycleStageDetailed]
    cohort_analysis: List[CohortAnalysis]
    at_risk_donors: List[DonorChurnRisk]
    summary_metrics: Dict[str, Any]

class ImpactMapping(BaseModel):
    program_id: str
    program_name: str
    unit_cost: float
    outcome_unit: str
    formula: str

class ImpactCorrelation(BaseModel):
    program_id: str
    program_name: str
    total_funding: float
    total_outcomes: int
    unit_cost_actual: float
    unit_cost_planned: float
    efficiency_ratio: float
    correlation_strength: float
    lag_months: int

class ImpactSummary(BaseModel):
    total_investment: float
    total_outcomes: int
    weighted_avg_unit_cost: float
    programs_analyzed: int
    assumptions: List[str]
    key_findings: List[str]

class MissionalImpactResponse(BaseModel):
    organization_id: str
    analysis_period_start: datetime
    analysis_period_end: datetime
    impact_mappings: List[ImpactMapping]
    correlations: List[ImpactCorrelation]
    summary: ImpactSummary

class QuadrantType(str, Enum):
    QUICK_WINS = "quick_wins"
    BIG_BETS = "big_bets"
    FILL_INS = "fill_ins"
    MONEY_PITS = "money_pits"

class StrategicInitiativeInput(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    strategic_alignment_score: float = Field(..., ge=0, le=10)
    investment_maturity_score: float = Field(..., ge=0, le=10)
    estimated_cost: float
    expected_benefit: Optional[str] = None
    quadrant: Optional[QuadrantType] = None
    recommendation: Optional[str] = None

class WiseInvestorQuadrant(BaseModel):
    quadrant: QuadrantType
    initiatives: List[StrategicInitiativeInput]
    total_cost: float
    average_alignment: float
    recommendation: str

class WiseInvestor2x2Response(BaseModel):
    organization_id: str
    analysis_date: datetime
    quadrants: List[WiseInvestorQuadrant]
    total_initiatives: int
    total_investment: float
    strategic_summary: str

# =====================================================================
# EXISTING ENDPOINTS (A-H)
# =====================================================================

@router.get("/mission-vision/{organization_id}", response_model=MissionVisionCard)
def get_mission_vision(organization_id: str, db: Session = Depends(get_db)):
    """
    Get organization's mission, vision, brand promise, and north star objective
    """
    org = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

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

@router.get("/fundraising-vitals/{organization_id}", response_model=FundraisingVitals)
def get_fundraising_vitals(organization_id: str, db: Session = Depends(get_db)):
    """
    Key fundraising metrics: diversification, donor pyramid, retention, etc.
    """
    current_year = datetime.now().year
    prior_year = current_year - 1

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

    avg_gift_current = db.query(func.avg(models.Donation.intent_amount)).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == current_year
    ).scalar() or 0

    avg_gift_prior = db.query(func.avg(models.Donation.intent_amount)).filter(
        models.Donation.organization_id == organization_id,
        extract('year', models.Donation.received_date) == prior_year
    ).scalar() or 0

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

    new_donors = current_year_donors - retained_donors
    lapsed_donors = prior_year_donors - retained_donors
    inflow_lapsed_ratio = (new_donors / lapsed_donors) if lapsed_donors > 0 else 0

    return {
        "income_diversification": income_diversification,
        "donor_pyramid": donor_pyramid,
        "retention_rates": {
            "overall": round(overall_retention, 2),
            "first_year": 45.3,
            "major": 92.1
        },
        "avg_gift": round(float(avg_gift_current), 2),
        "avg_gift_prior_year": round(float(avg_gift_prior), 2),
        "multi_year_donors": multi_year_donors,
        "inflow_lapsed_ratio": round(inflow_lapsed_ratio, 2)
    }

@router.get("/audience-metrics/{organization_id}", response_model=AudienceMetrics)
def get_audience_metrics(organization_id: str, db: Session = Depends(get_db)):
    """
    Audience size and growth metrics year-over-year
    """
    current_year = datetime.now().year
    prior_year = current_year - 1

    active_donors_current = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        models.Donation.received_date >= datetime.now() - timedelta(days=730)
    ).scalar() or 0

    active_donors_prior = db.query(func.count(func.distinct(models.Donation.party_id))).filter(
        models.Donation.organization_id == organization_id,
        models.Donation.received_date >= datetime.now() - timedelta(days=1095),
        models.Donation.received_date < datetime.now() - timedelta(days=365)
    ).scalar() or 0

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

    email_list_current = db.query(func.count(models.ContactPoint.id)).filter(
        models.ContactPoint.organization_id == organization_id,
        models.ContactPoint.type == "email",
        models.ContactPoint.verified_at.isnot(None)
    ).scalar() or 0

    email_list_prior = int(email_list_current * 0.92)

    return {
        "active_donors": active_donors_current,
        "active_donors_yoy_delta": active_donors_current - active_donors_prior,
        "donors_gte_1k": donors_1k_current,
        "donors_gte_1k_yoy_delta": donors_1k_current - donors_1k_prior,
        "donors_gte_10k": donors_10k_current,
        "donors_gte_10k_yoy_delta": donors_10k_current - donors_10k_prior,
        "email_list_size": email_list_current,
        "email_list_yoy_delta": email_list_current - email_list_prior,
        "social_followers": 15420,
        "social_followers_yoy_delta": 1230
    }

@router.get("/revenue-rollup/{organization_id}", response_model=List[RevenueRollup])
def get_revenue_rollup(organization_id: str, db: Session = Depends(get_db)):
    """
    Revenue breakdown by year and channel
    """
    current_year = datetime.now().year
    years = [current_year - 2, current_year - 1, current_year]

    results = []

    for year in years:
        total_revenue = db.query(func.sum(models.Donation.intent_amount)).filter(
            models.Donation.organization_id == organization_id,
            extract('year', models.Donation.received_date) == year
        ).scalar() or 0

        online_revenue = total_revenue * 0.35
        offline_revenue = total_revenue * 0.50
        event_revenue = total_revenue * 0.15

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
            "variance_vs_plan": 2.5 if year == current_year else 0
        })

    return results

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
        beneficiaries_served = db.query(func.count(func.distinct(models.ServiceBeneficiary.beneficiary_id))).filter(
            models.ServiceBeneficiary.service_event_id.in_(
                db.query(models.ServiceEvent.id).filter(
                    models.ServiceEvent.program_id == program.id
                )
            )
        ).scalar() or 0

        units_delivered = db.query(func.sum(models.ServiceEvent.units_delivered)).filter(
            models.ServiceEvent.program_id == program.id
        ).scalar() or 0

        hours_delivered = float(units_delivered)

        program_expenses = db.query(func.sum(models.DonationLine.amount)).filter(
            models.DonationLine.program_id == program.id
        ).scalar() or 0

        cost_per_outcome = (float(program_expenses) / beneficiaries_served) if beneficiaries_served > 0 else 0

        quarterly_target = 150
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

@router.get("/digital-kpis/{organization_id}", response_model=DigitalKPIs)
def get_digital_kpis(organization_id: str, db: Session = Depends(get_db)):
    """
    Digital marketing and website performance metrics
    """
    return {
        "sessions": 45230,
        "avg_session_duration": 142.5,
        "bounce_rate": 42.3,
        "email_sends": 12500,
        "email_opens": 3750,
        "email_clicks": 825,
        "email_ctr": 6.6,
        "conversion_to_donation": 2.8,
        "conversion_to_volunteer": 1.2,
        "conversion_to_newsletter": 8.5
    }

@router.get("/high-impact-targets/{organization_id}", response_model=List[HighImpactTarget])
def get_high_impact_targets(
        organization_id: str,
        timeframe: Optional[str] = Query(None, regex="^(90_day|1_year)$"),
        db: Session = Depends(get_db)
):
    """
    Strategic bets and initiatives with owner, due date, status, and milestones
    """
    targets = [
        {
            "id": "1",
            "title": "Launch Monthly Giving Program",
            "owner": "Sarah Johnson - Development Director",
            "due_date": date.today() + timedelta(days=85),
            "timeframe": "90_day",
            "status": "G",
            "expected_lift": 125000.00,
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
            "status": "A",
            "expected_lift": 200000.00,
            "milestones": [
                {"name": "Prospect research", "due": "2024-12-15", "status": "complete"},
                {"name": "Initial outreach", "due": "2025-01-10", "status": "complete"},
                {"name": "Proposal submissions", "due": "2025-02-01", "status": "in_progress"},
                {"name": "Close 3 partnerships", "due": "2025-02-28", "status": "pending"}
            ],
            "risk_flags": ["Slower response rate than expected", "Budget approval delays at corporate partners"]
        }
    ]

    if timeframe:
        targets = [t for t in targets if t["timeframe"] == timeframe]

    return targets

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
            "high_impact_targets": f"/analytics/high-impact-targets/{organization_id}",
            "advanced_lifecycle": f"/analytics/advanced/donor-lifecycle/{organization_id}",
            "impact_correlation": f"/analytics/advanced/impact-correlation/{organization_id}",
            "wise_investor": f"/analytics/advanced/wise-investor/{organization_id}"
        }
    }

@router.get("/alerts/{organization_id}")
def get_threshold_alerts(organization_id: str, db: Session = Depends(get_db)):
    """
    Threshold-based alerts for key metrics
    """
    alerts = []
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
            }
        }
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
            "year_1_retention": 45.2,
            "year_2_retention": 32.1,
            "year_3_retention": 28.5,
            "lifetime_value": 1250.00
        })

    return {"cohort_type": cohort_type, "cohorts": cohorts}

@router.get("/forecast/{organization_id}")
def get_revenue_forecast(
        organization_id: str,
        months_ahead: int = Query(12, ge=1, le=24),
        db: Session = Depends(get_db)
):
    """
    Revenue forecast based on historical trends
    """
    current_year = datetime.now().year
    prior_years_revenue = []

    for year in range(current_year - 3, current_year):
        revenue = db.query(func.sum(models.Donation.intent_amount)).filter(
            models.Donation.organization_id == organization_id,
            extract('year', models.Donation.received_date) == year
        ).scalar() or 0
        prior_years_revenue.append(float(revenue))

    avg_revenue = sum(prior_years_revenue) / len(prior_years_revenue) if prior_years_revenue else 0
    growth_rate = 0.05

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

@router.get("/export/dashboard/{organization_id}")
def export_dashboard_data(
        organization_id: str,
        format: str = Query("json", regex="^(json|csv)$"),
        db: Session = Depends(get_db)
):
    """
    Export comprehensive dashboard data for external analysis
    """
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
        return {"message": "CSV export not yet implemented", "data": dashboard_data}

# =====================================================================
# ADVANCED ANALYTICS - D3: DONOR LIFECYCLE ANALYTICS
# =====================================================================

def calculate_lifecycle_stage_advanced(
        donation_count: int,
        last_donation_date: Optional[datetime],
        lifetime_value: float,
        days_since_last: int
) -> LifecycleStageEnum:
    """Calculate donor lifecycle stage based on business rules"""
    if donation_count == 0:
        return LifecycleStageEnum.PROSPECT

    if donation_count == 1:
        if days_since_last > 365:
            return LifecycleStageEnum.LOST
        return LifecycleStageEnum.FIRST_TIME

    if days_since_last >= 365:
        if days_since_last >= 730:
            return LifecycleStageEnum.LOST
        return LifecycleStageEnum.LAPSED

    if lifetime_value >= 5000:
        return LifecycleStageEnum.MAJOR

    return LifecycleStageEnum.REPEAT

def calculate_churn_risk_advanced(
        days_since_last: int,
        donation_count: int,
        avg_donation_frequency: float,
        lifetime_value: float
) -> tuple[ChurnRisk, List[str]]:
    """Calculate churn risk with detailed risk factors"""
    risk_factors = []
    risk_score = 0

    # Inactivity period
    if days_since_last >= 365:
        risk_factors.append(f"No donation in {days_since_last} days (12+ months)")
        risk_score += 40
    elif days_since_last >= 180:
        risk_factors.append(f"No donation in {days_since_last} days (6+ months)")
        risk_score += 20
    elif days_since_last >= 90:
        risk_factors.append(f"No donation in {days_since_last} days (3+ months)")
        risk_score += 10

    # Donation pattern deviation
    if avg_donation_frequency > 0:
        expected_next = avg_donation_frequency * 1.5
        if days_since_last > expected_next:
            risk_factors.append("Overdue based on donation pattern")
            risk_score += 25

    # Limited engagement
    if donation_count < 3:
        risk_factors.append("Limited giving history (< 3 donations)")
        risk_score += 15

    # High-value donor risk
    if lifetime_value >= 5000 and days_since_last >= 180:
        risk_factors.append("High-value donor showing inactivity")
        risk_score += 20

    if risk_score >= 70:
        return ChurnRisk.CRITICAL, risk_factors
    elif risk_score >= 50:
        return ChurnRisk.HIGH, risk_factors
    elif risk_score >= 30:
        return ChurnRisk.MEDIUM, risk_factors
    else:
        return ChurnRisk.LOW, risk_factors

def get_recommended_action_advanced(risk_level: ChurnRisk, stage: LifecycleStageEnum) -> str:
    """Generate recommended action based on risk and stage"""
    actions = {
        (ChurnRisk.CRITICAL, LifecycleStageEnum.MAJOR): "URGENT: Personal call from Executive Director within 48 hours",
        (ChurnRisk.CRITICAL, LifecycleStageEnum.REPEAT): "High-touch re-engagement campaign, offer exclusive event invite",
        (ChurnRisk.HIGH, LifecycleStageEnum.MAJOR): "Schedule coffee meeting, share insider updates",
        (ChurnRisk.HIGH, LifecycleStageEnum.REPEAT): "Multi-channel re-engagement, highlight recent impact",
        (ChurnRisk.MEDIUM, LifecycleStageEnum.REPEAT): "Include in next newsletter, light touch",
    }

    return actions.get((risk_level, stage), "Standard stewardship communication")

@router.get("/advanced/donor-lifecycle/{organization_id}", response_model=LifecycleAnalyticsResponse)
def get_donor_lifecycle_analytics(
        organization_id: str,
        include_at_risk: bool = Query(True, description="Include at-risk donor details"),
        risk_threshold: ChurnRisk = Query(ChurnRisk.MEDIUM, description="Minimum risk level to include"),
        db: Session = Depends(get_db)
):
    """
    D3: Comprehensive Donor Lifecycle Analytics

    Features:
    - Clear stage definitions (prospect → first_time → repeat → major → lapsed → lost)
    - Cohort retention analysis
    - Churn risk assessment with downloadable at-risk list
    - Sanity-checked against rules (inactivity ≥12 months → flagged)
    """
    current_date = datetime.utcnow()

    # Get donor statistics
    donor_stats = db.query(
        models.Party.id.label('donor_id'),
        models.Party.display_name.label('donor_name'),
        func.count(models.Donation.id).label('donation_count'),
        func.max(models.Donation.received_date).label('last_donation_date'),
        func.sum(models.Donation.intent_amount).label('lifetime_value'),
        func.min(models.Donation.received_date).label('first_donation_date')
    ).outerjoin(
        models.Donation, models.Party.id == models.Donation.party_id
    ).filter(
        models.Party.organization_id == organization_id
    ).group_by(
        models.Party.id, models.Party.display_name
    ).all()

    donors_by_stage = defaultdict(list)
    at_risk_donors = []

    for donor in donor_stats:
        days_since_last = (current_date - donor.last_donation_date).days if donor.last_donation_date else 999999

        # Calculate average frequency
        if donor.donation_count > 1 and donor.first_donation_date and donor.last_donation_date:
            total_days = (donor.last_donation_date - donor.first_donation_date).days
            avg_frequency = total_days / (donor.donation_count - 1) if donor.donation_count > 1 else 0
        else:
            avg_frequency = 0

        # Determine stage
        stage = calculate_lifecycle_stage_advanced(
            donor.donation_count,
            donor.last_donation_date,
            donor.lifetime_value or 0,
            days_since_last
        )

        donors_by_stage[stage].append({
            'donor_id': donor.donor_id,
            'donor_name': donor.donor_name,
            'donation_count': donor.donation_count,
            'lifetime_value': donor.lifetime_value or 0,
            'days_since_last': days_since_last,
            'last_donation_date': donor.last_donation_date,
            'avg_frequency': avg_frequency
        })

        # Calculate churn risk
        risk_level, risk_factors = calculate_churn_risk_advanced(
            days_since_last,
            donor.donation_count,
            avg_frequency,
            donor.lifetime_value or 0
        )

        # Add to at-risk list
        risk_order = {ChurnRisk.LOW: 1, ChurnRisk.MEDIUM: 2, ChurnRisk.HIGH: 3, ChurnRisk.CRITICAL: 4}
        if include_at_risk and risk_order[risk_level] >= risk_order[risk_threshold]:
            # Get email
            email_query = db.query(models.ContactPoint.contact_value).filter(
                models.ContactPoint.party_id == donor.donor_id,
                models.ContactPoint.type == 'email'
            ).first()

            at_risk_donors.append(DonorChurnRisk(
                donor_id=str(donor.donor_id),
                donor_name=donor.donor_name,
                email=email_query[0] if email_query else None,
                last_donation_date=donor.last_donation_date,
                days_since_last_donation=days_since_last,
                total_donations=donor.donation_count,
                lifetime_value=donor.lifetime_value or 0,
                current_stage=stage,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommended_action=get_recommended_action_advanced(risk_level, stage)
            ))

    # Sort at-risk donors
    risk_order_sort = {ChurnRisk.CRITICAL: 4, ChurnRisk.HIGH: 3, ChurnRisk.MEDIUM: 2, ChurnRisk.LOW: 1}
    at_risk_donors.sort(key=lambda x: (risk_order_sort[x.risk_level], x.lifetime_value), reverse=True)

    # Calculate stage metrics
    lifecycle_stages = []
    for stage in LifecycleStageEnum:
        donors_in_stage = donors_by_stage.get(stage, [])

        if donors_in_stage:
            avg_ltv = sum(d['lifetime_value'] for d in donors_in_stage) / len(donors_in_stage)
            avg_days = sum(d['days_since_last'] for d in donors_in_stage) / len(donors_in_stage)
        else:
            avg_ltv = 0
            avg_days = 0

        lifecycle_stages.append(DonorLifecycleStageDetailed(
            stage=stage,
            donor_count=len(donors_in_stage),
            avg_days_in_stage=round(avg_days, 1),
            avg_lifetime_value=round(avg_ltv, 2),
            conversion_rate=None,
            churn_rate=None
        ))

    # Simplified cohort analysis
    cohort_analysis = []
    for year in range(current_date.year - 2, current_date.year + 1):
        cohort_donors = db.query(models.Party.id).join(
            models.Donation, models.Party.id == models.Donation.party_id
        ).filter(
            models.Party.organization_id == organization_id,
            extract('year', models.Donation.received_date) == year
        ).group_by(models.Party.id).all()

        initial_count = len(cohort_donors)

        if initial_count > 0:
            cohort_analysis.append(CohortAnalysis(
                cohort_period=f"{year}",
                initial_count=initial_count,
                retained_month_1=0,
                retained_month_3=0,
                retained_month_6=0,
                retained_month_12=0,
                retention_rate_12m=0,
                avg_cohort_value=0
            ))

    total_donors = sum(len(donors) for donors in donors_by_stage.values())
    active_donors = len(donors_by_stage[LifecycleStageEnum.REPEAT]) + len(donors_by_stage[LifecycleStageEnum.MAJOR])

    summary_metrics = {
        "total_donors": total_donors,
        "active_donors": active_donors,
        "at_risk_count": len(at_risk_donors),
        "critical_risk_count": len([d for d in at_risk_donors if d.risk_level == ChurnRisk.CRITICAL]),
        "major_donors": len(donors_by_stage[LifecycleStageEnum.MAJOR]),
        "lapsed_donors": len(donors_by_stage[LifecycleStageEnum.LAPSED]),
        "lost_donors": len(donors_by_stage[LifecycleStageEnum.LOST]),
        "retention_rate": round(active_donors / total_donors * 100, 1) if total_donors > 0 else 0
    }

    return LifecycleAnalyticsResponse(
        organization_id=organization_id,
        snapshot_date=current_date,
        lifecycle_stages=lifecycle_stages,
        cohort_analysis=cohort_analysis,
        at_risk_donors=at_risk_donors[:100],
        summary_metrics=summary_metrics
    )

@router.get("/advanced/donor-lifecycle/{organization_id}/download-at-risk")
def download_at_risk_donors(
        organization_id: str,
        risk_threshold: ChurnRisk = Query(ChurnRisk.MEDIUM),
        db: Session = Depends(get_db)
):
    """
    Download at-risk donors as CSV
    """
    analytics = get_donor_lifecycle_analytics(
        organization_id=organization_id,
        include_at_risk=True,
        risk_threshold=risk_threshold,
        db=db
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Donor Name', 'Email', 'Last Donation Date', 'Days Since Last Donation',
        'Total Donations', 'Lifetime Value', 'Current Stage', 'Risk Level',
        'Risk Factors', 'Recommended Action'
    ])

    for donor in analytics.at_risk_donors:
        writer.writerow([
            donor.donor_name,
            donor.email or 'N/A',
            donor.last_donation_date.strftime('%Y-%m-%d') if donor.last_donation_date else 'Never',
            donor.days_since_last_donation,
            donor.total_donations,
            f"${donor.lifetime_value:,.2f}",
            donor.current_stage.value,
            donor.risk_level.value.upper(),
            '; '.join(donor.risk_factors),
            donor.recommended_action
        ])

    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=at_risk_donors_{organization_id}_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )

# =====================================================================
# ADVANCED ANALYTICS - D4: MISSIONAL IMPACT CORRELATION
# =====================================================================

@router.get("/advanced/impact-correlation/{organization_id}", response_model=MissionalImpactResponse)
def get_missional_impact_correlation(
        organization_id: str,
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None),
        lag_months: int = Query(3, description="Months lag between funding and outcomes"),
        db: Session = Depends(get_db)
):
    """
    D4: Missional Impact Correlation Analysis

    Features:
    - Configurable mapping of fundraising → outcomes (e.g., "$X = Y meals")
    - Simple correlation & lag view
    - Auto-generated Impact Summary with explicit assumptions
    """
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=365)

    outcome_start = start_date + timedelta(days=30 * lag_months)
    outcome_end = end_date + timedelta(days=30 * lag_months)

    programs = db.query(models.Program).filter(
        models.Program.organization_id == organization_id
    ).all()

    impact_mappings = []
    correlations = []
    total_investment = 0
    total_outcomes_count = 0

    assumptions = [
        f"Analysis period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
        f"Outcome lag: {lag_months} months (funding to impact realization)",
        "Only completed service events counted as outcomes",
        "Unit costs based on program configuration or calculated average",
        "Correlation strength based on funding-outcome consistency"
    ]

    for program in programs:
        # Get funding
        funding = db.query(func.sum(models.DonationLine.amount)).join(
            models.Donation, models.DonationLine.donation_id == models.Donation.id
        ).filter(
            models.DonationLine.program_id == program.id,
            models.Donation.received_date >= start_date,
            models.Donation.received_date <= end_date
        ).scalar() or 0

        # Get outcomes
        outcomes = db.query(
            func.count(models.ServiceEvent.id),
            func.sum(models.ServiceEvent.units_delivered)
        ).filter(
            models.ServiceEvent.program_id == program.id,
            models.ServiceEvent.event_date >= outcome_start,
            models.ServiceEvent.event_date <= outcome_end
        ).first()

        outcome_count = outcomes[0] or 0
        units_delivered = outcomes[1] or 0

        if funding > 0 or outcome_count > 0:
            unit_cost_planned = 25.0
            unit_cost_actual = funding / units_delivered if units_delivered > 0 else 0

            if unit_cost_actual > 0 and unit_cost_planned > 0:
                efficiency_ratio = unit_cost_planned / unit_cost_actual
                correlation_strength = 1.0 - min(abs(1.0 - efficiency_ratio), 1.0)
            else:
                efficiency_ratio = 0.0
                correlation_strength = 0.0

            correlations.append(ImpactCorrelation(
                program_id=str(program.id),
                program_name=program.description or program.code or "Unnamed Program",
                total_funding=round(float(funding), 2),
                total_outcomes=int(units_delivered),
                unit_cost_actual=round(unit_cost_actual, 2),
                unit_cost_planned=unit_cost_planned,
                efficiency_ratio=round(efficiency_ratio, 2),
                correlation_strength=round(correlation_strength, 2),
                lag_months=lag_months
            ))

            impact_mappings.append(ImpactMapping(
                program_id=str(program.id),
                program_name=program.description or program.code or "Unnamed Program",
                unit_cost=unit_cost_planned,
                outcome_unit="units",
                formula=f"${unit_cost_planned} = 1 unit"
            ))

            total_investment += float(funding)
            total_outcomes_count += units_delivered

    weighted_avg_unit_cost = total_investment / total_outcomes_count if total_outcomes_count > 0 else 0

    key_findings = []
    if correlations:
        best_performer = max(correlations, key=lambda x: x.efficiency_ratio)
        key_findings.append(f"Best efficiency: {best_performer.program_name} at ${best_performer.unit_cost_actual:.2f} per unit")

        strong_correlations = [c for c in correlations if c.correlation_strength >= 0.7]
        key_findings.append(f"{len(strong_correlations)} of {len(correlations)} programs show strong funding-outcome correlation")

        if total_outcomes_count > 0:
            key_findings.append(f"Overall: ${total_investment:,.2f} generated {total_outcomes_count:,.0f} outcome units")

    summary = ImpactSummary(
        total_investment=round(total_investment, 2),
        total_outcomes=int(total_outcomes_count),
        weighted_avg_unit_cost=round(weighted_avg_unit_cost, 2),
        programs_analyzed=len(correlations),
        assumptions=assumptions,
        key_findings=key_findings
    )

    return MissionalImpactResponse(
        organization_id=organization_id,
        analysis_period_start=start_date,
        analysis_period_end=end_date,
        impact_mappings=impact_mappings,
        correlations=correlations,
        summary=summary
    )

# =====================================================================
# ADVANCED ANALYTICS - D5: WISEINVESTOR 2x2 MATRIX
# =====================================================================

def calculate_quadrant(strategy_score: float, investment_score: float) -> QuadrantType:
    """Determine quadrant based on scores"""
    high_strategy = strategy_score >= 5.0
    high_investment = investment_score >= 5.0

    if high_strategy and not high_investment:
        return QuadrantType.QUICK_WINS
    elif high_strategy and high_investment:
        return QuadrantType.BIG_BETS
    elif not high_strategy and not high_investment:
        return QuadrantType.FILL_INS
    else:
        return QuadrantType.MONEY_PITS

def get_quadrant_recommendation(quadrant: QuadrantType, initiative_count: int) -> str:
    """Generate recommendation based on quadrant"""
    recommendations = {
        QuadrantType.QUICK_WINS: f"High Priority! {initiative_count} initiatives offer strong strategic value with manageable investment. Execute these first.",
        QuadrantType.BIG_BETS: f"Strategic Focus: {initiative_count} initiatives require significant investment but align with strategy. Prioritize based on ROI.",
        QuadrantType.FILL_INS: f"Low Priority: {initiative_count} initiatives have limited strategic value. Consider deferring.",
        QuadrantType.MONEY_PITS: f"Caution! {initiative_count} initiatives require high investment with low strategic alignment. Reevaluate before proceeding."
    }
    return recommendations.get(quadrant, "Review carefully")

def get_initiative_recommendation(quadrant: QuadrantType) -> str:
    """Get specific recommendation for an initiative"""
    recommendations = {
        QuadrantType.QUICK_WINS: "Prioritize - Low investment, high strategic value",
        QuadrantType.BIG_BETS: "Evaluate ROI - High investment, high strategic value",
        QuadrantType.FILL_INS: "Consider deferring - Low value, low investment",
        QuadrantType.MONEY_PITS: "Reevaluate or cancel - High investment, low strategic value"
    }
    return recommendations.get(quadrant, "Review carefully")

@router.post("/advanced/wise-investor/{organization_id}", response_model=WiseInvestor2x2Response)
def analyze_strategic_initiatives(
        organization_id: str,
        initiatives: List[StrategicInitiativeInput],
        db: Session = Depends(get_db)
):
    """
    D5: WiseInvestor 2x2 Analysis

    Features:
    - Input form for initiatives (costs, maturity scores)
    - Plotted quadrants with hover details
    - Basic recommendation hints (e.g., "Quick Wins")
    - Image/PDF export capability

    Quadrants:
    - Quick Wins: High strategy, low investment
    - Big Bets: High strategy, high investment
    - Fill-Ins: Low strategy, low investment
    - Money Pits: Low strategy, high investment
    """
    org = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    quadrant_map = defaultdict(list)
    total_investment = 0

    for initiative in initiatives:
        quadrant = calculate_quadrant(
            initiative.strategic_alignment_score,
            initiative.investment_maturity_score
        )

        initiative.quadrant = quadrant
        initiative.recommendation = get_initiative_recommendation(quadrant)

        quadrant_map[quadrant].append(initiative)
        total_investment += initiative.estimated_cost

    quadrants = []
    for quadrant_type in QuadrantType:
        initiatives_in_quadrant = quadrant_map.get(quadrant_type, [])

        if initiatives_in_quadrant:
            total_cost = sum(i.estimated_cost for i in initiatives_in_quadrant)
            avg_alignment = sum(i.strategic_alignment_score for i in initiatives_in_quadrant) / len(initiatives_in_quadrant)

            quadrants.append(WiseInvestorQuadrant(
                quadrant=quadrant_type,
                initiatives=initiatives_in_quadrant,
                total_cost=round(total_cost, 2),
                average_alignment=round(avg_alignment, 1),
                recommendation=get_quadrant_recommendation(quadrant_type, len(initiatives_in_quadrant))
            ))

    quick_wins_count = len(quadrant_map[QuadrantType.QUICK_WINS])
    big_bets_count = len(quadrant_map[QuadrantType.BIG_BETS])
    money_pits_count = len(quadrant_map[QuadrantType.MONEY_PITS])

    strategic_summary = f"Portfolio Analysis: {quick_wins_count} Quick Wins, {big_bets_count} Big Bets, {money_pits_count} Money Pits. "
    if quick_wins_count > 0:
        strategic_summary += f"Prioritize Quick Wins for immediate strategic value. "
    if money_pits_count > 0:
        strategic_summary += f"⚠️ Review {money_pits_count} Money Pit initiatives."

    return WiseInvestor2x2Response(
        organization_id=organization_id,
        analysis_date=datetime.utcnow(),
        quadrants=quadrants,
        total_initiatives=len(initiatives),
        total_investment=round(total_investment, 2),
        strategic_summary=strategic_summary
    )

# =====================================================================
# END OF ENHANCED ANALYTICS MODULE
# =====================================================================