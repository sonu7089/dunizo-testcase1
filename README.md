# Bathroom Pricing Engine

This project is a Python-based pricing engine for bathroom renovation projects. It takes a natural language description of a renovation project, parses it to understand the scope, and then calculates a detailed price quote including materials, labor, margins, and VAT.

## Project Structure

```
├── data/
│   ├── materials.json
│   └── price_templates.csv
├── output/
├── pricing_engine.py
├── pricing_logic/
│   ├── labor_calc.py
│   ├── material_db.py
│   └── vat_rules.py
├── requirements.txt
└── tests/
    ├── test_logic.py
    └── test_results/
```

- **data/**: Contains the raw data for materials and labor pricing.
  - `materials.json`: A database of materials with their prices and units.
  - `price_templates.csv`: Templates for labor costs based on difficulty.
- **output/**: Directory where the generated JSON price quotes are saved.
- **pricing_engine.py**: The main script that orchestrates the pricing process.
- **pricing_logic/**: A package containing the core business logic.
  - `material_db.py`: Handles fetching material prices from a local JSON file and can fall back to an external API.
  - `labor_calc.py`: Calculates labor costs based on task difficulty and regional multipliers.
  - `vat_rules.py`: Determines and applies the correct VAT rates based on location and work type.
- **tests/**: Contains the test suite for the pricing engine.
  - `test_logic.py`: The main test script that runs various scenarios.
  - `test_results/`: Directory where test artifacts are stored.
- `requirements.txt`: (Currently empty) Should contain the project's Python dependencies.

## How it Works

1.  **Parsing**: The `pricing_engine.py` takes a user's description of a bathroom project.
2.  **Material Pricing**: The `MaterialDB` class in `material_db.py` is used to look up the prices of all required materials. If a material is not found in the local `materials.json`, it can (optionally) query the OpenRouter API to get a price.
3.  **Labor Calculation**: The `LaborCalculator` in `labor_calc.py` determines the labor costs. It uses a CSV template (`price_templates.csv`) to find the base hourly rate for different difficulty levels and applies regional multipliers.
4.  **Margin Calculation**: The `MarginCalculator` in `pricing_engine.py` adds a business margin to the material and labor costs. The margin is adjusted based on budget level, project complexity, and location.
5.  **VAT Calculation**: The `VATRules` class in `vat_rules.py` calculates the Value Added Tax. It can detect the country from the location and apply different VAT rates for renovations vs. new constructions.
6.  **Output**: The final pricing breakdown is saved as a JSON file in the `output/` directory.

## Environment Variables

Create a `.env` file in the project root with the following content:

OPENROUTER_API_KEY=your_openrouter_api_key_here

OPENROUTER_MODEL=your_choice_of_model

This key is required for API access and should never be hardcoded in the codebase.

## How to Run

1.  **Install dependencies** (if any were listed in `requirements.txt`):
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the pricing engine**:
    ```bash
    python pricing_engine.py "YOUR_TRANSCRIPT_GOES_HERE"
    ```

3.  **Run tests**:
    ```bash
    python tests/test_logic.py
    ```

## Pricing Logic
The pricing engine calculates comprehensive project costs through a multi-stage process involving materials, labor, margins, and VAT calculations.

---

## Pricing Components

### 1. Materials Pricing

- **Regular Materials**: Included in final pricing calculations  
- **Miscellaneous Materials**: Priced for reference but excluded from final cost  
- **Pricing Source**: `data/materials.json`  
- **Fallback Mechanism**: Default pricing applied for missing materials  
- **Currency**: EUR

---

### 2. Labor Cost Calculation

- **Base Calculation**: Uses difficulty levels (1–3) and estimated hours  
- **Skill Multipliers**: Based on task complexity  
- **Regional Adjustments**: Location-based multipliers for different cities  
- **Confidence Adjustments**: Applied in cases of estimation uncertainty

---

### 3. Margin Calculations

#### Base Margin Rates
- **Materials**: 10%  
- **Labor**: 5%  
- **Total**: Additional 15% applied on top of subtotal  

#### Budget Level Adjustments
| Level | Description      | Adjustment |
|-------|------------------|------------|
| 0     | Tight            | -5%        |
| 1     | Moderate (Default)| 0%         |
| 2     | Above Normal     | +5%        |
| 3     | Premium          | +10%       |

#### Complexity Adjustments
| Complexity | Adjustment |
|------------|------------|
| Low        | 0%         |
| Medium     | +5%        |
| High       | +10%       |

#### Location Multipliers
| City      | Multiplier |
|-----------|------------|
| Paris     | 1.20x      |
| Lyon      | 1.15x      |
| Nice      | 1.10x      |
| Marseille | 1.00x      |
| Default   | 1.00x      |

---

### 4. VAT Calculation

- **Country Detection**: Based on project location  
- **Differentiated Rates**: Applied separately for materials and labor  
- **Multi-Country Support**: Supports multiple European VAT schemes  
- **Applied After**: Margin calculations

---

## Final Pricing Formula

Subtotal = Materials Cost + Labor Cost
Margin = (Subtotal × Margin Rate) × Location Multiplier × Complexity Factor
Subtotal with Margin = Subtotal + Margin
Final Price = Subtotal with Margin + VAT


---

## Key Assumptions & Edge Cases

### Assumptions
- All pricing in EUR  
- Minimum of 1-hour labor for any task  
- Miscellaneous materials (e.g., tools, consumables) **excluded** from final pricing  
- Default budget level: `1 (Moderate)`  
- Unknown city = Default location multiplier `1.0`

### Edge Cases Handled
- **Missing Material Pricing**: Assigned `€0`, flagged as `included_in_pricing: false`  
- **Unknown Locations**: Use default multiplier  
- **Invalid Budget Levels**: Default to level `1`  
- **Zero Quantities**: Graceful fallback applied  
- **Missing Labor Data**: Confidence-based adjustment applied

---

## Cost Structure

| Component  | Description                                                       |
|------------|-------------------------------------------------------------------|
| Materials  | Primary cost passed to the client                                 |
| Labor      | Skilled trade rates with complexity and regional adjustments      |
| Margins    | Tiered margins based on project complexity and client budget      |
| VAT        | Applied based on country-specific tax laws                        |

---

## Output Structure

The system generates detailed cost breakdowns at:

- **Project Level**: Total cost, margins, VAT, final pricing  
- **Task Level**: Individual task breakdown  
- **Objective Level**: Per work item analysis

>  All calculations maintain transparency for client review and internal cost validation.
