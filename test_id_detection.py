"""
Test script to verify ID column detection
"""
import pandas as pd
import sys
sys.path.append('backend')
from analyzer import TableAnalyzer

def test_id_detection():
    """Test that columns with 'id' at start or end are treated as categorical"""

    print("=" * 60)
    print("TESTING ID COLUMN DETECTION")
    print("=" * 60)

    # Load test data with ID columns
    df = pd.read_csv('test_id_columns.csv')
    print(f"\n✓ Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
    print(f"✓ Columns: {', '.join(df.columns)}")

    # Check actual dtypes from pandas
    print(f"\n{'PANDAS DTYPES':^60}")
    print("-" * 60)
    for col in df.columns:
        print(f"{col:<20} → {df[col].dtype}")

    # Initialize analyzer
    analyzer = TableAnalyzer(df)

    # Print detected types
    print(f"\n{'DETECTED COLUMN TYPES (by TableAnalyzer)':^60}")
    print("-" * 60)
    for col, col_type in analyzer.column_types.items():
        emoji = {'numeric': '🔢', 'categorical': '🏷️', 'text': '📝', 'datetime': '📅'}
        print(f"{emoji.get(col_type, '📊')} {col:<20} → {col_type}")

    # Verify expectations
    print(f"\n{'VERIFICATION':^60}")
    print("-" * 60)

    # Numeric ID columns should be detected as categorical (not numeric)
    expected_id_categorical = ['id', 'user_id', 'customer_id']
    expected_numeric = ['age', 'revenue']
    expected_text_or_categorical = ['name', 'ID_CODE']  # ID_CODE has text values, so text is fine

    all_passed = True

    # Check numeric ID columns are categorical (not numeric)
    for col in expected_id_categorical:
        if analyzer.column_types[col] == 'categorical':
            print(f"✓ '{col}' correctly detected as categorical (not numeric)")
        else:
            print(f"✗ '{col}' incorrectly detected as {analyzer.column_types[col]} (expected categorical)")
            all_passed = False

    # Check numeric columns are numeric
    for col in expected_numeric:
        if analyzer.column_types[col] == 'numeric':
            print(f"✓ '{col}' correctly detected as numeric")
        else:
            print(f"✗ '{col}' incorrectly detected as {analyzer.column_types[col]} (expected numeric)")
            all_passed = False

    # Check text/categorical columns (both are fine for these)
    for col in expected_text_or_categorical:
        if analyzer.column_types[col] in ['text', 'categorical']:
            print(f"✓ '{col}' correctly detected as {analyzer.column_types[col]}")
        else:
            print(f"✗ '{col}' incorrectly detected as {analyzer.column_types[col]}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 60)

    return all_passed

if __name__ == '__main__':
    success = test_id_detection()
    sys.exit(0 if success else 1)
