# phase2/sprint1/app.py

import uuid

from fastapi import FastAPI, HTTPException
from typing import List, Dict, Any
from datetime import datetime

from phase2.sprint1.schema.schema import CreateLeadSchema, CreateAccountSchema

app = FastAPI(title="CRM Mock API", description="Mock API for testing CRM operations")

leads_db: Dict[str, Dict[str, Any]] = {}
accounts_db: Dict[str, Dict[str, Any]] = {}

@app.get("/")
def read_root():
    return {"message": "CRM Mock API is running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "leads_count": len(leads_db),
        "accounts_count": len(accounts_db)
    }

@app.post("/leads")
def create_lead(lead: CreateLeadSchema):
    """Create a new lead in the CRM system"""
    lead_id = str(uuid.uuid4())
    lead_data = {
        "id": lead_id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "company": lead.company,
        "notes": lead.notes,
        "created_at": datetime.now().isoformat(),
        "status": "new"
    }
    
    leads_db[lead_id] = lead_data
    return {
        "success": True,
        "message": "Lead created successfully",
        "data": lead_data
    }

@app.get("/leads")
def get_leads():
    """Get all leads"""
    return {
        "success": True,
        "data": list(leads_db.values()),
        "count": len(leads_db)
    }

@app.get("/leads/{lead_id}")
def get_lead(lead_id: str):
    """Get a specific lead by ID"""
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    return {
        "success": True,
        "data": leads_db[lead_id]
    }

@app.put("/leads/{lead_id}")
def update_lead(lead_id: str, lead: CreateLeadSchema):
    """Update an existing lead"""
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    leads_db[lead_id].update({
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "company": lead.company,
        "notes": lead.notes,
        "updated_at": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": "Lead updated successfully",
        "data": leads_db[lead_id]
    }

@app.delete("/leads/{lead_id}")
def delete_lead(lead_id: str):
    """Delete a lead"""
    if lead_id not in leads_db:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    deleted_lead = leads_db.pop(lead_id)
    return {
        "success": True,
        "message": "Lead deleted successfully",
        "data": deleted_lead
    }

@app.post("/accounts")
def create_account(account: CreateAccountSchema):
    """Create a new account in the CRM system"""
    account_id = str(uuid.uuid4())
    account_data = {
        "id": account_id,
        "name": account.name,
        "industry": account.industry,
        "phone": account.phone,
        "email": account.email,
        "website": account.website,
        "address": account.address,
        "notes": account.notes,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    accounts_db[account_id] = account_data
    return {
        "success": True,
        "message": "Account created successfully",
        "data": account_data
    }

@app.get("/accounts")
def get_accounts():
    """Get all accounts"""
    return {
        "success": True,
        "data": list(accounts_db.values()),
        "count": len(accounts_db)
    }

@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    """Get a specific account by ID"""
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    return {
        "success": True,
        "data": accounts_db[account_id]
    }

@app.put("/accounts/{account_id}")
def update_account(account_id: str, account: CreateAccountSchema):
    """Update an existing account"""
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    accounts_db[account_id].update({
        "name": account.name,
        "industry": account.industry,
        "phone": account.phone,
        "email": account.email,
        "website": account.website,
        "address": account.address,
        "notes": account.notes,
        "updated_at": datetime.now().isoformat()
    })
    
    return {
        "success": True,
        "message": "Account updated successfully",
        "data": accounts_db[account_id]
    }

@app.delete("/accounts/{account_id}")
def delete_account(account_id: str):
    """Delete an account"""
    if account_id not in accounts_db:
        raise HTTPException(status_code=404, detail="Account not found")
    
    deleted_account = accounts_db.pop(account_id)
    return {
        "success": True,
        "message": "Account deleted successfully",
        "data": deleted_account
    }

@app.delete("/clear-all")
def clear_all_data():
    """Clear all data from the mock database"""
    global leads_db, accounts_db
    leads_count = len(leads_db)
    accounts_count = len(accounts_db)
    
    leads_db.clear()
    accounts_db.clear()
    
    return {
        "success": True,
        "message": "All data cleared successfully",
        "cleared": {
            "leads": leads_count,
            "accounts": accounts_count
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
