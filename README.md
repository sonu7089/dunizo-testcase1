# Bathroom Pricing Engine

A comprehensive Python-based pricing engine for bathroom renovation projects. This system takes natural language descriptions of bathroom projects, parses them using AI, and generates detailed price quotes including materials, labor, margins, and VAT calculations.

## Project Structure

```
├── data/
│   ├── materials.json          # Material database with pricing
│   └── price_templates.csv     # Labor pricing templates by difficulty
├── output/                     # Generated pricing quotes (JSON)
├── pricing_engine.py          # Main orchestration script
├── pricing_logic/             # Core business logic modules
│   ├── material_db.py         # Material pricing and API fallback
│   ├── labor_calc.py          # Labor cost calculations
│   ├── vat_rules.py           # VAT rate determination
│   └── __pycache__/
├── tests/
│   ├── test_logic.py          # Comprehensive test suite
│   └── test_results/          # Test output artifacts
├── .env                       # Environment configuration
├── requirements.txt           # Python dependencies
└── README.md
```

## How to Run the Code

### Prerequisites
1. **Python 3.7+** installed on your system
2. **OpenRouter API key** for AI transcript parsing

### Installation & Setup

1. **Clone or download** the project files

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   OPENROUTER_MODEL=openrouter/cypher-alpha:free
   ```

### Running the Pricing Engine

**Basic Usage**:
```bash
python pricing_engine.py "Client wants to renovate a 4m² bathroom in Marseille. Remove old tiles, install new toilet, vanity, and ceramic flooring. Budget-conscious project."
```

**Example Commands**:
```bash
# Simple renovation
python pricing_engine.py "Small bathroom renovation in Paris - new tiles, paint, and fixtures"

# Complex project
python pricing_engine.py "Master bathroom renovation in Lyon: freestanding tub, walk-in shower, premium finishes, 8m² space"

