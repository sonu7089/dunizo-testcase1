#!/usr/bin/env python3
"""
Test script for the bathroom pricing engine
Tests three different transcript scenarios through the complete pricing pipeline
"""

import os
import sys
import json
import datetime
from pathlib import Path

# Add the parent directory to path to import pricing_engine
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from pricing_engine import parse_transcript
except ImportError as e:
    print(f"Error importing pricing_engine: {e}")
    print("Make sure pricing_engine.py is in the parent directory")
    sys.exit(1)

class TestPricingEngine:
    def __init__(self):
        self.test_results = []
        self.test_directory = "tests/test_results"
        self.ensure_test_directory()
    
    def ensure_test_directory(self):
        """Create test results directory if it doesn't exist"""
        if not os.path.exists(self.test_directory):
            os.makedirs(self.test_directory)
            print(f"Created test results directory: {self.test_directory}")
    
    def run_transcript_test(self, transcript_name, transcript_text):
        """Run a single transcript test and capture results"""
        print(f"\n{'='*80}")
        print(f"RUNNING TEST: {transcript_name}")
        print(f"{'='*80}")
        print(f"Transcript: {transcript_text}")
        print(f"{'='*80}")
        
        try:
            # Store original stdout to capture print statements
            import io
            import contextlib
            
            # Capture stdout during parsing
            captured_output = io.StringIO()
            
            with contextlib.redirect_stdout(captured_output):
                parse_transcript(transcript_text)
            
            # Get the captured output
            output = captured_output.getvalue()
            
            # Also print to console
            print(output)
            
            # Try to find and load the generated JSON file
            results_dir = "output"
            if os.path.exists(results_dir):
                # Find the most recent result file
                result_files = [f for f in os.listdir(results_dir) if f.startswith("result_") and f.endswith(".json")]
                if result_files:
                    latest_file = max(result_files, key=lambda x: os.path.getctime(os.path.join(results_dir, x)))
                    latest_file_path = os.path.join(results_dir, latest_file)
                    
                    # Read the generated JSON
                    with open(latest_file_path, 'r', encoding='utf-8') as f:
                        result_json = json.load(f)
                    
                    # Save test-specific copy
                    test_result_file = os.path.join(self.test_directory, f"{transcript_name}_result.json")

                    with open(test_result_file, 'w', encoding='utf-8') as f:
                        json.dump(result_json, f, indent=2, ensure_ascii=False)
                    
                    # Save captured output
                    output_file = os.path.join(self.test_directory, f"{transcript_name}_output.txt")
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"Test: {transcript_name}\n")
                        f.write(f"Transcript: {transcript_text}\n")
                        f.write(f"{'='*80}\n")
                        f.write(output)
                    
                    # Store test result summary
                    test_result = {
                        "test_name": transcript_name,
                        "transcript": transcript_text,
                        "status": "SUCCESS",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "result_file": test_result_file,
                        "output_file": output_file,
                        "summary": self.extract_summary(result_json)
                    }
                    
                    self.test_results.append(test_result)
                    print(f"✅ Test {transcript_name} completed successfully")
                    print(f"Results saved to: {test_result_file}")
                    
                else:
                    print(f"❌ No result files found for {transcript_name}")
                    self.test_results.append({
                        "test_name": transcript_name,
                        "transcript": transcript_text,
                        "status": "FAILED - No result file",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "error": "No result file generated"
                    })
            else:
                print(f"❌ Results directory not found for {transcript_name}")
                self.test_results.append({
                    "test_name": transcript_name,
                    "transcript": transcript_text,
                    "status": "FAILED - No results directory",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "error": "Results directory not found"
                })
        
        except Exception as e:
            print(f"❌ Test {transcript_name} failed with error: {e}")
            import traceback
            traceback.print_exc()
            
            self.test_results.append({
                "test_name": transcript_name,
                "transcript": transcript_text,
                "status": "FAILED - Exception",
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e)
            })
    
    def extract_summary(self, result_json):
        """Extract key metrics from the result JSON"""
        summary = {}
        
        if 'pricing_summary' in result_json:
            pricing = result_json['pricing_summary']
            summary['total_materials_cost'] = pricing.get('total_materials_cost', 0)
            summary['total_labor_cost'] = pricing.get('total_labor_cost', 0)
            summary['total_project_cost'] = pricing.get('total_project_cost', 0)
            summary['total_margin'] = pricing.get('total_margin', 0)
            summary['total_vat'] = pricing.get('total_vat', 0)
            summary['final_project_cost'] = pricing.get('final_project_cost', 0)
            summary['country'] = pricing.get('country', 'Unknown')
            summary['budget_level'] = pricing.get('budget_level', 1)
        
        summary['location'] = result_json.get('location', 'Unknown')
        summary['project_scope'] = result_json.get('project_scope', 'Unknown')
        summary['tasks_count'] = len(result_json.get('tasks', []))
        summary['total_objectives'] = sum(len(task.get('objectives', [])) for task in result_json.get('tasks', []))
        
        return summary
    
    def run_all_tests(self):
        """Run all transcript tests"""
        print("🚀 Starting Bathroom Pricing Engine Tests")
        print(f"Test results will be saved to: {self.test_directory}")
        
        # Test transcripts
        transcripts = {
            "test_1_guest_bathroom": "We're looking to upgrade our guest bathroom — it's about 3.5 square meters. We'd like to remove the existing bathtub and replace it with a walk-in shower. The sink and mirror cabinet need to be modernized too. We'd also appreciate help choosing space-saving fixtures. Budget is moderate. We're in Lyon.",
            
            "test_2_dual_bathrooms": "We have two bathrooms we want to renovate. First is the master bath — around 6m². We'd like to install a freestanding tub, redo the tiling completely, and upgrade the lighting. The second is a smaller ensuite — just 2.5m². We need to replace the shower, update the vanity, and fix some minor water damage on the ceiling. We'd like both to have a cohesive look. Budget is flexible, depending on design. We're based in Toulouse.",
            
            "test_3_new_bathroom": "We're building an extension and want to add a new bathroom, roughly 5m². It'll need full plumbing installation, tiling, a shower enclosure, wall-hung toilet, and floating vanity. We haven't picked out materials yet, so would love recommendations. Our main concern is staying within a mid-range budget. Located in Nice."
        }
        
        # Run each test
        for test_name, transcript in transcripts.items():
            self.run_transcript_test(test_name, transcript)
        
        # Generate test summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate a comprehensive test summary"""
        print(f"\n{'='*80}")
        print("📊 TEST SUMMARY")
        print(f"{'='*80}")
        
        successful_tests = [r for r in self.test_results if r['status'] == 'SUCCESS']
        failed_tests = [r for r in self.test_results if r['status'] != 'SUCCESS']
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Successful: {len(successful_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        
        if failed_tests:
            print(f"\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['status']}")
                if 'error' in test:
                    print(f"    Error: {test['error']}")
        
        if successful_tests:
            print(f"\nSuccessful Test Results:")
            for test in successful_tests:
                summary = test['summary']
                print(f"\n🏗️  {test['test_name'].upper()}")
                print(f"  Location: {summary.get('location', 'Unknown')}")
                print(f"  Project Scope: {summary.get('project_scope', 'Unknown')}")
                print(f"  Budget Level: {summary.get('budget_level', 1)}")
                print(f"  Tasks: {summary.get('tasks_count', 0)}")
                print(f"  Objectives: {summary.get('total_objectives', 0)}")
                print(f"  Materials Cost: €{summary.get('total_materials_cost', 0)}")
                print(f"  Labor Cost: €{summary.get('total_labor_cost', 0)}")
                print(f"  Total Margin: €{summary.get('total_margin', 0)}")
                print(f"  Total VAT: €{summary.get('total_vat', 0)}")
                print(f"  FINAL COST: €{summary.get('final_project_cost', 0)}")
                print(f"  Country: {summary.get('country', 'Unknown')}")
        
        # Save test summary to file
        summary_file = os.path.join(self.test_directory, "test_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "test_run_timestamp": datetime.datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "successful_tests": len(successful_tests),
                "failed_tests": len(failed_tests),
                "results": self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed test summary saved to: {summary_file}")
        print(f"{'='*80}")
    
    def cleanup_old_results(self):
        """Clean up old result files to avoid confusion"""
        results_dir = "results"
        if os.path.exists(results_dir):
            try:
                for file in os.listdir(results_dir):
                    file_path = os.path.join(results_dir, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                print(f"🧹 Cleaned up old results from {results_dir}")
            except Exception as e:
                print(f"Warning: Could not clean up old results: {e}")

def main():
    """Main test runner"""
    print("🛠️  Bathroom Pricing Engine Test Suite")
    print("="*80)
    
    # Initialize test runner
    test_runner = TestPricingEngine()
    
    # Clean up old results
    test_runner.cleanup_old_results()
    
    # Run all tests
    test_runner.run_all_tests()
    
    print("\n🎉 All tests completed!")
    print(f"Check the '{test_runner.test_directory}' directory for detailed results")

if __name__ == "__main__":
    main()