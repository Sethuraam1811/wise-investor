# main.py
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
import uvicorn

from database import get_db, engine
import models
import schemas

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Organization Management API",
    version="1.0.0",
    description="Comprehensive API for managing organizations, users, programs, donations, and related entities"
)

security = HTTPBearer()

# Dependency for authentication
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Implement your JWT verification logic here
    token = credentials.credentials
    # For now, just pass through - implement proper JWT verification
    return token

# ==================== ORGANIZATION APIs ====================

@app.get("/organizations", response_model=schemas.OrganizationListResponse, tags=["Organization"])
def list_organizations(
        status: Optional[str] = None,
        timezone: Optional[str] = None,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Organization)
    if status:
        query = query.filter(models.Organization.status == status)
    if timezone:
        query = query.filter(models.Organization.timezone == timezone)

    total = query.count()
    organizations = query.offset(offset).limit(limit).all()

    return {
        "data": organizations,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@app.post("/organizations", response_model=schemas.Organization, status_code=status.HTTP_201_CREATED, tags=["Organization"])
def create_organization(
        organization: schemas.OrganizationCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_org = models.Organization(**organization.dict())
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

@app.get("/organizations/{id}", response_model=schemas.Organization, tags=["Organization"])
def get_organization(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    org = db.query(models.Organization).filter(models.Organization.id == id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

@app.put("/organizations/{id}", response_model=schemas.Organization, tags=["Organization"])
def update_organization(
        id: UUID,
        organization: schemas.OrganizationUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_org = db.query(models.Organization).filter(models.Organization.id == id).first()
    if not db_org:
        raise HTTPException(status_code=404, detail="Organization not found")

    for key, value in organization.dict(exclude_unset=True).items():
        setattr(db_org, key, value)

    db.commit()
    db.refresh(db_org)
    return db_org

@app.delete("/organizations/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Organization"])
def delete_organization(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_org = db.query(models.Organization).filter(models.Organization.id == id).first()
    if not db_org:
        raise HTTPException(status_code=404, detail="Organization not found")

    db.delete(db_org)
    db.commit()
    return None

# ==================== USER APIs ====================

@app.get("/users", response_model=List[schemas.User], tags=["User"])
def list_users(
        organization_id: Optional[UUID] = None,
        status: Optional[str] = None,
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.User)
    if organization_id:
        query = query.filter(models.User.organization_id == organization_id)
    if status:
        query = query.filter(models.User.status == status)

    return query.offset(offset).limit(limit).all()

@app.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["User"])
def create_user(
        user: schemas.UserCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    # Hash password before storing (use passlib or bcrypt in production)
    user_data = user.dict()
    # user_data['password_hash'] = hash_password(user_data.pop('password'))
    user_data['password_hash'] = user_data.pop('password')  # Simplified for demo

    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{id}", response_model=schemas.User, tags=["User"])
def get_user(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{id}", response_model=schemas.User, tags=["User"])
def update_user(
        id: UUID,
        user: schemas.UserUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user.dict(exclude_unset=True)
    if 'password' in update_data:
        # Hash password (simplified for demo)
        update_data['password_hash'] = update_data.pop('password')

    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["User"])
def delete_user(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_user = db.query(models.User).filter(models.User.id == id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return None

# ==================== ROLE APIs ====================

@app.get("/roles", response_model=List[schemas.Role], tags=["Role"])
def list_roles(
        organization_id: Optional[UUID] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Role)
    if organization_id:
        query = query.filter(models.Role.organization_id == organization_id)
    return query.all()

@app.post("/roles", response_model=schemas.Role, status_code=status.HTTP_201_CREATED, tags=["Role"])
def create_role(
        role: schemas.RoleCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_role = models.Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@app.get("/roles/{id}", response_model=schemas.Role, tags=["Role"])
def get_role(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    role = db.query(models.Role).filter(models.Role.id == id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@app.put("/roles/{id}", response_model=schemas.Role, tags=["Role"])
def update_role(
        id: UUID,
        role: schemas.RoleUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_role = db.query(models.Role).filter(models.Role.id == id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    for key, value in role.dict(exclude_unset=True).items():
        setattr(db_role, key, value)

    db.commit()
    db.refresh(db_role)
    return db_role

@app.delete("/roles/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Role"])
def delete_role(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_role = db.query(models.Role).filter(models.Role.id == id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")

    db.delete(db_role)
    db.commit()
    return None

# ==================== PERMISSION APIs ====================

@app.get("/permissions", response_model=List[schemas.Permission], tags=["Permission"])
def list_permissions(
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    return db.query(models.Permission).all()

@app.post("/permissions", response_model=schemas.Permission, status_code=status.HTTP_201_CREATED, tags=["Permission"])
def create_permission(
        permission: schemas.PermissionCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_permission = models.Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

# ==================== USER_ROLE APIs ====================

@app.get("/user-roles", response_model=List[schemas.UserRole], tags=["UserRole"])
def list_user_roles(
        user_id: Optional[UUID] = None,
        role_id: Optional[UUID] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.UserRole)
    if user_id:
        query = query.filter(models.UserRole.user_id == user_id)
    if role_id:
        query = query.filter(models.UserRole.role_id == role_id)
    return query.all()

@app.post("/user-roles", response_model=schemas.UserRole, status_code=status.HTTP_201_CREATED, tags=["UserRole"])
def assign_role_to_user(
        user_role: schemas.UserRoleCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_user_role = models.UserRole(**user_role.dict())
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role

@app.delete("/user-roles/{user_id}/{role_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["UserRole"])
def remove_role_from_user(
        user_id: UUID,
        role_id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_user_role = db.query(models.UserRole).filter(
        models.UserRole.user_id == user_id,
        models.UserRole.role_id == role_id
    ).first()

    if not db_user_role:
        raise HTTPException(status_code=404, detail="User role assignment not found")

    db.delete(db_user_role)
    db.commit()
    return None

# ==================== ROLE_PERMISSION APIs ====================

@app.get("/role-permissions", response_model=List[schemas.RolePermission], tags=["RolePermission"])
def list_role_permissions(
        role_id: Optional[UUID] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.RolePermission)
    if role_id:
        query = query.filter(models.RolePermission.role_id == role_id)
    return query.all()

@app.post("/role-permissions", response_model=schemas.RolePermission, status_code=status.HTTP_201_CREATED, tags=["RolePermission"])
def assign_permission_to_role(
        role_permission: schemas.RolePermissionCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_role_permission = models.RolePermission(**role_permission.dict())
    db.add(db_role_permission)
    db.commit()
    db.refresh(db_role_permission)
    return db_role_permission

# ==================== PROGRAM APIs ====================

@app.get("/programs", response_model=List[schemas.Program], tags=["Program"])
def list_programs(
        organization_id: Optional[UUID] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Program)
    if organization_id:
        query = query.filter(models.Program.organization_id == organization_id)
    return query.all()

@app.post("/programs", response_model=schemas.Program, status_code=status.HTTP_201_CREATED, tags=["Program"])
def create_program(
        program: schemas.ProgramCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_program = models.Program(**program.dict())
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

@app.get("/programs/{id}", response_model=schemas.Program, tags=["Program"])
def get_program(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    program = db.query(models.Program).filter(models.Program.id == id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program

@app.put("/programs/{id}", response_model=schemas.Program, tags=["Program"])
def update_program(
        id: UUID,
        program: schemas.ProgramUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_program = db.query(models.Program).filter(models.Program.id == id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")

    for key, value in program.dict(exclude_unset=True).items():
        setattr(db_program, key, value)

    db.commit()
    db.refresh(db_program)
    return db_program

@app.delete("/programs/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Program"])
def delete_program(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_program = db.query(models.Program).filter(models.Program.id == id).first()
    if not db_program:
        raise HTTPException(status_code=404, detail="Program not found")

    db.delete(db_program)
    db.commit()
    return None

# ==================== CAMPAIGN APIs ====================

@app.get("/campaigns", response_model=List[schemas.Campaign], tags=["Campaign"])
def list_campaigns(
        organization_id: Optional[UUID] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Campaign)
    if organization_id:
        query = query.filter(models.Campaign.organization_id == organization_id)
    if status:
        query = query.filter(models.Campaign.status == status)
    return query.all()

@app.post("/campaigns", response_model=schemas.Campaign, status_code=status.HTTP_201_CREATED, tags=["Campaign"])
def create_campaign(
        campaign: schemas.CampaignCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_campaign = models.Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@app.get("/campaigns/{id}", response_model=schemas.Campaign, tags=["Campaign"])
def get_campaign(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    campaign = db.query(models.Campaign).filter(models.Campaign.id == id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@app.put("/campaigns/{id}", response_model=schemas.Campaign, tags=["Campaign"])
def update_campaign(
        id: UUID,
        campaign: schemas.CampaignUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    for key, value in campaign.dict(exclude_unset=True).items():
        setattr(db_campaign, key, value)

    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@app.delete("/campaigns/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Campaign"])
def delete_campaign(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_campaign = db.query(models.Campaign).filter(models.Campaign.id == id).first()
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(db_campaign)
    db.commit()
    return None

# ==================== DONATION APIs ====================

@app.get("/donations", response_model=List[schemas.Donation], tags=["Donation"])
def list_donations(
        organization_id: Optional[UUID] = None,
        party_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Donation)
    if organization_id:
        query = query.filter(models.Donation.organization_id == organization_id)
    if party_id:
        query = query.filter(models.Donation.party_id == party_id)
    if start_date:
        query = query.filter(models.Donation.received_date >= start_date)
    if end_date:
        query = query.filter(models.Donation.received_date <= end_date)
    return query.all()

@app.post("/donations", response_model=schemas.Donation, status_code=status.HTTP_201_CREATED, tags=["Donation"])
def create_donation(
        donation: schemas.DonationCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_donation = models.Donation(**donation.dict())
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    return db_donation

@app.get("/donations/{id}", response_model=schemas.Donation, tags=["Donation"])
def get_donation(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    donation = db.query(models.Donation).filter(models.Donation.id == id).first()
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")
    return donation

@app.put("/donations/{id}", response_model=schemas.Donation, tags=["Donation"])
def update_donation(
        id: UUID,
        donation: schemas.DonationUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_donation = db.query(models.Donation).filter(models.Donation.id == id).first()
    if not db_donation:
        raise HTTPException(status_code=404, detail="Donation not found")

    for key, value in donation.dict(exclude_unset=True).items():
        setattr(db_donation, key, value)

    db.commit()
    db.refresh(db_donation)
    return db_donation

# ==================== PAYMENT APIs ====================

@app.get("/payments", response_model=List[schemas.Payment], tags=["Payment"])
def list_payments(
        donation_id: Optional[UUID] = None,
        status: Optional[str] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Payment)
    if donation_id:
        query = query.filter(models.Payment.donation_id == donation_id)
    if status:
        query = query.filter(models.Payment.status == status)
    return query.all()

@app.post("/payments", response_model=schemas.Payment, status_code=status.HTTP_201_CREATED, tags=["Payment"])
def create_payment(
        payment: schemas.PaymentCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_payment = models.Payment(**payment.dict())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

@app.get("/payments/{id}", response_model=schemas.Payment, tags=["Payment"])
def get_payment(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@app.put("/payments/{id}", response_model=schemas.Payment, tags=["Payment"])
def update_payment(
        id: UUID,
        payment: schemas.PaymentUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_payment = db.query(models.Payment).filter(models.Payment.id == id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    for key, value in payment.dict(exclude_unset=True).items():
        setattr(db_payment, key, value)

    db.commit()
    db.refresh(db_payment)
    return db_payment

# ==================== PARTY APIs ====================

@app.get("/parties", response_model=List[schemas.Party], tags=["Party"])
def list_parties(
        organization_id: Optional[UUID] = None,
        ein: Optional[str] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Party)
    if organization_id:
        query = query.filter(models.Party.organization_id == organization_id)
    if ein:
        query = query.filter(models.Party.ein == ein)
    return query.all()

@app.post("/parties", response_model=schemas.Party, status_code=status.HTTP_201_CREATED, tags=["Party"])
def create_party(
        party: schemas.PartyCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_party = models.Party(**party.dict())
    db.add(db_party)
    db.commit()
    db.refresh(db_party)
    return db_party

@app.get("/parties/{id}", response_model=schemas.Party, tags=["Party"])
def get_party(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    party = db.query(models.Party).filter(models.Party.id == id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party

@app.put("/parties/{id}", response_model=schemas.Party, tags=["Party"])
def update_party(
        id: UUID,
        party: schemas.PartyUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_party = db.query(models.Party).filter(models.Party.id == id).first()
    if not db_party:
        raise HTTPException(status_code=404, detail="Party not found")

    for key, value in party.dict(exclude_unset=True).items():
        setattr(db_party, key, value)

    db.commit()
    db.refresh(db_party)
    return db_party

@app.delete("/parties/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Party"])
def delete_party(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_party = db.query(models.Party).filter(models.Party.id == id).first()
    if not db_party:
        raise HTTPException(status_code=404, detail="Party not found")

    db.delete(db_party)
    db.commit()
    return None

# ==================== PLEDGE APIs ====================

@app.get("/pledges", response_model=List[schemas.Pledge], tags=["Pledge"])
def list_pledges(
        organization_id: Optional[UUID] = None,
        party_id: Optional[UUID] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Pledge)
    if organization_id:
        query = query.filter(models.Pledge.organization_id == organization_id)
    if party_id:
        query = query.filter(models.Pledge.party_id == party_id)
    return query.all()

@app.post("/pledges", response_model=schemas.Pledge, status_code=status.HTTP_201_CREATED, tags=["Pledge"])
def create_pledge(
        pledge: schemas.PledgeCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_pledge = models.Pledge(**pledge.dict())
    db.add(db_pledge)
    db.commit()
    db.refresh(db_pledge)
    return db_pledge

@app.get("/pledges/{id}", response_model=schemas.Pledge, tags=["Pledge"])
def get_pledge(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    pledge = db.query(models.Pledge).filter(models.Pledge.id == id).first()
    if not pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")
    return pledge

@app.put("/pledges/{id}", response_model=schemas.Pledge, tags=["Pledge"])
def update_pledge(
        id: UUID,
        pledge: schemas.PledgeUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_pledge = db.query(models.Pledge).filter(models.Pledge.id == id).first()
    if not db_pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")

    for key, value in pledge.dict(exclude_unset=True).items():
        setattr(db_pledge, key, value)

    db.commit()
    db.refresh(db_pledge)
    return db_pledge

@app.delete("/pledges/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Pledge"])
def delete_pledge(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_pledge = db.query(models.Pledge).filter(models.Pledge.id == id).first()
    if not db_pledge:
        raise HTTPException(status_code=404, detail="Pledge not found")

    db.delete(db_pledge)
    db.commit()
    return None

# ==================== FUND APIs ====================

@app.get("/funds", response_model=List[schemas.Fund], tags=["Fund"])
def list_funds(
        organization_id: Optional[UUID] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Fund)
    if organization_id:
        query = query.filter(models.Fund.organization_id == organization_id)
    return query.all()

@app.post("/funds", response_model=schemas.Fund, status_code=status.HTTP_201_CREATED, tags=["Fund"])
def create_fund(
        fund: schemas.FundCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_fund = models.Fund(**fund.dict())
    db.add(db_fund)
    db.commit()
    db.refresh(db_fund)
    return db_fund

@app.get("/funds/{id}", response_model=schemas.Fund, tags=["Fund"])
def get_fund(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    fund = db.query(models.Fund).filter(models.Fund.id == id).first()
    if not fund:
        raise HTTPException(status_code=404, detail="Fund not found")
    return fund

@app.put("/funds/{id}", response_model=schemas.Fund, tags=["Fund"])
def update_fund(
        id: UUID,
        fund: schemas.FundUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_fund = db.query(models.Fund).filter(models.Fund.id == id).first()
    if not db_fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    for key, value in fund.dict(exclude_unset=True).items():
        setattr(db_fund, key, value)

    db.commit()
    db.refresh(db_fund)
    return db_fund

@app.delete("/funds/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Fund"])
def delete_fund(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_fund = db.query(models.Fund).filter(models.Fund.id == id).first()
    if not db_fund:
        raise HTTPException(status_code=404, detail="Fund not found")

    db.delete(db_fund)
    db.commit()
    return None

# ==================== BENEFICIARY APIs ====================

@app.get("/beneficiaries", response_model=List[schemas.Beneficiary], tags=["Beneficiary"])
def list_beneficiaries(
        organization_id: Optional[UUID] = None,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    query = db.query(models.Beneficiary)
    if organization_id:
        query = query.filter(models.Beneficiary.organization_id == organization_id)
    return query.all()

@app.post("/beneficiaries", response_model=schemas.Beneficiary, status_code=status.HTTP_201_CREATED, tags=["Beneficiary"])
def create_beneficiary(
        beneficiary: schemas.BeneficiaryCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_beneficiary = models.Beneficiary(**beneficiary.dict())
    db.add(db_beneficiary)
    db.commit()
    db.refresh(db_beneficiary)
    return db_beneficiary

@app.get("/beneficiaries/{id}", response_model=schemas.Beneficiary, tags=["Beneficiary"])
def get_beneficiary(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    beneficiary = db.query(models.Beneficiary).filter(models.Beneficiary.id == id).first()
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return beneficiary

@app.put("/beneficiaries/{id}", response_model=schemas.Beneficiary, tags=["Beneficiary"])
def update_beneficiary(
        id: UUID,
        beneficiary: schemas.BeneficiaryUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_beneficiary = db.query(models.Beneficiary).filter(models.Beneficiary.id == id).first()
    if not db_beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    for key, value in beneficiary.dict(exclude_unset=True).items():
        setattr(db_beneficiary, key, value)

    db.commit()
    db.refresh(db_beneficiary)
    return db_beneficiary

@app.delete("/beneficiaries/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Beneficiary"])
def delete_beneficiary(
        id: UUID,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token)
):
    db_beneficiary = db.query(models.Beneficiary).filter(models.Beneficiary.id == id).first()
    if not db_beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")

    db.delete(db_beneficiary)
    db.commit()
    return None


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)