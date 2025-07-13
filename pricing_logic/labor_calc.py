import csv
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class LaborCalculator:
    """
    Labor cost calculation system for bathroom renovation projects.
    Handles different labor difficulty levels and regional pricing variations.
    """
    
    def __init__(self, price_templates_file: str = "data/price_templates.csv"):
        """
        Initialize the labor calculator with price templates.
        
        Args:
            price_templates_file (str): Path to the CSV file containing labor pricing templates
        """
        self.price_templates_file = price_templates_file
        self.labor_rates = {}
        self.regional_multipliers = {}
        self.load_price_templates()
        self.load_regional_multipliers()
    
    def load_price_templates(self):
        """Load labor pricing templates from CSV file."""
        try:
            if not os.path.exists(self.price_templates_file):
                print(f"Warning: Price templates file not found: {self.price_templates_file}")
                print("Using default labor rates...")
                self._use_default_rates()
                return
            
            with open(self.price_templates_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        difficulty = int(row['labor_difficulty'])
                        self.labor_rates[difficulty] = {
                            'base_hourly_rate': float(row['base_hourly_rate']),
                            'skill_multiplier': float(row['skill_multiplier']),
                            'complexity_factor': float(row['complexity_factor']),
                            'description': row['description'],
                            'typical_tasks': row['typical_tasks'].split(';') if row['typical_tasks'] else []
                        }
                    except (ValueError, KeyError) as e:
                        print(f"Error parsing row in price templates: {e}")
                        continue
            
            print(f"Loaded {len(self.labor_rates)} labor difficulty levels")
            
        except Exception as e:
            print(f"Error loading price templates: {e}")
            self._use_default_rates()
    
    def _use_default_rates(self):
        """Use default labor rates if CSV file is not available."""
        self.labor_rates = {
            1: {
                'base_hourly_rate': 25.0,
                'skill_multiplier': 1.0,
                'complexity_factor': 1.0,
                'description': 'Basic tasks - cleaning, simple maintenance, fixture replacement',
                'typical_tasks': ['cleaning', 'basic maintenance', 'simple fixture replacement', 'mirror installation', 'caulking']
            },
            2: {
                'base_hourly_rate': 35.0,
                'skill_multiplier': 1.2,
                'complexity_factor': 1.1,
                'description': 'Medium tasks - toilet installation, vanity mounting, basic tiling',
                'typical_tasks': ['toilet installation', 'vanity mounting', 'basic tiling', 'shower head replacement', 'minor plumbing repairs']
            },
            3: {
                'base_hourly_rate': 50.0,
                'skill_multiplier': 1.5,
                'complexity_factor': 1.3,
                'description': 'Hard tasks - plumbing rerouting, electrical work, waterproofing',
                'typical_tasks': ['plumbing rerouting', 'electrical work', 'waterproofing', 'complex tile work', 'structural changes', 'demolition']
            }
        }
    
    def load_regional_multipliers(self):
        """Load regional pricing multipliers for different cities/regions."""
        # Regional multipliers based on typical French city pricing
        self.regional_multipliers = {
            'paris': 1.3,
            'marseille': 1.0,
            'lyon': 1.15,
            'toulouse': 1.05,
            'nice': 1.2,
            'nantes': 1.1,
            'montpellier': 1.05,
            'strasbourg': 1.1,
            'bordeaux': 1.15,
            'lille': 1.05,
            'rennes': 1.05,
            'reims': 1.0,
            'saint-etienne': 0.95,
            'toulon': 1.1,
            'grenoble': 1.1,
            'dijon': 1.0,
            'angers': 1.0,
            'villeurbanne': 1.1,
            'le mans': 0.95,
            'aix-en-provence': 1.15,
            'clermont-ferrand': 0.95,
            'brest': 1.0,
            'tours': 1.0,
            'limoges': 0.9,
            'besancon': 0.95,
            'orleans': 1.0,
            'metz': 1.0,
            'rouen': 1.05,
            'mulhouse': 1.0,
            'perpignan': 0.95,
            'caen': 1.0,
            'boulogne-billancourt': 1.25,
            'nancy': 1.0,
            'saint-denis': 1.2,
            'argenteuil': 1.15,
            'roubaix': 1.0,
            'tourcoing': 1.0,
            'nimes': 1.0,
            'vitry-sur-seine': 1.15,
            'créteil': 1.15,
            'avignon': 1.05,
            'poitiers': 0.95,
            'fort-de-france': 1.1,
            'courbevoie': 1.25,
            'versailles': 1.2,
            'colombes': 1.15,
            'aulnay-sous-bois': 1.1,
            'saint-pierre': 1.1,
            'rueil-malmaison': 1.2,
            'pau': 1.0,
            'le havre': 1.05,
            'champigny-sur-marne': 1.1,
            'antibes': 1.15,
            'la rochelle': 1.05,
            'cannes': 1.2,
            'calais': 1.0,
            'noisy-le-grand': 1.1,
            'drancy': 1.1,
            'ajaccio': 1.15,
            'levallois-perret': 1.25,
            'issy-les-moulineaux': 1.2,
            'antony': 1.15,
            'villeneuve-dascq': 1.05,
            'neuilly-sur-seine': 1.3,
            'cergy': 1.1,
            'troyes': 0.95,
            'montrouge': 1.2,
            'châtillon': 1.15,
            'sarcelles': 1.1,
            'meudon': 1.15,
            'saint-maur-des-fosses': 1.15,
            'saint-nazaire': 1.0,
            'colmar': 1.05,
            'istres': 1.0,
            'quimper': 1.0,
            'merignac': 1.1,
            'villejuif': 1.15,
            'saint-andre': 1.1,
            'pessac': 1.1,
            'ivry-sur-seine': 1.15,
            'clichy': 1.2,
            'lorient': 1.0,
            'saint-ouen': 1.2,
            'saint-quentin': 1.0,
            'les abymes': 1.1,
            'la seyne-sur-mer': 1.05,
            'hyères': 1.1,
            'valence': 1.0,
            'wattrelos': 1.0,
            'meaux': 1.1,
            'nanterre': 1.2,
            'chelles': 1.1,
            'bourges': 0.95,
            'charleville-mezieres': 0.95,
            'annecy': 1.15,
            'caluire-et-cuire': 1.1,
            'saint-priest': 1.1,
            'saint-martin-dheres': 1.1,
            'sevran': 1.1,
            'cholet': 1.0,
            'vannes': 1.0,
            'frejus': 1.15,
            'bayonne': 1.05,
            'saint-germain-en-laye': 1.2,
            'epinay-sur-seine': 1.1,
            'montauban': 1.0,
            'rosny-sous-bois': 1.1,
            'arles': 1.0,
            'cagnes-sur-mer': 1.15,
            'saint-raphael': 1.15,
            'chalons-en-champagne': 0.95,
            'sartrouville': 1.15,
            'laval': 1.0,
            'massy': 1.15,
            'venissieux': 1.1,
            'saint-louis': 1.05,
            'beauvais': 1.05,
            'choisy-le-roi': 1.15,
            'perigueux': 0.95,
            'gap': 1.0,
            'chartres': 1.05,
            'bourg-en-bresse': 1.0,
            'tarbes': 1.0,
            'brive-la-gaillarde': 0.95,
            'angouleme': 0.95,
            'saint-herblain': 1.1,
            'saumur': 1.0,
            'blois': 1.0,
            'saint-chamond': 0.95,
            'saint-brieuc': 1.0,
            'niort': 1.0,
            'castres': 1.0,
            'arras': 1.0,
            'salon-de-provence': 1.05,
            'auxerre': 0.95,
            'saint-malo': 1.05,
            'thionville': 1.0,
            'roanne': 0.95,
            'le cannet': 1.2,
            'boulogne-sur-mer': 1.0,
            'albi': 1.0,
            'charleville-mezieres': 0.95,
            'cambrai': 1.0,
            'macon': 1.0,
            'compiegne': 1.05,
            'saint-etienne-du-rouvray': 1.05,
            'tremblay-en-france': 1.1,
            'bagneux': 1.15,
            'fleury-les-aubrais': 1.0,
            'saint-martin': 1.1,
            'vincennes': 1.25,
            'draguignan': 1.1,
            'chatou': 1.15,
            'montlucon': 0.9,
            'saint-joseph': 1.1,
            'villefranche-sur-saone': 1.1,
            'evreux': 1.0,
            'pontoise': 1.1,
            'flers': 1.0,
            'rodez': 0.95,
            'agde': 1.05,
            'epinal': 0.95,
            'guyancourt': 1.15,
            'carcassonne': 1.0,
            'fontenay-sous-bois': 1.15,
            'bondy': 1.1,
            'creteil': 1.15,
            'saint-benoit': 1.1,
            'nogent-sur-marne': 1.15,
            'saint-laurent-du-var': 1.15,
            'pontault-combault': 1.1,
            'saint-pol-sur-mer': 1.0,
            'palaiseau': 1.15,
            'six-fours-les-plages': 1.05,
            'saint-priest': 1.1,
            'houilles': 1.15,
            'epinay-sur-seine': 1.1,
            'savigny-sur-orge': 1.1,
            'franconville': 1.1,
            'goussainville': 1.1,
            'reze': 1.1,
            'livry-gargan': 1.1,
            'herblay': 1.1,
            'taverny': 1.1,
            'viry-chatillon': 1.1,
            'conflans-sainte-honorine': 1.1,
            'saint-cloud': 1.2,
            'neuilly-plaisance': 1.15,
            'villemomble': 1.1,
            'montfermeil': 1.1,
            'chatillon': 1.15,
            'garges-les-gonesse': 1.1,
            'pierrefitte-sur-seine': 1.1,
            'villeneuve-le-roi': 1.1,
            'fresnes': 1.1,
            'rungis': 1.15,
            'gentilly': 1.15,
            'villejuif': 1.15,
            'le kremlin-bicetre': 1.15,
            'cachan': 1.15,
            'vincennes': 1.25,
            'saint-mande': 1.2,
            'charenton-le-pont': 1.2,
            'nogent-sur-marne': 1.15,
            'joinville-le-pont': 1.15,
            'saint-maur-des-fosses': 1.15,
            'creteil': 1.15,
            'saint-maurice': 1.15,
            'alfortville': 1.15,
            'vitry-sur-seine': 1.15,
            'thiais': 1.1,
            'chevilly-larue': 1.1,
            'rungis': 1.15,
            'orly': 1.15,
            'villejuif': 1.15,
            'l-hay-les-roses': 1.1,
            'fresnes': 1.1,
            'antony': 1.15,
            'bourg-la-reine': 1.15,
            'sceaux': 1.2,
            'chatenay-malabry': 1.15,
            'le plessis-robinson': 1.15,
            'clamart': 1.15,
            'issy-les-moulineaux': 1.2,
            'vanves': 1.2,
            'malakoff': 1.15,
            'montrouge': 1.2,
            'chatillon': 1.15,
            'bagneux': 1.15,
            'fontenay-aux-roses': 1.15,
            'sceaux': 1.2,
            'robinson': 1.15,
            'velizy-villacoublay': 1.15,
            'chaville': 1.15,
            'sevres': 1.2,
            'saint-cloud': 1.2,
            'garches': 1.2,
            'vaucresson': 1.2,
            'ville-d-avray': 1.2,
            'marnes-la-coquette': 1.25,
            'rueil-malmaison': 1.2,
            'nanterre': 1.2,
            'puteaux': 1.25,
            'courbevoie': 1.25,
            'levallois-perret': 1.25,
            'neuilly-sur-seine': 1.3,
            'bois-colombes': 1.2,
            'colombes': 1.15,
            'asnieres-sur-seine': 1.15,
            'gennevilliers': 1.15,
            'villeneuve-la-garenne': 1.15,
            'clichy': 1.2,
            'saint-ouen': 1.2,
            'saint-denis': 1.2,
            'aubervilliers': 1.15,
            'la courneuve': 1.1,
            'stains': 1.1,
            'pierrefitte-sur-seine': 1.1,
            'villetaneuse': 1.1,
            'epinay-sur-seine': 1.1,
            'l-ile-saint-denis': 1.15,
            'montmagny': 1.1,
            'deuil-la-barre': 1.1,
            'enghien-les-bains': 1.15,
            'saint-gratien': 1.1,
            'eaubonne': 1.1,
            'ermont': 1.1,
            'franconville': 1.1,
            'saint-leu-la-foret': 1.1,
            'taverny': 1.1,
            'herblay': 1.1,
            'conflans-sainte-honorine': 1.1,
            'acheres': 1.1,
            'poissy': 1.1,
            'carrieres-sur-seine': 1.15,
            'houilles': 1.15,
            'sartrouville': 1.15,
            'maisons-laffitte': 1.2,
            'le mesnil-le-roi': 1.2,
            'le pecq': 1.2,
            'le vesinet': 1.2,
            'chatou': 1.15,
            'croissy-sur-seine': 1.2,
            'bougival': 1.2,
            'la celle-saint-cloud': 1.2,
            'rocquencourt': 1.2,
            'versailles': 1.2,
            'le chesnay': 1.2,
            'viroflay': 1.2,
            'chaville': 1.15,
            'meudon': 1.15,
            'bellevue': 1.15,
            'sevres': 1.2,
            'saint-cloud': 1.2,
            'suresnes': 1.2,
            'puteaux': 1.25,
            'courbevoie': 1.25,
            'la defense': 1.3,
            'default': 1.0  # Default multiplier for unknown cities
        }
    
    def get_regional_multiplier(self, location: str) -> float:
        """
        Get the regional pricing multiplier for a given location.
        
        Args:
            location (str): Location string (e.g., "Marseille", "Paris", "Lyon, France")
            
        Returns:
            float: Regional pricing multiplier
        """
        if not location:
            return self.regional_multipliers['default']
        
        # Clean and normalize location string
        location_clean = location.lower().strip()
        
        # Remove common suffixes and prefixes
        location_clean = location_clean.replace(', france', '')
        location_clean = location_clean.replace(', fr', '')
        location_clean = location_clean.replace('france', '')
        location_clean = location_clean.split(',')[0].strip()  # Take first part if comma-separated
        
        # Direct lookup
        if location_clean in self.regional_multipliers:
            return self.regional_multipliers[location_clean]
        
        # Partial matching for common variations
        for city, multiplier in self.regional_multipliers.items():
            if city != 'default' and (city in location_clean or location_clean in city):
                return multiplier
        
        # Default multiplier if no match found
        return self.regional_multipliers['default']
    
    def calculate_labor_cost(self, 
                           difficulty: int, 
                           estimated_hours: float, 
                           location: str = None,
                           confidence_score: float = 1.0) -> Dict[str, float]:
        """
        Calculate labor cost for a specific task.
        
        Args:
            difficulty (int): Labor difficulty level (1-3)
            estimated_hours (float): Estimated time in hours
            location (str, optional): Location for regional pricing
            confidence_score (float): Confidence score (0.0-1.0) for adjusting pricing
            
        Returns:
            Dict containing labor cost breakdown
        """
        # Validate inputs
        if difficulty not in self.labor_rates:
            print(f"Warning: Unknown difficulty level {difficulty}, using level 2")
            difficulty = 2
        
        if estimated_hours <= 0:
            print(f"Warning: Invalid estimated hours {estimated_hours}, using 1 hour")
            estimated_hours = 1
        
        # Get base labor rates
        labor_info = self.labor_rates[difficulty]
        base_rate = labor_info['base_hourly_rate']
        skill_multiplier = labor_info['skill_multiplier']
        complexity_factor = labor_info['complexity_factor']
        
        # Calculate effective hourly rate
        effective_rate = base_rate * skill_multiplier * complexity_factor
        
        # Apply regional multiplier
        regional_multiplier = self.get_regional_multiplier(location)
        regional_rate = effective_rate * regional_multiplier
        
        # Apply confidence score adjustment (lower confidence = higher safety margin)
        confidence_adjustment = 1.0 + (0.2 * (1.0 - confidence_score))
        final_rate = regional_rate * confidence_adjustment
        
        # Calculate total labor cost
        total_labor_cost = final_rate * estimated_hours
        
        return {
            'base_hourly_rate': base_rate,
            'skill_multiplier': skill_multiplier,
            'complexity_factor': complexity_factor,
            'effective_hourly_rate': effective_rate,
            'regional_multiplier': regional_multiplier,
            'regional_hourly_rate': regional_rate,
            'confidence_adjustment': confidence_adjustment,
            'final_hourly_rate': final_rate,
            'estimated_hours': estimated_hours,
            'total_labor_cost': total_labor_cost,
            'difficulty_level': difficulty,
            'difficulty_description': labor_info['description']
        }
    
    def calculate_objective_labor_cost(self, 
                                     objective: Dict, 
                                     location: str = None) -> Dict[str, float]:
        """
        Calculate labor cost for a complete objective.
        
        Args:
            objective (Dict): Objective dictionary containing labor_difficulty and estimated_time
            location (str, optional): Location for regional pricing
            
        Returns:
            Dict containing labor cost breakdown
        """
        difficulty = objective.get('labor_difficulty', 2)
        estimated_hours = objective.get('estimated_time', 1)
        confidence_score = objective.get('confidence_score', 1.0)
        
        return self.calculate_labor_cost(difficulty, estimated_hours, location, confidence_score)
    
    def get_labor_summary(self, location: str = None) -> Dict:
        """
        Get a summary of available labor rates and regional information.
        
        Args:
            location (str, optional): Location for regional pricing
            
        Returns:
            Dict containing labor rate summary
        """
        regional_multiplier = self.get_regional_multiplier(location)
        
        summary = {
            'regional_multiplier': regional_multiplier,
            'location': location,
            'difficulty_levels': {}
        }
        
        for difficulty, info in self.labor_rates.items():
            effective_rate = info['base_hourly_rate'] * info['skill_multiplier'] * info['complexity_factor']
            regional_rate = effective_rate * regional_multiplier
            
            summary['difficulty_levels'][difficulty] = {
                'description': info['description'],
                'base_rate': info['base_hourly_rate'],
                'effective_rate': effective_rate,
                'regional_rate': regional_rate,
                'typical_tasks': info['typical_tasks']
            }
        
        return summary

# Example usage and testing
if __name__ == "__main__":
    # Test the labor calculator
    labor_calc = LaborCalculator()
    
    # Test different scenarios
    test_cases = [
        {'difficulty': 1, 'hours': 2, 'location': 'Marseille'},
        {'difficulty': 2, 'hours': 8, 'location': 'Paris'},
        {'difficulty': 3, 'hours': 16, 'location': 'Lyon'},
        {'difficulty': 2, 'hours': 4, 'location': 'Unknown City'},
    ]
    
    print("=== Labor Calculator Test ===")
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: Difficulty {test['difficulty']}, {test['hours']} hours, {test['location']}")
        result = labor_calc.calculate_labor_cost(
            test['difficulty'], 
            test['hours'], 
            test['location']
        )
        print(f"  Total Labor Cost: €{result['total_labor_cost']:.2f}")
        print(f"  Effective Rate: €{result['final_hourly_rate']:.2f}/hour")
        print(f"  Regional Multiplier: {result['regional_multiplier']:.2f}")
    
    # Test with objective format
    print("\n=== Objective Format Test ===")
    test_objective = {
        'labor_difficulty': 2,
        'estimated_time': 6,
        'confidence_score': 0.8
    }
    
    result = labor_calc.calculate_objective_labor_cost(test_objective, 'Marseille')
    print(f"Objective Labor Cost: €{result['total_labor_cost']:.2f}")
    
    # Show summary
    print("\n=== Labor Summary for Marseille ===")
    summary = labor_calc.get_labor_summary('Marseille')
    for difficulty, info in summary['difficulty_levels'].items():
        print(f"Level {difficulty}: {info['description']} - €{info['regional_rate']:.2f}/hour")