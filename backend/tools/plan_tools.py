from typing import Annotated, Dict, Any, List
from semantic_kernel.functions import kernel_function
from data.dummy_data import dummy_data
import json

class PlanTools:
    @kernel_function(
        name="get_current_plan",
        description="Get the user's current mobile plan details"
    )
    def get_current_plan(self) -> Annotated[str, "Current plan details including features"]:
        plan = dummy_data.get_current_plan()
        return json.dumps(plan, indent=2)
    
    @kernel_function(
        name="get_roaming_plans",
        description="Get available roaming plans for international travel"
    )
    def get_roaming_plans(self) -> Annotated[str, "Available roaming plans with pricing"]:
        plans = dummy_data.get_roaming_plans()
        return json.dumps(plans, indent=2)
    
    @kernel_function(
        name="get_available_addons",
        description="Get available add-ons to enhance the current plan"
    )
    def get_available_addons(self) -> Annotated[str, "Available add-ons with pricing"]:
        addons = dummy_data.get_available_addons()
        return json.dumps(addons, indent=2)
    
    @kernel_function(
        name="get_usage_summary",
        description="Get current billing cycle usage summary"
    )
    def get_usage_summary(self) -> Annotated[str, "Usage summary for current billing cycle"]:
        usage = dummy_data.get_usage_summary()
        return json.dumps(usage, indent=2)
    
    @kernel_function(
        name="check_feature_inclusion",
        description="Check if a specific feature or service is included in the user's plan"
    )
    def check_feature_inclusion(
        self,
        feature: Annotated[str, "The feature to check (e.g., 'roaming in USA', 'international calls')"]
    ) -> Annotated[str, "Whether the feature is included and relevant details"]:
        plan = dummy_data.get_current_plan()
        
        feature_lower = feature.lower()
        
        # Check included features
        for included in plan['included_features']:
            if feature_lower in included.lower():
                return json.dumps({
                    "included": True,
                    "feature": feature,
                    "details": included,
                    "additional_info": "This feature is included in your current plan"
                })
        
        # Check excluded features
        for excluded in plan['excluded_features']:
            if feature_lower in excluded.lower():
                return json.dumps({
                    "included": False,
                    "feature": feature,
                    "details": excluded,
                    "additional_info": "This feature is NOT included in your current plan. Additional charges apply."
                })
        
        return json.dumps({
            "included": "unknown",
            "feature": feature,
            "additional_info": "Unable to determine if this specific feature is included. Please check with customer service."
        })