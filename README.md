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
