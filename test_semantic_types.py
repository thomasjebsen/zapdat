"""
Unit tests for semantic type detection
"""

import sys

import pandas as pd

sys.path.append("backend")
from analyzer import TableAnalyzer


def test_semantic_type_detection():
    """Test semantic type detection with comprehensive test data"""

    print("=" * 80)
    print("TESTING SEMANTIC TYPE DETECTION")
    print("=" * 80)

    # Load semantic test data
    df = pd.read_csv("semantic_test_data.csv")
    print(f"\n✓ Loaded semantic test CSV with {len(df)} rows and {len(df.columns)} columns")

    # Initialize analyzer
    analyzer = TableAnalyzer(df)

    # Expected semantic types for each column
    expected_types = {
        "email": "email",
        "url": "url",
        "phone": "phone",
        "currency": "currency",
        "percentage": "percentage",
        "uuid": "uuid",
        "ipv4": "ipv4",
        "postal_code_us": "postal_code_us",
        "credit_card": "credit_card",
        "boolean_text": "boolean_text",
        "iso_date": "iso_date",  # Should be detected and converted to datetime
        "us_date": "us_date",  # Should be detected and converted to datetime
        "category": None,  # Regular categorical, no semantic type
        "amount": None,  # Regular numeric, no semantic type
        "age": None,  # Regular numeric, no semantic type
    }

    print(f"\n{'COLUMN TYPE DETECTION RESULTS':^80}")
    print("-" * 80)
    print(f"{'Column':<20} {'Expected':<20} {'Detected':<20} {'Confidence':<12} {'Status':<8}")
    print("-" * 80)

    passed = 0
    failed = 0

    for col, expected_semantic in expected_types.items():
        col_info = analyzer.column_types[col]
        detected_type = col_info["type"]
        detected_semantic = col_info.get("semantic_type")
        confidence = col_info.get("confidence", 1.0)

        # For datetime columns that were parsed from strings
        if expected_semantic in ["iso_date", "us_date"]:
            if detected_type == "datetime" and detected_semantic == expected_semantic:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1
        # For other semantic types
        elif expected_semantic is not None:
            if detected_semantic == expected_semantic:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1
        # For regular columns without semantic types
        else:
            if detected_semantic is None or detected_semantic == expected_semantic:
                status = "✓ PASS"
                passed += 1
            else:
                status = "✗ FAIL"
                failed += 1

        expected_str = expected_semantic if expected_semantic else f"({detected_type})"
        detected_str = detected_semantic if detected_semantic else f"({detected_type})"

        print(
            f"{col:<20} {expected_str:<20} {detected_str:<20} {confidence:<12.1%} {status:<8}"
        )

    print("-" * 80)
    print(f"\nTest Results: {passed} passed, {failed} failed")

    # Test edge cases
    print(f"\n{'EDGE CASE TESTS':^80}")
    print("-" * 80)

    edge_cases = [
        {
            "name": "Mixed email and text",
            "data": [
                "john@example.com",
                "jane@test.org",
                "not an email",
                "also not email",
                "still not email",
                "bob@company.net",
            ],  # 2/6 = 33% emails
            "expected_semantic": None,  # Should not detect as email (only 33% match)
        },
        {
            "name": "All emails",
            "data": [
                "john@example.com",
                "jane@test.org",
                "bob@company.net",
                "alice@domain.io",
            ],
            "expected_semantic": "email",
        },
        {
            "name": "Boolean variations",
            "data": ["yes", "no", "yes", "yes", "no", "yes"],
            "expected_semantic": "boolean_text",
        },
        {
            "name": "Low cardinality categorical",
            "data": ["Red", "Blue", "Green", "Red", "Blue", "Red", "Green", "Blue"] * 10,
            "expected_type": "categorical",
        },
        {
            "name": "High cardinality text",
            "data": [f"unique_text_{i}" for i in range(100)],
            "expected_type": "text",
        },
    ]

    edge_passed = 0
    edge_failed = 0

    for test_case in edge_cases:
        test_df = pd.DataFrame({"test_col": test_case["data"]})
        test_analyzer = TableAnalyzer(test_df)
        result = test_analyzer.column_types["test_col"]

        detected_type = result["type"]
        detected_semantic = result.get("semantic_type")
        confidence = result.get("confidence", 1.0)

        # Check semantic type if expected
        if "expected_semantic" in test_case:
            expected = test_case["expected_semantic"]
            if detected_semantic == expected:
                status = "✓ PASS"
                edge_passed += 1
            else:
                status = "✗ FAIL"
                edge_failed += 1
            expected_str = expected if expected else "(none)"
            detected_str = detected_semantic if detected_semantic else "(none)"
        # Check base type if expected
        else:
            expected = test_case["expected_type"]
            if detected_type == expected:
                status = "✓ PASS"
                edge_passed += 1
            else:
                status = "✗ FAIL"
                edge_failed += 1
            expected_str = expected
            detected_str = detected_type

        print(f"{test_case['name']:<30} Expected: {expected_str:<15} Got: {detected_str:<15} {status}")

    print("-" * 80)
    print(f"\nEdge Case Results: {edge_passed} passed, {edge_failed} failed")

    # Overall summary
    print("\n" + "=" * 80)
    total_passed = passed + edge_passed
    total_failed = failed + edge_failed
    if total_failed == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  SOME TESTS FAILED: {total_passed} passed, {total_failed} failed")
    print("=" * 80)

    return total_failed == 0


if __name__ == "__main__":
    success = test_semantic_type_detection()
    sys.exit(0 if success else 1)
