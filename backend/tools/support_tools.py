from typing import Annotated, Dict, Any, List
from semantic_kernel.functions import kernel_function
from datetime import datetime, timedelta
import json
import uuid

class SupportTools:
    _shared_tickets = []  # Class variable shared across all instances
    
    def __init__(self):
        self.tickets = SupportTools._shared_tickets  # Reference to shared storage
    
    @kernel_function(
        name="create_support_ticket",
        description="Create a support ticket for human agent follow-up"
    )
    def create_support_ticket(
        self,
        issue_summary: Annotated[str, "Brief summary of the customer's issue"],
        priority: Annotated[str, "Priority level: low, medium, high"] = "medium"
    ) -> Annotated[str, "Ticket creation confirmation with ticket ID"]:
        
        ticket_id = f"CS-TICKET-{str(uuid.uuid4())[:8].upper()}"
        
        ticket = {
            "ticket_id": ticket_id,
            "created_at": datetime.now().isoformat(),
            "customer_id": "CS-USER-12345",
            "customer_name": "John Smith",
            "phone_number": "+44 7700 900123",
            "issue_summary": issue_summary,
            "priority": priority,
            "status": "open",
            "assigned_to": "Next available agent",
            "conversation_context": issue_summary
        }
        
        SupportTools._shared_tickets.append(ticket)
        print(f"DEBUG: Added ticket to storage. Total tickets now: {len(SupportTools._shared_tickets)}")
        print(f"DEBUG: Ticket ID added: {ticket['ticket_id']}")
        
        return json.dumps({
            "success": True,
            "ticket_id": ticket_id,
            "message": f"Support ticket {ticket_id} has been created successfully",
            "confirmation": "A human agent will reach out to you within 24 hours"
        }, indent=2)
    
    @kernel_function(
        name="get_widget_link",
        description="Generate a widget or link for customer actions"
    )
    def get_widget_link(
        self,
        action_type: Annotated[str, "Type of action: addon_purchase, roaming_activation, plan_upgrade"],
        item_id: Annotated[str, "ID of the addon, roaming plan, or upgrade option"]
    ) -> Annotated[str, "Widget information with link"]:
        
        base_url = "https://contoso.com/demo"
        
        widgets = {
            "addon_purchase": {
                "url": f"{base_url}/addons/{item_id}",
                "type": "Add-on Purchase",
                "button_text": "Add to Plan",
                "disclaimer": "Changes will be reflected in your next billing cycle"
            },
            "roaming_activation": {
                "url": f"{base_url}/roaming/{item_id}",
                "type": "Roaming Plan Activation",
                "button_text": "Activate Roaming",
                "disclaimer": "Roaming plan will be activated immediately upon purchase"
            },
            "plan_upgrade": {
                "url": f"{base_url}/plans/upgrade/{item_id}",
                "type": "Plan Upgrade",
                "button_text": "Upgrade Plan",
                "disclaimer": "Plan changes may extend your contract period"
            }
        }
        
        if action_type in widgets:
            widget = widgets[action_type]
            return json.dumps({
                "widget_type": widget["type"],
                "action_url": widget["url"],
                "button_text": widget["button_text"],
                "disclaimer": widget["disclaimer"],
                "display_format": "button",
                "demo_note": "This is a demo link - no actual charges will be applied"
            }, indent=2)
        else:
            return json.dumps({
                "error": "Invalid action type",
                "valid_types": list(widgets.keys())
            }, indent=2)
    
    def _calculate_callback_time(self, priority: str) -> str:
        """Calculate expected callback time based on priority"""
        now = datetime.now()
        
        if priority == "high":
            callback_time = now + timedelta(hours=2)
        elif priority == "medium":
            callback_time = now + timedelta(hours=4)
        else:
            callback_time = now + timedelta(hours=24)
        
        # Adjust for business hours (9 AM - 6 PM)
        if callback_time.hour < 9:
            callback_time = callback_time.replace(hour=9, minute=0)
        elif callback_time.hour >= 18:
            callback_time = callback_time + timedelta(days=1)
            callback_time = callback_time.replace(hour=9, minute=0)
        
        return callback_time.strftime("%Y-%m-%d %H:%M")