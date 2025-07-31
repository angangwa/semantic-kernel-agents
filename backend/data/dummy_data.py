from datetime import datetime, timedelta
from typing import Dict, List, Any
import pandas as pd
from io import StringIO

class DummyDataStore:
    def __init__(self):
        self.user_id = "CS-USER-12345"
        self.user_name = "John Smith"
        self.phone_number = "+44 7700 900123"
        
    def get_current_plan(self) -> Dict[str, Any]:
        return {
            "plan_name": "Contoso Ultimate Entertainment",
            "monthly_cost": 45.00,
            "data_allowance": "100GB",
            "minutes": "Unlimited UK",
            "texts": "Unlimited UK",
            "included_features": [
                "5G connectivity",
                "Spotify Premium",
                "YouTube Premium",
                "EU Roaming (25GB)",
                "Unlimited UK calls and texts"
            ],
            "excluded_features": [
                "International calls outside EU",
                "Premium rate numbers",
                "Roaming outside EU",
                "Data usage beyond 100GB",
                "Calls while roaming outside EU"
            ],
            "contract_end_date": "2025-03-15"
        }
    
    def get_bill_line_items(self, bill_id: str) -> pd.DataFrame:
        """Get detailed line items for a specific bill"""
        
        if bill_id == "CS-BILL-202411":
            # November bill with roaming charges from USA
            csv_data = """date,time,type,description,duration,location,charge,included_in_plan
2024-11-03,14:23:00,CALL,Call to UK mobile,15 mins,USA,12.50,No
2024-11-03,18:45:00,CALL,Call to UK landline,8 mins,USA,8.00,No
2024-11-04,09:15:00,DATA,Data usage 500MB,N/A,USA,15.00,No
2024-11-05,11:30:00,CALL,Call to USA number,22 mins,USA,24.00,No
2024-11-05,16:20:00,CALL,Call to UK mobile,5 mins,USA,5.00,No
2024-11-06,10:00:00,DATA,Data usage 1GB,N/A,USA,25.00,No
2024-11-08,13:45:00,CALL,Call to India,30 mins,UK,45.28,No
2024-11-10,19:00:00,SERVICE,Premium SMS service,N/A,UK,22.00,No
2024-11-01,00:00:00,PLAN,Monthly plan charge,N/A,UK,45.00,Yes"""
            
        elif bill_id == "CS-BILL-202410":
            # October bill with heavy roaming from multiple countries
            csv_data = """date,time,type,description,duration,location,charge,included_in_plan
2024-10-05,10:30:00,CALL,Call to UK mobile,45 mins,Australia,67.50,No
2024-10-05,14:15:00,DATA,Data usage 2GB,N/A,Australia,50.00,No
2024-10-08,09:00:00,CALL,Call to UK landline,20 mins,Japan,35.00,No
2024-10-08,21:30:00,CALL,Call to local number,10 mins,Japan,15.00,No
2024-10-10,15:45:00,DATA,Data usage 500MB,N/A,Japan,10.50,No
2024-10-15,11:20:00,CALL,Call to Canada,15 mins,UK,32.50,No
2024-10-20,08:00:00,DATA,Data overage 2.4GB,N/A,UK,24.00,No
2024-10-01,00:00:00,PLAN,Monthly plan charge,N/A,UK,45.00,Yes"""
            
        else:  # September bill - normal usage
            csv_data = """date,time,type,description,duration,location,charge,included_in_plan
2024-09-15,14:30:00,CALL,Call to USA,5 mins,UK,12.50,No
2024-09-01,00:00:00,PLAN,Monthly plan charge,N/A,UK,45.00,Yes
2024-09-05,10:00:00,CALL,UK mobile calls,250 mins,UK,0.00,Yes
2024-09-10,15:00:00,DATA,Data usage 45GB,N/A,UK,0.00,Yes"""
        
        return pd.read_csv(StringIO(csv_data))
    
    def get_recent_bills(self) -> List[Dict[str, Any]]:
        base_date = datetime.now()
        return [
            {
                "bill_id": "CS-BILL-202411",
                "period": "November 2024",
                "date": (base_date - timedelta(days=30)).strftime("%Y-%m-%d"),
                "standard_charges": 45.00,
                "additional_charges": 156.78,
                "total": 201.78,
                "breakdown": {
                    "plan_charge": 45.00,
                    "roaming_charges": 89.50,
                    "international_calls": 45.28,
                    "premium_services": 22.00
                },
                "high_charge_summary": "3 calls and 2 data sessions while roaming in USA",
                "status": "paid"
            },
            {
                "bill_id": "CS-BILL-202410", 
                "period": "October 2024",
                "date": (base_date - timedelta(days=60)).strftime("%Y-%m-%d"),
                "standard_charges": 45.00,
                "additional_charges": 234.50,
                "total": 279.50,
                "breakdown": {
                    "plan_charge": 45.00,
                    "roaming_charges": 178.00,
                    "international_calls": 32.50,
                    "data_overage": 24.00
                },
                "high_charge_summary": "Multiple calls and data usage while roaming in Australia and Japan",
                "status": "paid"
            },
            {
                "bill_id": "CS-BILL-202409",
                "period": "September 2024", 
                "date": (base_date - timedelta(days=90)).strftime("%Y-%m-%d"),
                "standard_charges": 45.00,
                "additional_charges": 12.50,
                "total": 57.50,
                "breakdown": {
                    "plan_charge": 45.00,
                    "international_calls": 12.50
                },
                "high_charge_summary": "Normal usage with one international call",
                "status": "paid"
            }
        ]
    
    def get_roaming_plans(self) -> List[Dict[str, Any]]:
        return [
            {
                "plan_id": "ROAM-USA-7",
                "name": "USA Roaming Pass - 7 Days",
                "price": 15.00,
                "duration": "7 days",
                "data": "5GB",
                "minutes": "100 minutes to UK",
                "texts": "Unlimited to UK",
                "countries": ["USA", "Canada"],
                "savings_example": "Save up to £75 vs pay-as-you-go roaming"
            },
            {
                "plan_id": "ROAM-USA-30",
                "name": "USA Roaming Pass - 30 Days", 
                "price": 40.00,
                "duration": "30 days",
                "data": "20GB",
                "minutes": "500 minutes to UK",
                "texts": "Unlimited to UK",
                "countries": ["USA", "Canada"],
                "savings_example": "Save up to £300 vs pay-as-you-go roaming"
            },
            {
                "plan_id": "ROAM-WORLD-7",
                "name": "World Roaming Pass - 7 Days",
                "price": 25.00,
                "duration": "7 days", 
                "data": "3GB",
                "minutes": "50 minutes to UK",
                "texts": "100 texts to UK",
                "countries": ["Australia", "Japan", "India", "UAE", "Singapore", "Thailand"],
                "savings_example": "Save up to £150 vs pay-as-you-go roaming"
            },
            {
                "plan_id": "ROAM-WORLD-30",
                "name": "World Roaming Pass - 30 Days",
                "price": 70.00,
                "duration": "30 days",
                "data": "15GB", 
                "minutes": "300 minutes to UK",
                "texts": "Unlimited to UK",
                "countries": ["Australia", "Japan", "India", "UAE", "Singapore", "Thailand"],
                "savings_example": "Save up to £500 vs pay-as-you-go roaming"
            }
        ]
    
    def get_available_addons(self) -> List[Dict[str, Any]]:
        return [
            {
                "addon_id": "ADDON-DATA-10",
                "name": "Extra 10GB Data",
                "price": 10.00,
                "description": "Add 10GB to your monthly allowance",
                "duration": "Until next billing cycle",
                "activation": "Instant"
            },
            {
                "addon_id": "ADDON-INTL-100",
                "name": "International Minutes - 100",
                "price": 15.00,
                "description": "100 minutes to call 50+ countries",
                "duration": "30 days",
                "countries": "USA, Canada, India, Australia, most of Europe",
                "activation": "Instant"
            },
            {
                "addon_id": "ADDON-SECURE",
                "name": "Contoso Security Shield",
                "price": 3.00,
                "description": "Protection from malware and phishing",
                "duration": "Monthly subscription",
                "activation": "Within 24 hours"
            },
            {
                "addon_id": "ADDON-FAMILY",
                "name": "Family Data Share",
                "price": 5.00,
                "description": "Share your data with up to 4 family members",
                "duration": "Monthly subscription",
                "activation": "Instant"
            }
        ]
    
    def get_usage_summary(self) -> Dict[str, Any]:
        return {
            "billing_cycle_start": "2024-11-01",
            "billing_cycle_end": "2024-11-30",
            "days_remaining": 4,
            "data": {
                "used": "87.5GB",
                "total": "100GB",
                "percentage": 87.5,
                "daily_average": "3.2GB"
            },
            "minutes": {
                "used": "342 minutes",
                "type": "Unlimited UK",
                "international_used": "45 minutes"
            },
            "texts": {
                "used": "156 texts",
                "type": "Unlimited UK"
            },
            "alerts": [
                "You've used 87.5% of your data allowance",
                "Consider adding extra data to avoid overage charges"
            ]
        }
    
    def analyze_high_charges(self, bill_id: str) -> Dict[str, Any]:
        """Analyze bill to identify main causes of high charges"""
        df = self.get_bill_line_items(bill_id)
        
        # Filter out plan charges and charges included in plan
        extra_charges = df[df['included_in_plan'] == 'No']
        
        # Group by type and location - create a more JSON-friendly summary
        charge_summary = extra_charges.groupby(['type', 'location'])['charge'].agg(['sum', 'count']).reset_index()
        charge_summary.columns = ['type', 'location', 'total_charge', 'count']
        
        # Find top contributors
        top_charges = extra_charges.nlargest(3, 'charge')
        
        total_extra = extra_charges['charge'].sum()
        
        return {
            "total_additional_charges": float(total_extra),
            "main_contributors": charge_summary.to_dict('records'),
            "top_3_charges": top_charges[['date', 'description', 'location', 'charge']].to_dict('records'),
            "roaming_total": float(extra_charges[extra_charges['location'] != 'UK']['charge'].sum()),
            "international_calls_total": float(extra_charges[(extra_charges['type'] == 'CALL') & (extra_charges['location'] == 'UK')]['charge'].sum())
        }

dummy_data = DummyDataStore()