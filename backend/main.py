
from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from models.database_models import (

    Base, League, Currency, ItemBase, ModGroup, 

    CurrencyExchangeRate, ProfitOpportunity

)

from scripts.scheduler import DataScheduler

from datetime import datetime

import uvicorn



app = FastAPI(

    title="PoE2 Profit Optimizer API",

    description="Path of Exile 2 Crafting Profit Optimization System",

    version="0.2.0"

)



# CORS settings

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



# Database connection

engine = create_engine('sqlite:///poe2_profit_optimizer.db')

SessionLocal = sessionmaker(bind=engine)



# Initialize scheduler

scheduler = DataScheduler()



@app.on_event("startup")

async def startup_event():

    """Start scheduler on server startup"""

    scheduler.start()

    print("Scheduler started")



@app.on_event("shutdown")

async def shutdown_event():

    """Stop scheduler on server shutdown"""

    scheduler.stop()

    print("Scheduler stopped")



@app.get("/")

def read_root():

    return {

        "message": "PoE2 Profit Optimizer API",

        "version": "0.2.0",

        "status": "running",

        "scheduler_jobs": len(scheduler.scheduler.get_jobs()),

        "timestamp": datetime.now().isoformat()

    }



@app.get("/health")

def health_check():

    return {

        "status": "healthy",

        "database": "connected",

        "scheduler": "active" if scheduler.scheduler.running else "stopped",

        "timestamp": datetime.now().isoformat()

    }



@app.get("/api/leagues")

def get_leagues():

    """Get all leagues"""

    session = SessionLocal()

    try:

        leagues = session.query(League).all()

        return {

            "count": len(leagues),

            "leagues": [

                {

                    "id": l.id,

                    "name": l.name,

                    "is_active": l.is_active,

                    "realm": l.realm,

                    "type": l.type

                } for l in leagues

            ]

        }

    finally:

        session.close()



@app.get("/api/currencies")

def get_currencies():

    """Get all currencies"""

    session = SessionLocal()

    try:

        currencies = session.query(Currency).all()

        return {

            "count": len(currencies),

            "currencies": [

                {

                    "id": c.id,

                    "name": c.name,

                    "name_kr": c.name_kr,

                    "type": c.type,

                    "rarity": c.rarity

                } for c in currencies

            ]

        }

    finally:

        session.close()



@app.get("/api/exchange-rates")

def get_exchange_rates():

    """Get latest exchange rates"""

    session = SessionLocal()

    try:

        latest = session.query(CurrencyExchangeRate).order_by(

            CurrencyExchangeRate.last_updated.desc()

        ).first()

        

        if not latest:

            return {"message": "No exchange rates available yet"}

        

        return {

            "divine_to_exalt": latest.divine_to_exalt,

            "divine_to_chaos": latest.divine_to_chaos,

            "exalt_to_chaos": latest.exalt_to_chaos,

            "last_updated": latest.last_updated.isoformat()

        }

    finally:

        session.close()



@app.get("/api/bases")

def get_bases(limit: int = 100):

    """Get all base items"""

    session = SessionLocal()

    try:

        bases = session.query(ItemBase).limit(limit).all()

        return {

            "count": len(bases),

            "bases": [

                {

                    "id": b.id,

                    "name": b.name,

                    "required_level": b.required_level

                } for b in bases

            ]

        }

    finally:

        session.close()



@app.get("/api/modifiers")

def get_modifiers(limit: int = 100):

    """Get all modifiers"""

    session = SessionLocal()

    try:

        mods = session.query(ModGroup).limit(limit).all()

        return {

            "count": len(mods),

            "modifiers": [

                {

                    "id": m.id,

                    "name": m.name,

                    "display_name": m.display_name,

                    "is_prefix": m.is_prefix

                } for m in mods

            ]

        }

    finally:

        session.close()



@app.get("/api/profit-opportunities")

def get_profit_opportunities(limit: int = 10):

    """Get profit opportunities"""

    session = SessionLocal()

    try:

        opportunities = session.query(ProfitOpportunity).order_by(

            ProfitOpportunity.roi_percentage.desc()

        ).limit(limit).all()

        

        return {

            "count": len(opportunities),

            "opportunities": [

                {

                    "id": o.id,

                    "base_cost": o.base_cost_divine,

                    "crafting_cost": o.crafting_cost_divine,

                    "sale_price": o.expected_sale_price_divine,

                    "net_profit": o.net_profit_divine,

                    "roi": o.roi_percentage,

                    "success_rate": o.success_probability,

                    "risk": o.risk_level

                } for o in opportunities

            ]

        }

    finally:

        session.close()



@app.get("/api/stats")

def get_stats():

    """Get system statistics"""

    session = SessionLocal()

    try:

        stats = {

            "leagues": session.query(League).count(),

            "currencies": session.query(Currency).count(),

            "bases": session.query(ItemBase).count(),

            "modifiers": session.query(ModGroup).count(),

            "exchange_rates": session.query(CurrencyExchangeRate).count(),

            "profit_opportunities": session.query(ProfitOpportunity).count(),

            "scheduler_active": scheduler.scheduler.running,

            "scheduler_jobs": len(scheduler.scheduler.get_jobs()),

            "timestamp": datetime.now().isoformat()

        }

        return stats

    finally:

        session.close()



@app.get("/api/scheduler/status")

def get_scheduler_status():

    """Get scheduler status"""

    jobs = scheduler.scheduler.get_jobs()

    return {

        "running": scheduler.scheduler.running,

        "jobs_count": len(jobs),

        "jobs": [

            {

                "id": job.id,

                "name": job.name,

                "next_run": job.next_run_time.isoformat() if job.next_run_time else None

            } for job in jobs

        ]

    }



if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8001)

