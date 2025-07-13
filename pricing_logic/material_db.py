import json
import os
import requests
from typing import Dict, List, Optional, Tuple
import logging
from dotenv import load_dotenv
load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaterialDB:
    """
    Material Database handler for construction materials pricing.
    Handles local JSON database and external API calls for missing materials.
    """
    
    def __init__(self, materials_file: str = "data/materials.json", api_key: str = None):
        """
        Initialize MaterialDB with materials file path and API key.
        
        Args:
            materials_file (str): Path to materials.json file
            api_key (str): OpenRouter API key for external lookups
        """
        self.materials_file = materials_file
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.materials_data = self._load_materials()
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.materials_file), exist_ok=True)
    
    def _load_materials(self) -> Dict:
        """Load materials from JSON file."""
        try:
            if os.path.exists(self.materials_file):
                with open(self.materials_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                logger.warning(f"Materials file not found: {self.materials_file}")
                return {}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Could not load materials file: {e}")
            return {}
    
    def _save_materials(self) -> None:
        """Save materials data to JSON file."""
        try:
            with open(self.materials_file, 'w', encoding='utf-8') as file:
                json.dump(self.materials_data, file, indent=2, ensure_ascii=False)
            logger.info(f"Materials database updated: {self.materials_file}")
        except Exception as e:
            logger.error(f"Error saving materials file: {e}")
    
    def _normalize_material_name(self, material_name: str) -> str:
        """
        Normalize material name for consistent lookup.
        
        Args:
            material_name (str): Raw material name
            
        Returns:
            str: Normalized material name
        """
        return material_name.lower().strip().replace(" ", "_").replace("-", "_")
    
    def get_material(self, material_name: str) -> Optional[Dict]:
        """
        Get material data from local database.
        
        Args:
            material_name (str): Material name to lookup
            
        Returns:
            Optional[Dict]: Material data if found, None otherwise
        """
        normalized_name = self._normalize_material_name(material_name)
        return self.materials_data.get(normalized_name)
    
    def get_multiple_materials(self, material_names: List[str]) -> Tuple[Dict[str, Dict], List[str]]:
        """
        Get multiple materials from local database.
        
        Args:
            material_names (List[str]): List of material names to lookup
            
        Returns:
            Tuple[Dict[str, Dict], List[str]]: Found materials and missing material names
        """
        found_materials = {}
        missing_materials = []
        
        for material_name in material_names:
            material_data = self.get_material(material_name)
            if material_data:
                found_materials[material_name] = material_data
            else:
                missing_materials.append(material_name)
        
        return found_materials, missing_materials
    
    def _call_openrouter_api(self, missing_materials: List[str]) -> Dict[str, Dict]:
        """
        Make API call to OpenRouter for missing materials.
        
        Args:
            missing_materials (List[str]): List of missing material names
            
        Returns:
            Dict[str, Dict]: Dictionary of material data from API
        """
        if not self.api_key:
            logger.error("OpenRouter API key not provided")
            return {}
        
        # Construct the prompt for the API
        materials_list = ", ".join(missing_materials)
        prompt = f"""
        You are a construction materials pricing expert. For each of the following materials: {materials_list}
        
        Please provide pricing and specifications for French construction market (Marseille region).
        
        Return ONLY a valid JSON object with this exact structure for each material:
        {{
            "material_name": {{
                "material_name": "original_material_name",
                "price": integer_price_in_euros,
                "quantity": integer_quantity,
                "unit": "unit_description_like_m²_or_L_or_pcs",
                "description": "brief_description_of_the_material"
            }}
        }}
        
        Requirements:
        - All prices must be realistic for French market
        - Price and quantity must be integers only
        - Units should be standard (m², L, pcs, kg, set, etc.)
        - Use underscore format for material names (e.g., "ceramic_tiles")
        - Provide market-appropriate pricing for construction materials
        
        Materials to price: {materials_list}
        """
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": os.getenv("OPENROUTER_MODEL"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Parse the JSON response
                try:
                    materials_data = json.loads(content)
                    logger.info(f"Successfully fetched {len(materials_data)} materials from API")
                    return materials_data
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse API response as JSON: {e}")
                    return {}
            else:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                return {}
                
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {}
    
    def _create_fallback_material(self, material_name: str) -> Dict:
        """
        Create fallback material data when API fails.
        
        Args:
            material_name (str): Material name
            
        Returns:
            Dict: Fallback material data
        """
        # Basic pricing estimates for common materials
        fallback_prices = {
            "tiles": (30, 1, "m²"),
            "paint": (40, 2, "L"),
            "plumbing": (100, 1, "set"),
            "toilet": (150, 1, "pcs"),
            "vanity": (200, 1, "pcs"),
            "shower": (120, 1, "set"),
            "cement": (8, 25, "kg"),
            "adhesive": (15, 20, "kg"),
            "grout": (12, 5, "kg")
        }
        
        # Try to match material name with fallback
        normalized_name = self._normalize_material_name(material_name)
        price, quantity, unit = (50, 1, "pcs")  # Default fallback
        
        for key, values in fallback_prices.items():
            if key in normalized_name:
                price, quantity, unit = values
                break
        
        return {
            "material_name": normalized_name,
            "price": price,
            "quantity": quantity,
            "unit": unit,
            "description": f"Estimated pricing for {material_name} (fallback data)"
        }
    
    def fetch_missing_materials(self, missing_materials: List[str]) -> Dict[str, Dict]:
        """
        Fetch missing materials from API and update local database.
        
        Args:
            missing_materials (List[str]): List of missing material names
            
        Returns:
            Dict[str, Dict]: Fetched material data
        """
        if not missing_materials:
            return {}
        
        logger.info(f"Fetching {len(missing_materials)} missing materials from API")
        
        # Try to fetch from API
        api_materials = self._call_openrouter_api(missing_materials)
        
        # Process results and create fallbacks if needed
        fetched_materials = {}
        
        for material_name in missing_materials:
            normalized_name = self._normalize_material_name(material_name)
            
            # Check if API returned data for this material
            if normalized_name in api_materials:
                material_data = api_materials[normalized_name]
                # Ensure data integrity
                if all(key in material_data for key in ["material_name", "price", "quantity", "unit", "description"]):
                    fetched_materials[material_name] = material_data
                    self.materials_data[normalized_name] = material_data
                else:
                    logger.warning(f"Incomplete API data for {material_name}, using fallback")
                    fallback_data = self._create_fallback_material(material_name)
                    fetched_materials[material_name] = fallback_data
                    self.materials_data[normalized_name] = fallback_data
            else:
                # Create fallback data
                logger.warning(f"No API data for {material_name}, using fallback")
                fallback_data = self._create_fallback_material(material_name)
                fetched_materials[material_name] = fallback_data
                self.materials_data[normalized_name] = fallback_data
        
        # Save updated materials database
        self._save_materials()
        
        return fetched_materials
    
    def get_materials_with_fallback(self, material_names: List[str]) -> Dict[str, Dict]:
        """
        Get materials with automatic fallback to API for missing items.
        
        Args:
            material_names (List[str]): List of material names to lookup
            
        Returns:
            Dict[str, Dict]: Complete material data for all requested materials
        """
        # First, try to get materials from local database
        found_materials, missing_materials = self.get_multiple_materials(material_names)
        
        # If there are missing materials, fetch them from API
        if missing_materials:
            fetched_materials = self.fetch_missing_materials(missing_materials)
            found_materials.update(fetched_materials)
        
        return found_materials
    
    def add_material(self, material_name: str, price: int, quantity: int, unit: str, description: str) -> bool:
        """
        Add or update material in the database.
        
        Args:
            material_name (str): Material name
            price (int): Price in euros
            quantity (int): Quantity per unit
            unit (str): Unit description
            description (str): Material description
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            normalized_name = self._normalize_material_name(material_name)
            
            self.materials_data[normalized_name] = {
                "material_name": normalized_name,
                "price": int(price),
                "quantity": int(quantity),
                "unit": unit,
                "description": description
            }
            
            self._save_materials()
            logger.info(f"Added/updated material: {normalized_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding material {material_name}: {e}")
            return False
    
    def list_all_materials(self) -> Dict[str, Dict]:
        """
        Get all materials from the database.
        
        Returns:
            Dict[str, Dict]: All materials in the database
        """
        return self.materials_data.copy()
    
    def search_materials(self, search_term: str) -> Dict[str, Dict]:
        """
        Search for materials by name or description.
        
        Args:
            search_term (str): Search term
            
        Returns:
            Dict[str, Dict]: Matching materials
        """
        search_term = search_term.lower()
        matching_materials = {}
        
        for material_name, material_data in self.materials_data.items():
            if (search_term in material_name.lower() or 
                search_term in material_data.get("description", "").lower()):
                matching_materials[material_name] = material_data
        
        return matching_materials


# Example usage and testing
if __name__ == "__main__":
    # Initialize MaterialDB
    material_db = MaterialDB()
    
    # Example: Get materials with automatic fallback
    test_materials = [
        "ceramic tiles",
        "wall paint", 
        "toilet",
        "bathroom_mirror",  # This might not exist in database
        "shower head"       # This might not exist in database
    ]
    
    print("Testing material lookup with fallback...")
    results = material_db.get_materials_with_fallback(test_materials)
    
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Example: Add a new material manually
    material_db.add_material(
        material_name="premium_tiles",
        price=45,
        quantity=1,
        unit="m²",
        description="Premium ceramic tiles with anti-slip coating"
    )
    
    print("\nAll materials in database:")
    all_materials = material_db.list_all_materials()
    for name, data in all_materials.items():
        print(f"- {name}: €{data['price']} per {data['quantity']} {data['unit']}")