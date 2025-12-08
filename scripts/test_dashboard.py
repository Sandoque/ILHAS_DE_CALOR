#!/usr/bin/env python3
"""
Test script for ETAPA 4 Dashboard endpoints and functionality.

Usage:
    python scripts/test_dashboard.py --all
    python scripts/test_dashboard.py --endpoint /api/gold/cidades
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"
DASHBOARD_BASE = f"{BASE_URL}/dashboard"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def log_pass(self, test_name: str, message: str = ""):
        self.passed += 1
        msg = f"{GREEN}✓{RESET} {test_name}"
        if message:
            msg += f" - {message}"
        print(msg)
        self.tests.append({"name": test_name, "status": "pass"})
    
    def log_fail(self, test_name: str, error: str):
        self.failed += 1
        print(f"{RED}✗{RESET} {test_name} - {error}")
        self.tests.append({"name": test_name, "status": "fail", "error": error})
    
    def log_info(self, message: str):
        print(f"{BLUE}ℹ{RESET} {message}")
    
    def log_skip(self, test_name: str, reason: str):
        print(f"{YELLOW}⊘{RESET} {test_name} - {reason}")
        self.tests.append({"name": test_name, "status": "skip", "reason": reason})
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"Test Results: {GREEN}{self.passed} passed{RESET}, {RED}{self.failed} failed{RESET} ({total} total)")
        print(f"{'='*60}")
        return self.failed == 0

# Initialize
runner = TestRunner()

# ============================================================================
# ENDPOINT TESTS
# ============================================================================

def test_dashboard_index():
    """Test GET /dashboard"""
    runner.log_info("Testing GET /dashboard (main page)")
    try:
        response = requests.get(f"{DASHBOARD_BASE}/")
        if response.status_code == 200:
            if "Dashboard" in response.text and "Ilhas de Calor" in response.text:
                runner.log_pass("Dashboard Index", f"HTTP {response.status_code}")
            else:
                runner.log_fail("Dashboard Index", "Expected text not found in response")
        else:
            runner.log_fail("Dashboard Index", f"HTTP {response.status_code}")
    except Exception as e:
        runner.log_fail("Dashboard Index", str(e))

def test_api_cidades():
    """Test GET /api/gold/cidades"""
    runner.log_info("Testing GET /api/gold/cidades")
    try:
        response = requests.get(f"{API_BASE}/gold/cidades")
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and isinstance(data.get("data"), list):
                cidades = data["data"]
                if len(cidades) > 0:
                    runner.log_pass("API /cidades", f"Retrieved {len(cidades)} cities")
                    
                    # Validate first city structure
                    first_cidade = cidades[0]
                    required_fields = ["id_cidade", "nome_cidade", "uf", "codigo_ibge"]
                    missing = [f for f in required_fields if f not in first_cidade]
                    if not missing:
                        runner.log_pass("API /cidades Structure", "All required fields present")
                        return cidades[0]["id_cidade"]  # Return first city ID for next tests
                    else:
                        runner.log_fail("API /cidades Structure", f"Missing fields: {missing}")
                else:
                    runner.log_skip("API /cidades", "No cities in database (run ETL first)")
            else:
                runner.log_fail("API /cidades", "Invalid response format")
        else:
            runner.log_fail("API /cidades", f"HTTP {response.status_code}")
    except Exception as e:
        runner.log_fail("API /cidades", str(e))
    
    return None

def test_api_resumo(cidade_id: Optional[int] = None):
    """Test GET /api/gold/<id>/resumo"""
    if not cidade_id:
        runner.log_skip("API /resumo", "No valid city ID")
        return
    
    runner.log_info(f"Testing GET /api/gold/{cidade_id}/resumo")
    try:
        response = requests.get(f"{API_BASE}/gold/{cidade_id}/resumo")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                resumo = data.get("data")
                required_fields = [
                    "id_cidade", "nome_cidade", "risco_calor", 
                    "temp_max", "temp_media", "temp_min", "umidade_media",
                    "dias_risco_alto_7d", "tendencia_temp"
                ]
                missing = [f for f in required_fields if f not in resumo]
                if not missing:
                    runner.log_pass("API /resumo", f"All fields present for {resumo['nome_cidade']}")
                    
                    # Validate field types and ranges
                    if resumo["risco_calor"] in ["Baixo", "Moderado", "Alto", "Muito Alto", "Extremo"]:
                        runner.log_pass("API /resumo Risk", f"Valid risk: {resumo['risco_calor']}")
                    else:
                        runner.log_fail("API /resumo Risk", f"Invalid risk: {resumo['risco_calor']}")
                    
                    if 0 <= resumo.get("dias_risco_alto_7d", -1) <= 7:
                        runner.log_pass("API /resumo 7d Dias", f"{resumo['dias_risco_alto_7d']} days")
                    else:
                        runner.log_fail("API /resumo 7d Dias", f"Invalid dias: {resumo['dias_risco_alto_7d']}")
                else:
                    runner.log_fail("API /resumo", f"Missing fields: {missing}")
            else:
                runner.log_fail("API /resumo", "success: false")
        else:
            runner.log_fail("API /resumo", f"HTTP {response.status_code}")
    except Exception as e:
        runner.log_fail("API /resumo", str(e))

def test_api_diario(cidade_id: Optional[int] = None):
    """Test GET /api/gold/<id>/diario"""
    if not cidade_id:
        runner.log_skip("API /diario", "No valid city ID")
        return
    
    runner.log_info(f"Testing GET /api/gold/{cidade_id}/diario")
    try:
        response = requests.get(f"{API_BASE}/gold/{cidade_id}/diario")
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and isinstance(data.get("data"), list):
                records = data["data"]
                if len(records) > 0:
                    runner.log_pass("API /diario", f"Retrieved {len(records)} records")
                    
                    # Validate first record
                    first = records[0]
                    expected = ["data", "temp_min", "temp_media", "temp_max", "risco_calor"]
                    missing = [f for f in expected if f not in first]
                    if not missing:
                        runner.log_pass("API /diario Structure", "All fields present")
                    else:
                        runner.log_fail("API /diario Structure", f"Missing: {missing}")
                else:
                    runner.log_skip("API /diario", "No records for this city")
            else:
                runner.log_fail("API /diario", "Invalid response format")
        else:
            runner.log_fail("API /diario", f"HTTP {response.status_code}")
    except Exception as e:
        runner.log_fail("API /diario", str(e))

def test_api_serie(cidade_id: Optional[int] = None):
    """Test GET /api/gold/<id>/serie"""
    if not cidade_id:
        runner.log_skip("API /serie", "No valid city ID")
        return
    
    runner.log_info(f"Testing GET /api/gold/{cidade_id}/serie")
    try:
        # Test with limit parameter
        response = requests.get(f"{API_BASE}/gold/{cidade_id}/serie?limit=7")
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                records = data.get("data", {}).get("data", [])
                if len(records) <= 7:
                    runner.log_pass("API /serie Limit", f"Limit 7 respected ({len(records)} records)")
                else:
                    runner.log_fail("API /serie Limit", f"Got {len(records)}, expected ≤7")
            else:
                runner.log_fail("API /serie", "success: false")
        else:
            runner.log_fail("API /serie", f"HTTP {response.status_code}")
        
        # Test with date range
        today = datetime.now().date()
        start = today - timedelta(days=30)
        response = requests.get(
            f"{API_BASE}/gold/{cidade_id}/serie",
            params={"start_date": start.isoformat(), "end_date": today.isoformat()}
        )
        if response.status_code == 200:
            runner.log_pass("API /serie Date Range", "Date filter works")
        else:
            runner.log_fail("API /serie Date Range", f"HTTP {response.status_code}")
    
    except Exception as e:
        runner.log_fail("API /serie", str(e))

def test_dashboard_city(cidade_id: Optional[int] = None):
    """Test GET /dashboard/cidade/<id>"""
    if not cidade_id:
        runner.log_skip("Dashboard City Page", "No valid city ID")
        return
    
    runner.log_info(f"Testing GET /dashboard/cidade/{cidade_id}")
    try:
        response = requests.get(f"{DASHBOARD_BASE}/cidade/{cidade_id}")
        if response.status_code == 200:
            if "chart-temperatura" in response.text and "chart-risco" in response.text:
                runner.log_pass("Dashboard City Page", "Page loads with chart containers")
            else:
                runner.log_fail("Dashboard City Page", "Expected chart containers not found")
        else:
            runner.log_fail("Dashboard City Page", f"HTTP {response.status_code}")
    except Exception as e:
        runner.log_fail("Dashboard City Page", str(e))

def test_htmx_partial(cidade_id: Optional[int] = None):
    """Test HTMX partial loading"""
    if not cidade_id:
        runner.log_skip("HTMX Partial Load", "No valid city ID")
        return
    
    runner.log_info("Testing HTMX partial load (HX-Request header)")
    try:
        headers = {"HX-Request": "true"}
        response = requests.get(f"{DASHBOARD_BASE}/cidade/{cidade_id}?range=7", headers=headers)
        if response.status_code == 200:
            # Should return partial HTML (city_charts.html)
            if "chart-temperatura" in response.text and "<html" not in response.text:
                runner.log_pass("HTMX Partial", "Returns partial HTML without base layout")
            else:
                runner.log_fail("HTMX Partial", "Response may include full page")
        else:
            runner.log_fail("HTMX Partial", f"HTTP {response.status_code}")
    except Exception as e:
        runner.log_fail("HTMX Partial", str(e))

def test_error_handling():
    """Test error handling"""
    runner.log_info("Testing error handling")
    try:
        # Test invalid city ID
        response = requests.get(f"{DASHBOARD_BASE}/cidade/99999")
        if response.status_code == 404:
            runner.log_pass("Error Handling - Invalid City", "Returns 404")
        else:
            runner.log_pass("Error Handling - Invalid City", f"Returns {response.status_code}")
        
        # Test invalid endpoint
        response = requests.get(f"{API_BASE}/gold/invalid")
        if response.status_code == 404:
            runner.log_pass("Error Handling - Invalid Endpoint", "Returns 404")
        else:
            runner.log_pass("Error Handling - Invalid Endpoint", f"Returns {response.status_code}")
    except Exception as e:
        runner.log_fail("Error Handling", str(e))

# ============================================================================
# MAIN
# ============================================================================

def main():
    print(f"\n{BLUE}{'='*60}")
    print("ETAPA 4 Dashboard Testing Suite")
    print(f"{'='*60}{RESET}\n")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        runner.log_info(f"Server running at {BASE_URL}")
    except requests.exceptions.ConnectionError:
        print(f"{RED}✗ Cannot connect to {BASE_URL}{RESET}")
        print(f"  Please start the server: docker-compose up")
        sys.exit(1)
    
    # Run tests
    print("\n--- Dashboard Pages ---")
    test_dashboard_index()
    
    print("\n--- API Endpoints ---")
    cidade_id = test_api_cidades()
    if cidade_id:
        test_api_resumo(cidade_id)
        test_api_diario(cidade_id)
        test_api_serie(cidade_id)
    
    print("\n--- Dashboard City Page ---")
    test_dashboard_city(cidade_id)
    
    print("\n--- HTMX Integration ---")
    test_htmx_partial(cidade_id)
    
    print("\n--- Error Handling ---")
    test_error_handling()
    
    # Summary
    success = runner.summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