# New construction
python pricing_engine.py "New bathroom construction in Nice - 5m² space, full plumbing, modern fixtures"
```

### Running Tests

**Execute the test suite**:
```bash
python tests/test_logic.py
```

This runs three comprehensive test scenarios and generates detailed reports in `tests/test_results/`.

## Output JSON Schema

The system generates detailed JSON files with the following structure:

```json
{
  "tasks": [
    {
      "task_id": "task_1",
      "task_name": "Bathroom renovation",
      "objectives": [
        {
          "objective_id": "obj_1",
          "description": "Install new ceramic tiles",
          "labor_difficulty": 2,
          "estimated_time": 8,
          "confidence_score": 0.85,
          "materials_required": [
            {
              "material": "ceramic_tiles",
              "quantity": 10,
              "unit": "m²",
              "unit_price": 25,
              "total_cost": 250,
              "description": "Standard ceramic floor tiles",
              "included_in_pricing": true
            }
          ],
          "miscellaneous_materials": [
            {
              "material": "tile_cutter",
              "quantity": 1,
              "unit": "unit",
              "total_cost": 50,
              "included_in_pricing": false
            }
          ],
          "cost_breakdown": {
            "materials_cost": 250,
            "miscellaneous_cost": 50,
            "total_materials_cost": 250,
            "labor_cost": 280,
            "total_cost": 530
          },
          "labor_cost_breakdown": {
            "difficulty_level": 2,
            "estimated_hours": 8,
            "base_hourly_rate": 35,
            "regional_multiplier": 1.0,
            "final_hourly_rate": 35,
            "total_labor_cost": 280
          },
          "vat_breakdown": {
            "materials_vat_rate": 0.055,
            "labor_vat_rate": 0.10,
            "materials_vat_amount": 13.75,
            "labor_vat_amount": 28,
            "total_vat_amount": 41.75
          },
          "pricing_breakdown": {
            "subtotal": 530,
            "margin": 79.5,
            "subtotal_with_margin": 609.5,
            "vat_amount": 41.75,
            "final_price": 651.25
          }
        }
      ],
      "estimated_complexity": "medium",
      "total_materials_cost": 250,
      "total_labor_cost": 280,
      "pricing_breakdown": {
        "subtotal": 530,
        "margin": 79.5,
        "subtotal_with_margin": 609.5,
        "vat_amount": 41.75,
        "final_price": 651.25
      }
    }
  ],
  "budget_level": 1,
  "location": "Marseille, France",
  "project_scope": "medium",
  "pricing_summary": {
    "total_materials_cost": 250,
    "total_labor_cost": 280,
    "total_project_cost": 530,
    "total_margin": 79.5,
    "subtotal_with_margin": 609.5,
    "total_vat": 41.75,
    "final_project_cost": 651.25,
    "country": "france",
    "budget_level": 1,
    "currency": "EUR"
  }
}
```

### Key JSON Fields

| Field                     | Description                          |
| ------------------------- | ------------------------------------ |
| `tasks`                   | Array of main project tasks          |
| `objectives`              | Specific work items within each task |
| `materials_required`      | Materials included in final pricing  |
| `miscellaneous_materials` | Tools/supplies excluded from pricing |
| `cost_breakdown`          | Detailed cost analysis per objective |
| `labor_cost_breakdown`    | Labor calculation details            |
| `vat_breakdown`           | VAT rates and amounts                |
| `pricing_breakdown`       | Final pricing with margins and VAT   |
| `pricing_summary`         | Project-level cost summary           |


## Pricing Logic Explanation

### 1. AI-Powered Transcript Parsing
- **Natural Language Processing**: Uses OpenRouter API to parse bathroom project descriptions
- **Structured Extraction**: Converts free-form text into structured project data
- **Task & Objective Identification**: Breaks down projects into actionable work items
- **Material & Labor Estimation**: Identifies required materials and estimates labor complexity

### 2. Material Pricing System
- **Local Database**: Primary source from `data/materials.json` (1300+ materials)
- **API Fallback**: OpenRouter API for missing materials with intelligent fallback pricing
- **Categorization**: Separates regular materials (included in pricing) from miscellaneous items (tools, excluded)
- **Price Validation**: Ensures realistic pricing for French construction market

### 3. Labor Cost Calculation

#### Difficulty-Based Pricing
| Level | Hourly Rate | Description   | Examples                                           |
| ----- | ----------- | ------------- | -------------------------------------------------- |
| 1     | €25         | Basic tasks   | Cleaning, caulking, simple repairs                 |
| 2     | €35         | Medium tasks  | Toilet installation, basic tiling, vanity mounting |
| 3     | €50         | Complex tasks | Plumbing rerouting, electrical work, waterproofing |


#### Regional Multipliers (Sample)
| City      | Multiplier |
| --------- | ---------- |
| Paris     | 1.30x      |
| Marseille | 1.00x      |
| Lyon      | 1.15x      |
| Nice      | 1.20x      |
| Toulouse  | 1.05x      |
| Bordeaux  | 1.15x      |


### 4. Margin Calculation System

#### Base Margin Rates
- **Materials**: 10% base margin
- **Labor**: 5% base margin  
- **Additional**: 15% total project margin

#### Budget Level Adjustments
| Level | Description        | Adjustment |
| ----- | ------------------ | ---------- |
| 0     | Tight budget       | -5%        |
| 1     | Moderate (default) | 0%         |
| 2     | Above normal       | +5%        |
| 3     | Premium            | +10%       |

#### Complexity Multipliers
| Complexity Level | Multiplier |
| ---------------- | ---------- |
| Low              | +0%        |
| Medium           | +5%        |
| High             | +10%       |


### 5. VAT Calculation Rules

#### French VAT Rates (Primary Market)
| Type                 | VAT Rate |
| -------------------- | -------- |
| Standard Rate        | 20%      |
| Renovation Materials | 5.5%     |
| Renovation Labor     | 10%      |
| New Construction     | 20%      |


#### Multi-Country Support
| Country | Standard Rate | Reduced Rate |
| ------- | ------------- | ------------ |
| Germany | 19%           | 7%           |
| Spain   | 21%           | 10%          |
| Italy   | 22%           | 10%          |


### 6. Final Pricing Formula

```
Subtotal = Materials Cost + Labor Cost
Adjusted Margin = Base Margin × (1 + Budget Adj + Complexity Adj) × Location Multiplier
Subtotal with Margin = Subtotal + Adjusted Margin
Final Price = Subtotal with Margin + VAT
```

## Key Assumptions & Edge Cases

### Core Assumptions
- **Currency**: All pricing in EUR (Euros)
- **Minimum Labor**: 1 hour minimum for any task
- **Material Exclusions**: Tools and consumables excluded from final client pricing
- **Default Budget**: Level 1 (Moderate) when not specified
- **Regional Defaults**: 1.0x multiplier for unknown locations

### Edge Cases Handled

#### Missing Data Scenarios
- **Unknown Materials**: Assigned €0 cost, flagged as `included_in_pricing: false`
- **Missing Labor Templates**: Uses default difficulty level 2 rates
- **Invalid Budget Levels**: Defaults to level 1 (moderate)
- **Unknown Locations**: Uses default 1.0x regional multiplier

#### Data Validation
- **Zero Quantities**: Minimum 1 unit applied
- **Negative Values**: Converted to positive or default values
- **Invalid Difficulty**: Clamped to 1-3 range
- **Missing Confidence Scores**: Defaults to 1.0 (full confidence)

#### API Failures
- **Material API Timeout**: Falls back to estimated pricing based on material type
- **Transcript Parsing Failure**: Provides detailed error messages and debug output
- **Network Issues**: Graceful degradation with local data only

### Quality Assurance Features
- **Confidence Scoring**: Each objective includes confidence level (0.0-1.0)
- **Pricing Transparency**: All calculations exposed in output JSON
- **Fallback Mechanisms**: Multiple layers of fallback for missing data
- **Validation Checks**: Input validation and data integrity checks throughout

## System Architecture

### Core Components

1. **pricing_engine.py**: Main orchestrator
   - Handles AI transcript parsing via OpenRouter API
   - Coordinates all pricing modules
   - Generates final JSON output
   - Provides comprehensive console reporting

2. **material_db.py**: Material pricing system
   - Local JSON database management
   - API integration for missing materials
   - Intelligent fallback pricing
   - Material categorization and validation

3. **labor_calc.py**: Labor cost calculator
   - Difficulty-based rate calculation
   - Regional pricing adjustments
   - Confidence-based modifications
   - Comprehensive French city coverage

4. **vat_rules.py**: VAT calculation engine
   - Multi-country VAT rate support
   - Work type classification (renovation vs. new construction)
   - Special material category handling
   - Location-based country detection

### Data Flow
```
Natural Language Input → AI Parsing → Material Pricing → Labor Calculation → Margin Application → VAT Calculation → Final JSON Output
```

## Future AI Enhancements

### Current AI Implementation
The system currently uses **OpenRouter API** for transcript parsing, which provides good results but has some limitations:
- **Network Dependency**: Requires internet connection for AI processing
- **API Costs**: Each transcript parsing incurs API usage costs
- **Generic Model**: Uses general-purpose language models not specialized for construction/renovation domain
- **Response Time**: Network latency affects processing speed

### Proposed Local AI Model
**Significant performance improvements** can be achieved by implementing a **small, specialized AI model** trained specifically for bathroom renovation transcript parsing:

#### Benefits of Local AI Model
- **🚀 Performance**: 10-50x faster processing without network calls
- **💰 Cost Reduction**: Eliminates ongoing API costs after initial training
- **🔒 Privacy**: All data processing happens locally
- **🎯 Domain Expertise**: Model trained specifically on bathroom renovation terminology
- **📱 Offline Capability**: Works without internet connection

#### Training Data Strategy
**Multi-Vendor Data Scraping** approach for comprehensive training:

1. **Vendor Catalog Integration**
   - Scrape product catalogs from major bathroom suppliers (Leroy Merlin, Castorama, Brico Dépôt)
   - Extract material specifications, pricing ranges, and compatibility information
   - Build comprehensive material knowledge base

2. **Construction Forum Analysis**
   - Parse renovation forums and Q&A sites for real project descriptions
   - Extract common terminology, project patterns, and cost expectations
   - Understand regional variations in language and preferences

3. **Professional Contractor Data**
   - Analyze contractor websites and project portfolios
   - Extract labor estimation patterns and complexity assessments
   - Build understanding of professional workflow and terminology

#### Enhanced Output Capabilities
With specialized training, the local model could provide:

**🎯 Multiple Vendor Options**
```json
{
  "material_options": [
    {
      "vendor": "Leroy Merlin",
      "product": "Ceramic Tiles Premium",
      "price": 28,
      "quality_score": 8.5,
      "availability": "in_stock"
    },
    {
      "vendor": "Castorama",
      "product": "Ceramic Tiles Standard",
      "price": 22,
      "quality_score": 7.2,
      "availability": "in_stock"
    },
    {
      "vendor": "Brico Dépôt",
      "product": "Ceramic Tiles Budget",
      "price": 18,
      "quality_score": 6.8,
      "availability": "limited_stock"
    }
  ]
}
```

**🎨 Budget-Optimized Recommendations**
- **Budget-Conscious**: Prioritize cost-effective materials and simpler installation methods
- **Mid-Range**: Balance quality and cost with good brand options
- **Premium**: Focus on high-end materials and specialized installation techniques

**📊 Constraint-Based Suggestions**
- **Time Constraints**: Suggest pre-fabricated solutions and faster installation methods
- **Space Limitations**: Recommend compact fixtures and space-saving designs
- **Accessibility Needs**: Prioritize accessible fixtures and safety features
- **Maintenance Preferences**: Suggest low-maintenance materials and finishes

#### Implementation Roadmap
1. **Phase 1**: Data collection and preprocessing from multiple vendor sources
2. **Phase 2**: Model training with bathroom-specific vocabulary and patterns
3. **Phase 3**: Integration testing with existing pricing engine
4. **Phase 4**: Performance optimization and deployment
5. **Phase 5**: Continuous learning from user feedback and new vendor data

#### Expected Improvements
- **Accuracy**: 15-25% improvement in material identification and quantity estimation
- **Speed**: 10-50x faster processing (milliseconds vs. seconds)
- **Cost**: 90%+ reduction in operational costs after initial development
- **Reliability**: Consistent performance without API dependencies
- **Customization**: Tailored recommendations based on regional preferences and vendor availability

This local AI enhancement would transform the system from a good pricing tool into a **comprehensive renovation planning assistant** that provides multiple options, vendor comparisons, and budget-optimized recommendations tailored to specific user constraints and preferences.

---

This comprehensive system ensures accurate, transparent, and detailed pricing for bathroom renovation projects across multiple European markets.
