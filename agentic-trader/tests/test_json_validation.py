#!/usr/bin/env python3
"""
Test script to demonstrate JSON validation techniques.
"""

import json
from utility import (
    validate_json_string,
    validate_json_file,
    safe_json_load,
    safe_json_dump,
    validate_json_structure
)


def test_json_validation():
    """Demonstrate various JSON validation techniques."""

    print("=== JSON Validation Examples ===\n")

    # 1. Test valid JSON string
    valid_json = '{"name": "AAPL", "price": 150.50, "volume": 1000}'
    is_valid, error = validate_json_string(valid_json)
    print(f"1. Valid JSON string: {is_valid}")
    if not is_valid:
        print(f"   Error: {error}")

    # 2. Test invalid JSON string
    # Missing closing brace
    invalid_json = '{"name": "AAPL", "price": 150.50, "volume": 1000'
    is_valid, error = validate_json_string(invalid_json)
    print(f"2. Invalid JSON string: {is_valid}")
    if not is_valid:
        print(f"   Error: {error}")

    # 3. Test structure validation
    trade_data = {
        "timestamp": "2024-01-01T10:00:00",
        "symbol": "AAPL",
        "decision": "BUY",
        "price": 150.50
    }

    required_keys = ["timestamp", "symbol", "decision"]
    optional_keys = ["price", "volume"]

    is_valid, error = validate_json_structure(
        trade_data, required_keys, optional_keys)
    print(f"3. Structure validation: {is_valid}")
    if not is_valid:
        print(f"   Error: {error}")

    # 4. Test missing required keys
    incomplete_data = {
        "timestamp": "2024-01-01T10:00:00",
        "symbol": "AAPL"
        # Missing "decision" key
    }

    is_valid, error = validate_json_structure(
        incomplete_data, required_keys, optional_keys)
    print(f"4. Incomplete data validation: {is_valid}")
    if not is_valid:
        print(f"   Error: {error}")

    # 5. Test safe JSON operations
    test_data = {
        "strategy": "BollingerBands",
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "performance": 0.15
    }

    # Safe save
    success = safe_json_dump(test_data, "test_output.json", indent=2)
    print(f"5. Safe JSON save: {success}")

    # Safe load
    loaded_data = safe_json_load("test_output.json", default={})
    print(f"6. Safe JSON load: {len(loaded_data)} keys loaded")

    # 7. Test with numpy types (like in your trading app)
    import numpy as np
    from datetime import datetime

    trading_data = {
        "timestamp": datetime.now(),
        "symbol": "AAPL",
        "price": np.float64(150.50),
        "volume": np.int64(1000),
        "returns": np.array([0.01, 0.02, -0.01])
    }

    # This would fail with regular json.dump, but works with your NpEncoder
    from analyze_log import NpEncoder
    try:
        json_str = json.dumps(trading_data, cls=NpEncoder)
        print(f"7. Numpy types JSON serialization: Success")
    except Exception as e:
        print(f"7. Numpy types JSON serialization: Failed - {e}")


def test_jsonl_validation():
    """Test JSONL (JSON Lines) validation."""

    print("\n=== JSONL Validation Examples ===\n")

    # Create a test JSONL file
    test_lines = [
        '{"timestamp": "2024-01-01T10:00:00", "symbol": "AAPL", "decision": "BUY"}',
        '{"timestamp": "2024-01-01T10:01:00", "symbol": "GOOGL", "decision": "SELL"}',
        '{"timestamp": "2024-01-01T10:02:00", "symbol": "MSFT", "decision": "HOLD"}',
        'invalid json line',  # This should be skipped
        '{"timestamp": "2024-01-01T10:03:00", "symbol": "TSLA", "decision": "BUY"}'
    ]

    with open("test_decisions.jsonl", "w") as f:
        for line in test_lines:
            f.write(line + "\n")

    # Validate JSONL file
    valid_decisions = []
    with open("test_decisions.jsonl", "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            is_valid, error = validate_json_string(line)
            if is_valid:
                decision = json.loads(line)
                valid_decisions.append(decision)
                print(
                    f"Line {line_num}: Valid decision for {decision['symbol']}")
            else:
                print(f"Line {line_num}: Invalid JSON - {error}")

    print(f"\nTotal valid decisions: {len(valid_decisions)}")


if __name__ == "__main__":
    test_json_validation()
    test_jsonl_validation()
