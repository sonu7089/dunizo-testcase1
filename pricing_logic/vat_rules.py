"""
VAT Rules Module - Handles VAT calculations for bathroom renovation projects

This module provides VAT rate determination and calculation logic based on:
- Work type (renovation vs new construction)
- Location (different countries/regions)
- Material vs labor costs
- Special cases and exemptions

Author: Bathroom Pricing Engine
"""

from typing import Dict, List, Any, Tuple
import datetime

class VATRules:
    """
    Handles VAT rate determination and calculations for bathroom projects.
    
    VAT rates vary by:
    - Country/Region
    - Type of work (renovation vs new construction)
    - Material vs labor
    - Project scale and client type
    """
    
    def __init__(self):
        """Initialize VAT rules with default rates and regional variations."""
        
        # Base VAT rates by country/region
        self.base_vat_rates = {
            "france": {
                "standard": 0.20,  # 20% standard VAT
                "reduced_renovation": 0.10,  # 10% for renovation work
                "reduced_materials": 0.055,  # 5.5% for certain renovation materials
                "intermediate": 0.10  # 10% intermediate rate
            },
            "germany": {
                "standard": 0.19,  # 19% standard VAT
                "reduced": 0.07   # 7% reduced rate
            },
            "spain": {
                "standard": 0.21,  # 21% standard VAT
                "reduced": 0.10   # 10% reduced rate
            },
            "italy": {
                "standard": 0.22,  # 22% standard VAT
                "reduced": 0.10   # 10% reduced rate
            },
            "default": {
                "standard": 0.20,  # 20% default standard VAT
                "reduced": 0.10   # 10% default reduced rate
            }
        }
        
        # Work type classifications for VAT determination
        self.work_type_classifications = {
            "renovation": [
                "renovation", "repair", "maintenance", "restoration", 
                "refurbishment", "upgrade", "modernization", "improvement"
            ],
            "new_construction": [
                "construction", "new build", "installation", "addition",
                "expansion", "extension"
            ],
            "demolition": [
                "demolition", "removal", "tear down", "destruction"
            ]
        }
        
        # Material categories with special VAT rates
        self.material_vat_categories = {
            "energy_efficient": {
                "materials": [
                    "led lighting", "insulation", "energy efficient fixtures",
                    "smart thermostats", "low flow fixtures", "water saving"
                ],
                "vat_reduction": 0.05  # Additional 5% reduction for energy efficiency
            },
            "accessibility": {
                "materials": [
                    "grab bars", "wheelchair accessible", "shower seats",
                    "walk-in tub", "raised toilet", "accessible vanity"
                ],
                "vat_reduction": 0.05  # Additional 5% reduction for accessibility
            }
        }
    
    def detect_country_from_location(self, location: str) -> str:
        """
        Detect country from location string.
        
        Args:
            location (str): Location string (e.g., "Marseille, France")
            
        Returns:
            str: Country code for VAT lookup
        """
        if not location:
            return "default"
            
        location_lower = location.lower()
        
        # French cities and regions
        french_indicators = [
            "france", "marseille", "paris", "lyon", "toulouse", "nice",
            "nantes", "montpellier", "strasbourg", "bordeaux", "lille",
            "provence", "normandy", "brittany", "alsace", "loire"
        ]
        
        # German cities and regions
        german_indicators = [
            "germany", "deutschland", "berlin", "munich", "hamburg",
            "cologne", "frankfurt", "stuttgart", "düsseldorf", "dortmund",
            "bavaria", "nordrhein-westfalen"
        ]
        
        # Spanish cities and regions
        spanish_indicators = [
            "spain", "españa", "madrid", "barcelona", "valencia",
            "sevilla", "zaragoza", "málaga", "bilbao", "catalonia",
            "andalusia", "basque"
        ]
        
        # Italian cities and regions
        italian_indicators = [
            "italy", "italia", "rome", "milan", "naples", "turin",
            "palermo", "genoa", "bologna", "florence", "lombardy",
            "sicily", "tuscany"
        ]
        
        if any(indicator in location_lower for indicator in french_indicators):
            return "france"
        elif any(indicator in location_lower for indicator in german_indicators):
            return "germany"
        elif any(indicator in location_lower for indicator in spanish_indicators):
            return "spain"
        elif any(indicator in location_lower for indicator in italian_indicators):
            return "italy"
        else:
            return "default"
    
    def classify_work_type(self, task_description: str, objectives: List[Dict]) -> str:
        """
        Classify work type based on task description and objectives.
        
        Args:
            task_description (str): Main task description
            objectives (List[Dict]): List of objectives with descriptions
            
        Returns:
            str: Work type classification (renovation, new_construction, demolition)
        """
        # Combine all text for analysis
        full_text = task_description.lower()
        for obj in objectives:
            full_text += " " + obj.get("description", "").lower()
        
        # Check for work type indicators
        renovation_score = 0
        construction_score = 0
        demolition_score = 0
        
        for keyword in self.work_type_classifications["renovation"]:
            if keyword in full_text:
                renovation_score += 1
        
        for keyword in self.work_type_classifications["new_construction"]:
            if keyword in full_text:
                construction_score += 1
        
        for keyword in self.work_type_classifications["demolition"]:
            if keyword in full_text:
                demolition_score += 1
        
        # Determine primary work type
        if renovation_score >= construction_score and renovation_score >= demolition_score:
            return "renovation"
        elif construction_score >= demolition_score:
            return "new_construction"
        else:
            return "demolition"
    
    def check_material_special_category(self, material_name: str) -> Tuple[str, float]:
        """
        Check if material qualifies for special VAT category.
        
        Args:
            material_name (str): Name of the material
            
        Returns:
            Tuple[str, float]: Category name and VAT reduction amount
        """
        material_lower = material_name.lower()
        
        for category, info in self.material_vat_categories.items():
            for material_keyword in info["materials"]:
                if material_keyword in material_lower:
                    return category, info["vat_reduction"]
        
        return "standard", 0.0
    
    def calculate_vat_rate(self, cost_type: str, work_type: str, country: str, 
                          material_name: str = None) -> Dict[str, Any]:
        """
        Calculate the appropriate VAT rate for a specific cost component.
        
        Args:
            cost_type (str): Type of cost ("materials", "labor", "total")
            work_type (str): Type of work ("renovation", "new_construction", "demolition")
            country (str): Country code
            material_name (str, optional): Specific material name for special rates
            
        Returns:
            Dict[str, Any]: VAT calculation details
        """
        country_rates = self.base_vat_rates.get(country, self.base_vat_rates["default"])
        
        # Initialize VAT calculation
        vat_info = {
            "base_rate": country_rates["standard"],
            "applied_rate": country_rates["standard"],
            "rate_type": "standard",
            "reductions": [],
            "explanation": f"Standard VAT rate for {country}"
        }
        
        # Apply work type specific rates
        if work_type == "renovation" and country == "france":
            if cost_type == "materials":
                # French renovation materials can get 5.5% or 10% rate
                vat_info["applied_rate"] = country_rates["reduced_materials"]
                vat_info["rate_type"] = "reduced_materials"
                vat_info["explanation"] = "Reduced VAT rate for renovation materials in France"
            elif cost_type == "labor":
                # French renovation labor gets 10% rate
                vat_info["applied_rate"] = country_rates["reduced_renovation"]
                vat_info["rate_type"] = "reduced_renovation"
                vat_info["explanation"] = "Reduced VAT rate for renovation labor in France"
        
        # Check for material-specific reductions
        if material_name and cost_type == "materials":
            category, reduction = self.check_material_special_category(material_name)
            if reduction > 0:
                vat_info["applied_rate"] = max(0, vat_info["applied_rate"] - reduction)
                vat_info["reductions"].append({
                    "category": category,
                    "reduction": reduction,
                    "reason": f"Special reduction for {category} materials"
                })
        
        # Ensure minimum VAT rate
        vat_info["applied_rate"] = max(0, vat_info["applied_rate"])
        
        return vat_info
    
    def calculate_task_vat(self, task: Dict[str, Any], country: str) -> Dict[str, Any]:
        """
        Calculate VAT for an entire task including all objectives.
        
        Args:
            task (Dict[str, Any]): Task dictionary with objectives
            country (str): Country code
            
        Returns:
            Dict[str, Any]: Complete VAT breakdown for the task
        """
        work_type = self.classify_work_type(
            task.get("task_name", ""), 
            task.get("objectives", [])
        )
        
        task_vat_breakdown = {
            "work_type": work_type,
            "country": country,
            "objectives": [],
            "materials_vat_total": 0,
            "labor_vat_total": 0,
            "total_vat": 0,
            "effective_vat_rate": 0
        }
        
        total_pre_vat = 0
        total_vat_amount = 0
        
        # Calculate VAT for each objective
        for objective in task.get("objectives", []):
            obj_vat = self.calculate_objective_vat(objective, work_type, country)
            task_vat_breakdown["objectives"].append(obj_vat)
            
            # Accumulate totals
            task_vat_breakdown["materials_vat_total"] += obj_vat["materials_vat_amount"]
            task_vat_breakdown["labor_vat_total"] += obj_vat["labor_vat_amount"]
            
            pre_vat = obj_vat["materials_cost"] + obj_vat["labor_cost"]
            vat_amount = obj_vat["materials_vat_amount"] + obj_vat["labor_vat_amount"]
            
            total_pre_vat += pre_vat
            total_vat_amount += vat_amount
        
        task_vat_breakdown["total_vat"] = total_vat_amount
        
        # Calculate effective VAT rate
        if total_pre_vat > 0:
            task_vat_breakdown["effective_vat_rate"] = total_vat_amount / total_pre_vat
        
        return task_vat_breakdown
    
    def calculate_objective_vat(self, objective: Dict[str, Any], work_type: str, 
                               country: str) -> Dict[str, Any]:
        """
        Calculate VAT for a specific objective.
        
        Args:
            objective (Dict[str, Any]): Objective dictionary
            work_type (str): Type of work
            country (str): Country code
            
        Returns:
            Dict[str, Any]: VAT breakdown for the objective
        """
        cost_breakdown = objective.get("cost_breakdown", {})
        materials_cost = cost_breakdown.get("total_materials_cost", 0)
        labor_cost = cost_breakdown.get("labor_cost", 0)
        
        # Calculate materials VAT
        materials_vat_info = self.calculate_vat_rate("materials", work_type, country)
        materials_vat_amount = materials_cost * materials_vat_info["applied_rate"]
        
        # Calculate labor VAT
        labor_vat_info = self.calculate_vat_rate("labor", work_type, country)
        labor_vat_amount = labor_cost * labor_vat_info["applied_rate"]
        
        # Check for special material rates
        special_materials_vat = 0
        material_details = []
        
        for material_item in objective.get("materials_required", []):
            material_name = material_item.get("material", "")
            material_cost = material_item.get("total_cost", 0)
            
            material_vat_info = self.calculate_vat_rate(
                "materials", work_type, country, material_name
            )
            material_vat_amount = material_cost * material_vat_info["applied_rate"]
            
            material_details.append({
                "material": material_name,
                "cost": material_cost,
                "vat_rate": material_vat_info["applied_rate"],
                "vat_amount": material_vat_amount,
                "rate_type": material_vat_info["rate_type"]
            })
            
            special_materials_vat += material_vat_amount
        
        # Use detailed material VAT if available, otherwise use aggregate
        if material_details:
            final_materials_vat = special_materials_vat
        else:
            final_materials_vat = materials_vat_amount
        
        return {
            "objective_id": objective.get("objective_id", ""),
            "description": objective.get("description", ""),
            "materials_cost": materials_cost,
            "labor_cost": labor_cost,
            "materials_vat_rate": materials_vat_info["applied_rate"],
            "labor_vat_rate": labor_vat_info["applied_rate"],
            "materials_vat_amount": final_materials_vat,
            "labor_vat_amount": labor_vat_amount,
            "total_vat_amount": final_materials_vat + labor_vat_amount,
            "total_with_vat": materials_cost + labor_cost + final_materials_vat + labor_vat_amount,
            "materials_vat_info": materials_vat_info,
            "labor_vat_info": labor_vat_info,
            "material_details": material_details
        }
    
    def get_vat_summary(self, country: str, work_type: str) -> Dict[str, Any]:
        """
        Get a summary of applicable VAT rates for a project.
        
        Args:
            country (str): Country code
            work_type (str): Type of work
            
        Returns:
            Dict[str, Any]: VAT rates summary
        """
        country_rates = self.base_vat_rates.get(country, self.base_vat_rates["default"])
        
        summary = {
            "country": country,
            "work_type": work_type,
            "standard_rate": country_rates["standard"],
            "applicable_rates": {},
            "special_categories": list(self.material_vat_categories.keys())
        }
        
        # Add applicable rates based on work type and country
        if work_type == "renovation" and country == "france":
            summary["applicable_rates"] = {
                "materials": country_rates["reduced_materials"],
                "labor": country_rates["reduced_renovation"]
            }
        else:
            summary["applicable_rates"] = {
                "materials": country_rates["standard"],
                "labor": country_rates["standard"]
            }
        
        return summary