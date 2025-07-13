import argparse
import os
import requests
import json
import datetime
import sys
from typing import Dict, List, Any
from dotenv import load_dotenv
load_dotenv()

try:
    from pricing_logic.material_db import MaterialDB
except ImportError:
    print("Error: Could not import MaterialDB. Make sure pricing_logic/material_db.py exists.")
    sys.exit(1)

try:
    from pricing_logic.labor_calc import LaborCalculator
except ImportError:
    print("Error: Could not import LaborCalculator. Make sure labor_calc.py exists.")
    sys.exit(1)

try:
    from pricing_logic.vat_rules import VATRules
except ImportError:
    print("Error: Could not import VATRules. Make sure vat_rules.py exists.")
    sys.exit(1)

class MarginCalculator:
    def __init__(self):
        self.base_margins = {
            "materials": 0.10,
            "labor": 0.05,
            "total": 0.15
        }
        
        self.budget_level_adjustments = {
            0: -0.05,
            1: 0.0,
            2: 0.05,
            3: 0.10
        }
        
        self.complexity_adjustments = {
            "low": 0.0,
            "medium": 0.05,
            "high": 0.1
        }
        
        self.location_multipliers = {
            "paris": 1.20,
            "marseille": 1.0,
            "lyon": 1.15,
            "nice": 1.10,
            "default": 1.0
        }
    
    def get_location_multiplier(self, location: str) -> float:
        location_lower = location.lower()
        for city, multiplier in self.location_multipliers.items():
            if city in location_lower:
                return multiplier
        return self.location_multipliers["default"]
    
    def calculate_margins(self, cost_breakdown: Dict[str, Any], budget_level: int, 
                         complexity: str, location: str) -> Dict[str, Any]:
        materials_cost = cost_breakdown.get("total_materials_cost", 0)
        labor_cost = cost_breakdown.get("labor_cost", 0)
        
        budget_adj = self.budget_level_adjustments.get(budget_level, 0)
        complexity_adj = self.complexity_adjustments.get(complexity, 0)
        location_mult = self.get_location_multiplier(location)
        
        materials_margin_rate = (self.base_margins["materials"] + budget_adj + complexity_adj) * location_mult
        labor_margin_rate = (self.base_margins["labor"] + budget_adj + complexity_adj) * location_mult
        
        materials_margin = materials_cost * materials_margin_rate
        labor_margin = labor_cost * labor_margin_rate
        
        subtotal = materials_cost + labor_cost
        total_margin = materials_margin + labor_margin
        additional_margin = subtotal * self.base_margins["total"] * location_mult
        
        return {
            "materials_margin_rate": round(materials_margin_rate, 3),
            "labor_margin_rate": round(labor_margin_rate, 3),
            "materials_margin": round(materials_margin, 2),
            "labor_margin": round(labor_margin, 2),
            "additional_margin": round(additional_margin, 2),
            "total_margin": round(total_margin + additional_margin, 2),
            "budget_adjustment": budget_adj,
            "complexity_adjustment": complexity_adj,
            "location_multiplier": location_mult
        }

