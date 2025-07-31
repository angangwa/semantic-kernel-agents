from typing import Annotated, Dict, Any, List
from semantic_kernel.functions import kernel_function
from data.dummy_data import dummy_data
from utils.file_manager import file_manager
import json
import csv
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path
import pandas as pd

class BillingTools:
    @kernel_function(
        name="get_recent_bills",
        description="Get the user's recent billing information with month-on-month chart"
    )
    def get_recent_bills(self) -> Annotated[str, "Recent bills with totals, breakdown and chart file reference"]:
        bills = dummy_data.get_recent_bills()
        
        # Create month-on-month chart
        chart_file_id = self._create_monthly_trend_chart(bills)
        
        # Add chart reference to response
        response = {
            "recent_bills": bills,
            "chart_reference": file_manager.format_file_reference(
                chart_file_id,
                "Monthly Bill Trend Chart"
            )
        }
        
        return json.dumps(response, indent=2)
    
    def _create_monthly_trend_chart(self, bills_data: List[Dict[str, Any]]) -> str:
        """Create month-on-month bill trend chart with Contoso branding"""
        
        # Extract bill amounts and dates
        bills = bills_data
        if not bills:
            return None
            
        # Prepare data for chart
        months = []
        amounts = []
        for bill in bills:
            months.append(bill["period"])  # Use period field
            amounts.append(bill["total"])  # Use total field
        
        # Contoso brand colors
        contoso_blue = "#0078D4"
        vf_dark_grey = "#333333"
        vf_light_grey = "#CCCCCC"
        
        # Create figure with Contoso styling
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(12, 7))
        fig.patch.set_facecolor('white')
        
        # Create bar chart
        bars = ax.bar(months, amounts, color=contoso_blue, alpha=0.8, edgecolor=vf_dark_grey, linewidth=1)
        
        # Customize chart
        ax.set_title('Monthly Bill Trend', fontsize=18, fontweight='bold', color=vf_dark_grey, pad=20)
        ax.set_xlabel('Billing Period', fontsize=12, color=vf_dark_grey)
        ax.set_ylabel('Amount (£)', fontsize=12, color=vf_dark_grey)
        
        # Format y-axis to show currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'£{x:.0f}'))
        
        # Customize grid
        ax.grid(True, linestyle='--', alpha=0.3, color=vf_light_grey)
        ax.set_axisbelow(True)
        
        # Add value labels on bars
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'£{amount:.0f}', ha='center', va='bottom', 
                   fontweight='bold', color=vf_dark_grey)
        
        # Style the axes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(vf_light_grey)
        ax.spines['bottom'].set_color(vf_light_grey)
        ax.tick_params(colors=vf_dark_grey)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add Contoso text branding
        fig.text(0.95, 0.98, 'CONTOSO', 
                fontsize=14, fontweight='bold', 
                color=contoso_blue, alpha=0.8,
                ha='right', va='top', 
                transform=fig.transFigure)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Generate file ID and save chart
        file_id = file_manager.generate_file_id("monthly_bill_trend", "png")
        file_path = file_manager.get_artifact_path(file_id)
        
        # Save chart with high DPI
        plt.savefig(file_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        # Register artifact
        file_manager.save_artifact(
            file_id=file_id,
            file_path=file_path,
            description="Month-on-month bill trend chart with Contoso branding",
            metadata={
                "chart_type": "bar_chart",
                "data_points": len(bills),
                "format": "png",
                "dimensions": "1200x700",
                "brand_colors": ["#0078D4", "#333333", "#CCCCCC"],
                "includes_logo": True
            }
        )
        
        return file_id
    
    @kernel_function(
        name="get_bill_details",
        description="Get detailed line items for a specific bill and create CSV artifact"
    )
    def get_bill_details(
        self,
        bill_id: Annotated[str, "The bill ID to get details for"]
    ) -> Annotated[str, "Detailed bill line items with file reference for frontend rendering"]:
        df = dummy_data.get_bill_line_items(bill_id)
        
        # Create CSV artifact
        file_id = file_manager.generate_file_id(f"bill_details_{bill_id}", "csv")
        file_path = file_manager.get_artifact_path(file_id)
        
        # Save CSV file
        df.to_csv(file_path, index=False)
        
        # Register artifact with metadata
        file_manager.save_artifact(
            file_id=file_id,
            file_path=file_path,
            description=f"Detailed line items for bill {bill_id}",
            metadata={
                "bill_id": bill_id,
                "row_count": len(df),
                "columns": df.columns.tolist(),
                "total_charges": df[df['charge'] > 0]['charge'].sum() if 'charge' in df.columns else 0
            }
        )
        
        # Return structured response with file reference
        summary = {
            "bill_id": bill_id,
            "total_line_items": len(df),
            "file_reference": file_manager.format_file_reference(
                file_id, 
                f"Bill {bill_id} Line Items"
            ),
            "preview": df.head(10).to_dict('records') if len(df) > 0 else []
        }
        
        return json.dumps(summary, indent=2)
    
    @kernel_function(
        name="analyze_high_charges",
        description="Analyze a bill to identify causes of high charges"
    )
    def analyze_high_charges(
        self,
        bill_id: Annotated[str, "The bill ID to analyze"]
    ) -> Annotated[str, "Analysis of high charges including main contributors"]:
        analysis = dummy_data.analyze_high_charges(bill_id)
        return json.dumps(analysis, indent=2)
    
    
    @kernel_function(
        name="calculate_bill_item",
        description="Calculate costs for billing items"
    )
    def calculate_bill_item(
        self,
        expression: Annotated[str, "Mathematical expression to calculate"]
    ) -> Annotated[float, "Calculated result"]:
        # Safe evaluation of mathematical expressions
        try:
            # Remove any dangerous functions
            safe_dict = {
                "__builtins__": {},
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum
            }
            result = eval(expression, safe_dict)
            return float(result)
        except Exception as e:
            return f"Error calculating: {str(e)}"