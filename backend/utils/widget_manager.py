"""
Widget management utility for Contoso Agent Demo
Resolves widget IDs to accurate data from dummy_data.py and formats for frontend rendering
"""

import json
import re
import datetime
import random
from typing import Dict, Any, List, Optional
from data.dummy_data import dummy_data
from tools.support_tools import SupportTools


class WidgetManager:
    """Manages widget data resolution and formatting for frontend rendering"""
    
    def __init__(self):
        self.dummy_data = dummy_data
        
        # Widget type handlers
        self.widget_handlers = {
            'current_plan': self._handle_current_plan,
            'roaming_plans': self._handle_roaming_plans,
            'addons': self._handle_addons,
            'usage_summary': self._handle_usage_summary,
            'support_ticket': self._handle_support_ticket
        }
    
    def extract_widget_references(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract widget references from agent response content
        Pattern: [WIDGET:widget_type:["id1","id2"]] or [WIDGET:widget_type:[]]
        
        Returns list of widget objects with resolved data
        """
        widgets = []
        pattern = r'\[WIDGET:([^:]+):(\[[^\]]*\])\]'
        matches = re.findall(pattern, content)
        
        print(f"DEBUG widget_manager: Found {len(matches)} widget patterns in content")
        
        for widget_type, ids_json in matches:
            try:
                # Parse the IDs array
                widget_ids = json.loads(ids_json)
                if not isinstance(widget_ids, list):
                    continue
                
                # Resolve widget data
                widget_data = self.resolve_widget_data(widget_type, widget_ids)
                if widget_data:
                    widgets.append({
                        'widget_type': widget_type,
                        'widget_ids': widget_ids,
                        'widget_data': widget_data,
                        'pattern': f'[WIDGET:{widget_type}:{ids_json}]'
                    })
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing widget reference: {widget_type}:{ids_json} - {e}")
                continue
        
        return widgets
    
    def resolve_widget_data(self, widget_type: str, widget_ids: List[str]) -> Optional[Dict[str, Any]]:
        """
        Resolve widget type and IDs to actual data from dummy_data.py
        
        Args:
            widget_type: Type of widget (current_plan, roaming_plans, addons, usage_summary)
            widget_ids: List of IDs to resolve (can be empty for some widget types)
            
        Returns:
            Dict with resolved widget data or None if invalid
        """
        handler = self.widget_handlers.get(widget_type)
        if not handler:
            print(f"Unknown widget type: {widget_type}")
            return None
        
        try:
            return handler(widget_ids)
        except Exception as e:
            print(f"Error resolving widget {widget_type}: {e}")
            return None
    
    def _handle_current_plan(self, widget_ids: List[str]) -> Dict[str, Any]:
        """Handle current_plan widget - no IDs needed, shows user's current plan"""
        plan_data = self.dummy_data.get_current_plan()
        
        return {
            'widget_type': 'current_plan',
            'title': 'Your Current Plan',
            'data': plan_data,
            'actions': [
                {
                    'label': 'View Plan Details',
                    'url': 'https://contoso.com/mobile/pay-monthly-contracts',
                    'type': 'primary'
                },
                {
                    'label': 'Upgrade Plan',
                    'url': 'https://contoso.com/mobile/pay-monthly-contracts',
                    'type': 'secondary'
                }
            ]
        }
    
    def _handle_roaming_plans(self, widget_ids: List[str]) -> Dict[str, Any]:
        """Handle roaming_plans widget - resolve specific plan IDs"""
        all_roaming_plans = self.dummy_data.get_roaming_plans()
        
        # If no IDs specified, show all plans
        if not widget_ids:
            selected_plans = all_roaming_plans
        else:
            # Filter to only requested plan IDs
            selected_plans = [
                plan for plan in all_roaming_plans 
                if plan['plan_id'] in widget_ids
            ]
        
        # Sort by price (cheapest first)
        selected_plans.sort(key=lambda x: x['price'])
        
        return {
            'widget_type': 'roaming_plans',
            'title': 'Recommended Roaming Plans',
            'data': selected_plans,
            'actions': [
                {
                    'label': 'View All Roaming Plans',
                    'url': 'https://contoso.com/mobile/global-roaming',
                    'type': 'primary'
                },
                {
                    'label': 'Check Coverage',
                    'url': 'https://contoso.com/mobile/global-roaming',
                    'type': 'secondary'
                }
            ]
        }
    
    def _handle_addons(self, widget_ids: List[str]) -> Dict[str, Any]:
        """Handle addons widget - resolve specific addon IDs"""
        all_addons = self.dummy_data.get_available_addons()
        
        # If no IDs specified, show all addons
        if not widget_ids:
            selected_addons = all_addons
        else:
            # Filter to only requested addon IDs
            selected_addons = [
                addon for addon in all_addons 
                if addon['addon_id'] in widget_ids
            ]
        
        # Sort by price (cheapest first)
        selected_addons.sort(key=lambda x: x['price'])
        
        return {
            'widget_type': 'addons',
            'title': 'Recommended Add-ons',
            'data': selected_addons,
            'actions': [
                {
                    'label': 'View All Extras',
                    'url': 'https://contoso.com/mobile/extras',
                    'type': 'primary'
                },
                {
                    'label': 'Manage Add-ons',
                    'url': 'https://contoso.com/mobile/extras',
                    'type': 'secondary'
                }
            ]
        }
    
    def _handle_usage_summary(self, widget_ids: List[str]) -> Dict[str, Any]:
        """Handle usage_summary widget - shows current usage stats"""
        usage_data = self.dummy_data.get_usage_summary()
        
        return {
            'widget_type': 'usage_summary',
            'title': 'Your Current Usage',
            'data': usage_data,
            'actions': [
                {
                    'label': 'View Detailed Usage',
                    'url': 'https://contoso.com/my-account',
                    'type': 'primary'
                },
                {
                    'label': 'Add Extra Data',
                    'url': 'https://contoso.com/mobile/extras',
                    'type': 'secondary'
                }
            ]
        }
    
    def _handle_support_ticket(self, widget_ids: List[str]) -> Dict[str, Any]:
        """Handle support_ticket widget - shows created support ticket details"""
        # Look up specific ticket by ID from shared storage
        try:
            # Get ticket ID from widget_ids (agent should pass the ticket_id)
            ticket_id = widget_ids[0] if widget_ids else None
            print(f"DEBUG: Looking for ticket_id: {ticket_id}")
            print(f"DEBUG: Available tickets: {len(SupportTools._shared_tickets)}")
            
            if ticket_id and SupportTools._shared_tickets:
                # Find the specific ticket by ID
                ticket = next((t for t in SupportTools._shared_tickets if t["ticket_id"] == ticket_id), None)
                print(f"DEBUG: Found ticket: {ticket is not None}")
                
                if ticket:
                    print(f"DEBUG: Ticket issue_summary: {ticket['issue_summary']}")
                    ticket_data = {
                        "ticket_id": ticket["ticket_id"],
                        "status": ticket["status"].title(),
                        "priority": ticket["priority"].title(),
                        "created_date": ticket["created_at"][:16].replace('T', ' '),
                        "subject": "Customer Support Request",
                        "description": ticket["issue_summary"],
                        "contact_method": "Phone call",
                        "estimated_callback": "Within 24 hours",
                        "assigned_team": "Customer Care Team",
                        "reference_number": ticket["ticket_id"]
                    }
                else:
                    raise Exception(f"Ticket {ticket_id} not found")
            else:
                raise Exception("No ticket ID provided or no tickets exist")
        except:
            # Fallback to demo data if lookup fails
            now = datetime.datetime.now()
            fallback_ticket_id = f"CS-{now.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            ticket_data = {
                "ticket_id": fallback_ticket_id,
                "status": "Open",
                "priority": "Normal",
                "created_date": now.strftime("%Y-%m-%d %H:%M"),
                "subject": "Customer Support Request",
                "description": "Customer requested human assistance",
                "contact_method": "Phone call",
                "estimated_callback": "Within 24 hours",
                "assigned_team": "Customer Care Team",
                "reference_number": fallback_ticket_id
            }
        
        return {
            'widget_type': 'support_ticket',
            'title': 'Support Ticket Created',
            'data': ticket_data,
            'actions': [
                {
                    'label': 'Track Your Ticket',
                    'url': 'https://contoso.com/support',
                    'type': 'primary'
                },
                {
                    'label': 'Contact Support',
                    'url': 'https://contoso.com/help-and-support',
                    'type': 'secondary'
                }
            ]
        }
    
    def format_widget_reference(self, widget_type: str, widget_ids: List[str] = None) -> str:
        """
        Format widget reference for agent responses
        
        Examples:
        - format_widget_reference('current_plan') -> '[WIDGET:current_plan:[]]'
        - format_widget_reference('roaming_plans', ['ROAM-USA-7']) -> '[WIDGET:roaming_plans:["ROAM-USA-7"]]'
        """
        if widget_ids is None:
            widget_ids = []
        
        ids_json = json.dumps(widget_ids)
        return f'[WIDGET:{widget_type}:{ids_json}]'
    
    def get_available_widget_types(self) -> List[str]:
        """Get list of available widget types"""
        return list(self.widget_handlers.keys())
    
    def get_available_ids_for_type(self, widget_type: str) -> List[str]:
        """Get available IDs for a specific widget type"""
        if widget_type == 'roaming_plans':
            plans = self.dummy_data.get_roaming_plans()
            return [plan['plan_id'] for plan in plans]
        elif widget_type == 'addons':
            addons = self.dummy_data.get_available_addons()
            return [addon['addon_id'] for addon in addons]
        elif widget_type in ['current_plan', 'usage_summary']:
            return []  # These don't use IDs
        else:
            return []


# Global instance
widget_manager = WidgetManager()