def enrich_materials_with_pricing(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    material_db = MaterialDB(materials_file="data/materials.json")
    
    all_material_names = []
    
    for task in parsed_json.get("tasks", []):
        for objective in task.get("objectives", []):
            # Only collect regular materials for pricing
            for material_item in objective.get("materials_required", []):
                material_name = material_item.get("material", "")
                if material_name and material_name not in all_material_names:
                    all_material_names.append(material_name)
            
            # Still collect misc materials for pricing info (for reference)
            for material_item in objective.get("miscellaneous_materials", []):
                material_name = material_item.get("material", "")
                if material_name and material_name not in all_material_names:
                    all_material_names.append(material_name)
    
    print(f"Found {len(all_material_names)} unique materials to price...")
    
    if all_material_names:
        materials_with_pricing = material_db.get_materials_with_fallback(all_material_names)
        print(f"Successfully retrieved pricing for {len(materials_with_pricing)} materials")
    else:
        materials_with_pricing = {}
        print("No materials found to price")
    
    total_materials_cost = 0
    
    for task in parsed_json.get("tasks", []):
        task_total_cost = 0
        
        for objective in task.get("objectives", []):
            objective_materials_cost = 0
            objective_misc_cost = 0
            
            # Process regular materials (INCLUDED in final cost)
            for material_item in objective.get("materials_required", []):
                material_name = material_item.get("material", "")
                quantity = material_item.get("quantity", 1)
                
                if material_name in materials_with_pricing:
                    pricing_info = materials_with_pricing[material_name]
                    unit_price = pricing_info["price"]
                    unit_quantity = pricing_info["quantity"]
                    unit_description = pricing_info["unit"]
                    
                    material_cost = quantity * unit_price
                    
                    material_item["unit_price"] = unit_price
                    material_item["unit_quantity"] = unit_quantity
                    material_item["price_unit"] = unit_description
                    material_item["total_cost"] = material_cost
                    material_item["description"] = pricing_info["description"]
                    material_item["included_in_pricing"] = True  # Flag for clarity
                    
                    objective_materials_cost += material_cost
                else:
                    material_item["unit_price"] = 0
                    material_item["unit_quantity"] = 1
                    material_item["price_unit"] = "unknown"
                    material_item["total_cost"] = 0
                    material_item["description"] = "Pricing not available"
                    material_item["included_in_pricing"] = False
                    
                    print(f"Warning: Could not find pricing for material: {material_name}")
            
            # Process miscellaneous materials (NOT INCLUDED in final cost)
            for material_item in objective.get("miscellaneous_materials", []):
                material_name = material_item.get("material", "")
                quantity = material_item.get("quantity", 1)
                
                if material_name in materials_with_pricing:
                    pricing_info = materials_with_pricing[material_name]
                    unit_price = pricing_info["price"]
                    unit_quantity = pricing_info["quantity"]
                    unit_description = pricing_info["unit"]
                    
                    material_cost = quantity * unit_price
                    
                    material_item["unit_price"] = unit_price
                    material_item["unit_quantity"] = unit_quantity
                    material_item["price_unit"] = unit_description
                    material_item["total_cost"] = material_cost
                    material_item["description"] = pricing_info["description"]
                    material_item["included_in_pricing"] = False  # Flag: NOT included in final cost
                    
                    objective_misc_cost += material_cost  # For reference only
                else:
                    material_item["unit_price"] = 0
                    material_item["unit_quantity"] = 1
                    material_item["price_unit"] = "unknown"
                    material_item["total_cost"] = 0
                    material_item["description"] = "Pricing not available"
                    material_item["included_in_pricing"] = False
                    
                    print(f"Warning: Could not find pricing for material: {material_name}")
            
            # ONLY materials_cost is included in final pricing (excluding misc)
            objective_total_materials = objective_materials_cost  # Changed: removed misc_cost
            
            objective["cost_breakdown"] = {
                "materials_cost": objective_materials_cost,
                "miscellaneous_cost": objective_misc_cost,  # For reference only
                "total_materials_cost": objective_total_materials,  # Only regular materials
                "misc_cost_excluded": True  # Flag to indicate misc costs are excluded
            }
            
            task_total_cost += objective_total_materials
        
        task["total_materials_cost"] = task_total_cost
        total_materials_cost += task_total_cost
    
    parsed_json["pricing_summary"] = {
        "total_materials_cost": total_materials_cost,
        "currency": "EUR",
        "pricing_date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "materials_priced": len(materials_with_pricing),
        "materials_missing_pricing": len(all_material_names) - len(materials_with_pricing),
        "miscellaneous_costs_included": False  # Flag to indicate misc costs are excluded
    }
    
    print(f"Total materials cost (excluding miscellaneous): €{total_materials_cost}")
    
    return parsed_json

def enrich_with_labor_costs(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    labor_calc = LaborCalculator(price_templates_file="data/price_templates.csv")
    
    location = parsed_json.get("location", "")
    
    print(f"Calculating labor costs for location: {location}")
    
    total_labor_cost = 0
    
    for task in parsed_json.get("tasks", []):
        task_total_labor_cost = 0
        
        for objective in task.get("objectives", []):
            labor_cost_breakdown = labor_calc.calculate_objective_labor_cost(objective, location)
            
            objective["labor_cost_breakdown"] = {
                "difficulty_level": labor_cost_breakdown["difficulty_level"],
                "difficulty_description": labor_cost_breakdown["difficulty_description"],
                "estimated_hours": labor_cost_breakdown["estimated_hours"],
                "base_hourly_rate": round(labor_cost_breakdown["base_hourly_rate"], 2),
                "skill_multiplier": labor_cost_breakdown["skill_multiplier"],
                "complexity_factor": labor_cost_breakdown["complexity_factor"],
                "effective_hourly_rate": round(labor_cost_breakdown["effective_hourly_rate"], 2),
                "regional_multiplier": labor_cost_breakdown["regional_multiplier"],
                "regional_hourly_rate": round(labor_cost_breakdown["regional_hourly_rate"], 2),
                "confidence_adjustment": labor_cost_breakdown["confidence_adjustment"],
                "final_hourly_rate": round(labor_cost_breakdown["final_hourly_rate"], 2),
                "total_labor_cost": round(labor_cost_breakdown["total_labor_cost"], 2)
            }
            
            current_materials_cost = objective.get("cost_breakdown", {}).get("total_materials_cost", 0)
            objective_labor_cost = labor_cost_breakdown["total_labor_cost"]
            
            objective["cost_breakdown"].update({
                "labor_cost": objective_labor_cost,
                "total_cost": current_materials_cost + objective_labor_cost
            })
            
            task_total_labor_cost += objective_labor_cost
        
        task["total_labor_cost"] = round(task_total_labor_cost, 2)
        current_materials_cost = task.get("total_materials_cost", 0)
        task["total_cost"] = current_materials_cost + task_total_labor_cost
        
        total_labor_cost += task_total_labor_cost
    
    current_materials_cost = parsed_json.get("pricing_summary", {}).get("total_materials_cost", 0)
    parsed_json["pricing_summary"].update({
        "total_labor_cost": round(total_labor_cost, 2),
        "total_project_cost": current_materials_cost + total_labor_cost,
        "location": location,
        "regional_multiplier": labor_calc.get_regional_multiplier(location)
    })
    
    print(f"Total labor cost: €{total_labor_cost}")
    print(f"Total project cost: €{current_materials_cost + total_labor_cost}")
    
    return parsed_json

def enrich_with_vat_and_margins(parsed_json: Dict[str, Any]) -> Dict[str, Any]:
    vat_rules = VATRules()
    margin_calc = MarginCalculator()
    
    location = parsed_json.get("location", "")
    budget_level = parsed_json.get("budget_level", 1)
    
    country = vat_rules.detect_country_from_location(location)
    
    print(f"Calculating VAT and margins for {country} (budget level: {budget_level})")
    
    total_vat_amount = 0
    total_margin_amount = 0
    total_final_cost = 0
    
    for task in parsed_json.get("tasks", []):
        task_vat_breakdown = vat_rules.calculate_task_vat(task, country)
        
        task_margin_breakdown = margin_calc.calculate_margins(
            {"total_materials_cost": task.get("total_materials_cost", 0),
             "labor_cost": task.get("total_labor_cost", 0)},
            budget_level,
            task.get("estimated_complexity", "medium"),
            location
        )
        
        task["vat_breakdown"] = task_vat_breakdown
        task["margin_breakdown"] = task_margin_breakdown
        
        task_subtotal = task.get("total_cost", 0)
        task_margin = task_margin_breakdown["total_margin"]
        task_with_margin = task_subtotal + task_margin
        task_vat = task_vat_breakdown["total_vat"]
        task_final = task_with_margin + task_vat
        
        task["pricing_breakdown"] = {
            "subtotal": round(task_subtotal, 2),
            "margin": round(task_margin, 2),
            "subtotal_with_margin": round(task_with_margin, 2),
            "vat_amount": round(task_vat, 2),
            "final_price": round(task_final, 2)
        }
        
        total_vat_amount += task_vat
        total_margin_amount += task_margin
        total_final_cost += task_final
        
        for i, objective in enumerate(task.get("objectives", [])):
            if i < len(task_vat_breakdown["objectives"]):
                obj_vat = task_vat_breakdown["objectives"][i]
                
                obj_subtotal = objective.get("cost_breakdown", {}).get("total_cost", 0)
                obj_margin_rate = (task_margin_breakdown["materials_margin_rate"] + 
                                 task_margin_breakdown["labor_margin_rate"]) / 2
                obj_margin = obj_subtotal * obj_margin_rate
                obj_with_margin = obj_subtotal + obj_margin
                obj_vat_amount = obj_vat["total_vat_amount"]
                obj_final = obj_with_margin + obj_vat_amount
                
                objective["vat_breakdown"] = obj_vat
                objective["margin_breakdown"] = {
                    "margin_rate": round(obj_margin_rate, 3),
                    "margin_amount": round(obj_margin, 2)
                }
                objective["pricing_breakdown"] = {
                    "subtotal": round(obj_subtotal, 2),
                    "margin": round(obj_margin, 2),
                    "subtotal_with_margin": round(obj_with_margin, 2),
                    "vat_amount": round(obj_vat_amount, 2),
                    "final_price": round(obj_final, 2)
                }
    
    current_subtotal = parsed_json.get("pricing_summary", {}).get("total_project_cost", 0)
    
    parsed_json["pricing_summary"].update({
        "total_margin": round(total_margin_amount, 2),
        "subtotal_with_margin": round(current_subtotal + total_margin_amount, 2),
        "total_vat": round(total_vat_amount, 2),
        "final_project_cost": round(total_final_cost, 2),
        "country": country,
        "budget_level": budget_level
    })
    
    print(f"Total margin: €{total_margin_amount}")
    print(f"Total VAT: €{total_vat_amount}")
    print(f"Final project cost: €{total_final_cost}")
    
    return parsed_json

def parse_transcript(transcript: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set.")
        print("Please set it before running the script. Example: export OPENROUTER_API_KEY='your_api_key'")
        return

    system_prompt = """You are an AI assistant specialized in parsing bathroom-related transcripts into structured JSON format. Your task is to analyze client conversations about any bathroom projects including construction, renovation, destruction, maintenance, repairs, installations, and all other bathroom-related work for bathroom contractors and professionals.
Instructions:
Parse the following bathroom-related transcript and convert it into a structured JSON format. Focus on identifying any bathroom work including:

Construction: New bathroom builds, additions, expansions
Renovation: Updates, modernization, style changes
Destruction/Demolition: Removal, tear-down, dismantling
Maintenance: Regular upkeep, cleaning, servicing
Repairs: Fixing broken fixtures, plumbing, electrical issues
Installation: New fixture installation, upgrades
Modifications: Accessibility improvements, layout changes
Inspections: Safety checks, compliance assessments


Tasks: Main project or service requests
Objectives: Specific work items or deliverables within each task
Budget Level: Inferred from tone and explicit mentions (0-3 scale)
Location: Geographic information
Additional Details: Any other relevant project information

Budget Scoring System:

3: Open budget / No budget constraints mentioned / Premium quality focus
2: Slight premium / Above normal budget / Quality-focused
1: Moderate budget / Some cost considerations mentioned
0: Tight budget / Budget-conscious / Cost-focused / Explicit budget constraints

Required JSON Structure:
json{
  "tasks": [
    {
      "task_id": "task_1",
      "task_name": "Main task description",
      "objectives": [
        {
          "objective_id": "obj_1",
          "description": "Objective description",
          "labor_difficulty": 2,
          "materials_required": [
            {
              "material": "Specific material name",
              "quantity": 5,
              "unit": "m²"
            }
          ],
          "miscellaneous_materials": [
            {
              "material": "Additional supplies/tools",
              "quantity": 1,
              "unit": "set"
            }
          ],
          "estimated_time": 8,
          "confidence_score": 0.85
        }
      ],
      "estimated_complexity": "low|medium|high",
      "timeline_mentions": "any specific deadlines or timeframes mentioned"
    }
  ],
  "budget_level": 0,
  "budget_notes": "Brief explanation of budget assessment",
  "location": "City, Region/State, Country (if available)",
  "client_preferences": [
    "Any specific preferences, materials, styles mentioned"
  ],
  "urgency_level": "low|medium|high",
  "project_scope": "small|medium|large",
  "special_requirements": [
    "Any unique or special requirements mentioned"
  ],
  "contact_details": {
    "name": "if mentioned",
    "phone": "if mentioned",
    "email": "if mentioned"
  },
  "additional_notes": "Any other relevant information not captured above"
}
Objective Analysis Guidelines:
For each objective, provide:
Labor Difficulty Scale (All Bathroom Work):

1: Easy tasks (cleaning, basic maintenance, simple fixture replacement, mirror installation, caulking)
2: Medium tasks (toilet installation, vanity mounting, basic tiling, shower head replacement, minor plumbing repairs)
3: Hard tasks (plumbing rerouting, electrical work, waterproofing, complex tile work, structural changes, demolition, new construction)

Materials Required & Miscellaneous (All Bathroom Work):

Materials Required: Bathroom fixtures, tiles, plumbing supplies, electrical components, construction materials, demolition materials
Miscellaneous Materials: ALWAYS include tools, adhesives, sealants, safety equipment, cleaning supplies, protective gear
Use integer quantities only (1, 2, 5, 10, etc.)
Specify appropriate units separately
Common bathroom units: "unit", "piece", "m²", "m", "kg", "liter", "box", "roll", "set", "tube", "bag"
Examples:

New bathroom construction: Concrete (quantity=10, unit="bag"), Framing lumber (quantity=20, unit="piece")
Demolition: Dumpster rental (quantity=1, unit="unit"), Sledgehammer (quantity=1, unit="unit")
Maintenance: Cleaning supplies (quantity=5, unit="liter"), Replacement parts (quantity=3, unit="piece")
Repairs: Pipe fittings (quantity=5, unit="piece"), Sealant (quantity=2, unit="tube")


IMPORTANT: Include demolition tools, construction equipment, maintenance supplies, repair materials, and ALL necessary tools in miscellaneous materials
Tool Examples: Drill (quantity=1, unit="unit"), Tile cutter (quantity=1, unit="unit"), Wrench set (quantity=1, unit="set"), Level (quantity=1, unit="unit")

Estimated Time (All Bathroom Work):

Provide integer hours only (1, 2, 8, 24, etc.)
Convert days to hours (1 day = 8 hours, 2 days = 16 hours)
Consider typical completion times for all bathroom work types
For tasks less than 1 hour, use 1 as minimum
Examples: 2 (basic cleaning), 4 (tile removal), 16 (full retiling), 40 (new bathroom construction), 8 (demolition)

Confidence Score:

Rate confidence in the objective extraction (0.0 to 1.0)
Higher score = more explicit/clear in transcript
Lower score = inferred or assumed from context
Consider specificity of details provided

Analysis Guidelines:

Task Identification: Look for any bathroom-related work requests (construction, renovation, destruction, maintenance, repairs, installations, modifications, inspections)
Objective Extraction: Break down each bathroom task into specific, actionable work items
Budget Assessment: Analyze language, tone, and explicit budget mentions for bathroom projects
Location Detection: Extract any geographical references
Timeline Sensitivity: Note any urgency indicators or deadlines for bathroom work
Scope Assessment: Evaluate bathroom project size and complexity (small repair vs. full construction)
Quality Preferences: Identify fixture preferences, material choices, finish quality expectations
Bathroom-Specific Considerations: Note accessibility needs, storage requirements, ventilation needs, plumbing requirements, electrical needs

Important Notes:

If information is not available, use "not specified" or null values
Maintain consistency in formatting and terminology
Focus on actionable, measurable objectives
Consider bathroom industry-standard terminology and practices
Extract implied information from context when possible

Output only the JSON structure with no additional text or formatting."""

    user_message = f"Please parse the following transcript:\n\n{transcript}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": os.getenv("OPENROUTER_MODEL"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        print("Sending request to OpenRouter API...")
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()

        if result and result.get("choices") and result["choices"][0].get("message"):
            ai_response_content = result["choices"][0]["message"].get("content")
            
            cleaned_content = ai_response_content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            
            try:
                print("Parsing AI response to JSON...")
                parsed_json = json.loads(cleaned_content)
                
                print("Enriching with material pricing...")
                enriched_json = enrich_materials_with_pricing(parsed_json)
                
                print("Enriching with labor costs...")
                labor_enriched_json = enrich_with_labor_costs(enriched_json)
                
                print("Enriching with VAT and margins...")
                final_enriched_json = enrich_with_vat_and_margins(labor_enriched_json)

                results_dir = "output"
                os.makedirs(results_dir, exist_ok=True)

                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = os.path.join(results_dir, f"result_{timestamp}.json")

                with open(output_filename, "w", encoding="utf-8") as f:
                    json.dump(final_enriched_json, f, indent=2, ensure_ascii=False)
                
                print(f"Successfully parsed and saved fully enriched JSON to {output_filename}")
                
                print("\n" + "="*80)
                print("COMPREHENSIVE PRICING SUMMARY")
                print("="*80)
                print(f"Tasks parsed: {len(final_enriched_json.get('tasks', []))}")
                if final_enriched_json.get('location'):
                    print(f"Location: {final_enriched_json['location']}")
                if final_enriched_json.get('budget_level') is not None:
                    print(f"Budget Level: {final_enriched_json['budget_level']}")
                if final_enriched_json.get('project_scope'):
                    print(f"Project Scope: {final_enriched_json['project_scope']}")
                
                if final_enriched_json.get('pricing_summary'):
                    pricing = final_enriched_json['pricing_summary']
                    print(f"\nPRICING BREAKDOWN:")
                    print(f"Materials Cost: €{pricing.get('total_materials_cost', 0)}")
                    print(f"Labor Cost: €{pricing.get('total_labor_cost', 0)}")
                    print(f"Subtotal: €{pricing.get('total_project_cost', 0)}")
                    print(f"Total Margin: €{pricing.get('total_margin', 0)}")
                    print(f"Subtotal with Margin: €{pricing.get('subtotal_with_margin', 0)}")
                    print(f"Total VAT: €{pricing.get('total_vat', 0)}")
                    print(f"FINAL PROJECT COST: €{pricing.get('final_project_cost', 0)}")
                    print(f"Country: {pricing.get('country', 'Unknown')}")
                    print(f"Budget Level: {pricing.get('budget_level', 1)}")
                
                print(f"\nDETAILED TASK BREAKDOWN:")
                for i, task in enumerate(final_enriched_json.get('tasks', []), 1):
                    pricing_breakdown = task.get('pricing_breakdown', {})
                    print(f"\n{i}. {task.get('task_name', 'Unnamed Task')}")
                    print(f"   Objectives: {len(task.get('objectives', []))}")
                    print(f"   Complexity: {task.get('estimated_complexity', 'Unknown')}")
                    print(f"   Subtotal: €{pricing_breakdown.get('subtotal', 0)}")
                    print(f"   Margin: €{pricing_breakdown.get('margin', 0)}")
                    print(f"   VAT: €{pricing_breakdown.get('vat_amount', 0)}")
                    print(f"   Final Price: €{pricing_breakdown.get('final_price', 0)}")
                    
                    for j, objective in enumerate(task.get('objectives', []), 1):
                        obj_pricing = objective.get('pricing_breakdown', {})
                        print(f"     {j}. {objective.get('description', 'No description')}")
                        print(f"        Final Price: €{obj_pricing.get('final_price', 0)} "
                              f"(Subtotal: €{obj_pricing.get('subtotal', 0)}, "
                              f"Margin: €{obj_pricing.get('margin', 0)}, "
                              f"VAT: €{obj_pricing.get('vat_amount', 0)})")
                
                print("="*80)

            except json.JSONDecodeError as e:
                print(f"Error: Could not decode JSON from AI response: {e}")
                print("AI Response Content:", ai_response_content)
                
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                debug_filename = os.path.join("results", f"debug_response_{timestamp}.txt")
                with open(debug_filename, "w", encoding="utf-8") as f:
                    f.write(ai_response_content)
                print(f"Raw response saved to {debug_filename} for debugging")
                
        else:
            print("Error: Unexpected API response format.")
            print("Full response:", json.dumps(result, indent=2))

    except requests.exceptions.RequestException as e:
        print(f"API Request failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="Parse a transcript using OpenRouter API and enrich with material pricing, labor costs, VAT, and margins.")
    parser.add_argument("transcript", type=str, help="The transcript to be parsed.")
    args = parser.parse_args()

    if not args.transcript.strip():
        print("Error: Empty transcript provided.")
        return

    parse_transcript(args.transcript)

if __name__ == "__main__":
    main()