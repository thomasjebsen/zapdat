"""
Test script to verify ID column analysis output
"""
import pandas as pd
import sys
sys.path.append('backend')
from analyzer import TableAnalyzer

def test_id_analysis():
    """Test the detailed analysis output for ID columns"""

    print("=" * 60)
    print("TESTING ID COLUMN ANALYSIS")
    print("=" * 60)

    # Load test data with ID columns
    df = pd.read_csv('test_id_columns.csv')
    print(f"\n✓ Loaded CSV with {len(df)} rows and {len(df.columns)} columns")

    # Initialize analyzer
    analyzer = TableAnalyzer(df)

    # Analyze the 'id' column
    print(f"\n{'ANALYSIS: id column':^60}")
    print("-" * 60)
    id_analysis = analyzer.analyze_id('id')

    for key, value in id_analysis['stats'].items():
        if value is None:
            print(f"{key:<25} → N/A")
        elif isinstance(value, bool):
            print(f"{key:<25} → {value}")
        elif isinstance(value, int):
            print(f"{key:<25} → {value:,}")
        elif isinstance(value, float):
            print(f"{key:<25} → {value:.2f}%")
        else:
            print(f"{key:<25} → {value}")

    print(f"\n{'Sample values:':<25} {', '.join(map(str, id_analysis['samples']))}")

    # Analyze the 'user_id' column
    print(f"\n{'ANALYSIS: user_id column':^60}")
    print("-" * 60)
    user_id_analysis = analyzer.analyze_id('user_id')

    for key, value in user_id_analysis['stats'].items():
        if value is None:
            print(f"{key:<25} → N/A")
        elif isinstance(value, bool):
            print(f"{key:<25} → {value}")
        elif isinstance(value, int):
            print(f"{key:<25} → {value:,}")
        elif isinstance(value, float):
            print(f"{key:<25} → {value:.2f}%")
        else:
            print(f"{key:<25} → {value}")

    print(f"\n{'Sample values:':<25} {', '.join(map(str, user_id_analysis['samples']))}")

    # Analyze the 'ID_CODE' column (text-based ID)
    print(f"\n{'ANALYSIS: ID_CODE column (text-based)':^60}")
    print("-" * 60)
    code_analysis = analyzer.analyze_id('ID_CODE')

    for key, value in code_analysis['stats'].items():
        if value is None:
            print(f"{key:<25} → N/A")
        elif isinstance(value, bool):
            print(f"{key:<25} → {value}")
        elif isinstance(value, int):
            print(f"{key:<25} → {value:,}")
        elif isinstance(value, float):
            print(f"{key:<25} → {value:.2f}%")
        else:
            print(f"{key:<25} → {value}")

    print(f"\n{'Sample values:':<25} {', '.join(map(str, code_analysis['samples']))}")

    # Test full analysis
    print(f"\n{'RUNNING FULL ANALYSIS':^60}")
    print("-" * 60)
    full_analysis = analyzer.analyze_all()

    # Verify ID columns are properly analyzed
    id_cols = [col for col, col_type in analyzer.column_types.items() if col_type == 'id']
    print(f"✓ Found {len(id_cols)} ID columns: {', '.join(id_cols)}")

    for col in id_cols:
        col_analysis = full_analysis['columns'][col]
        assert col_analysis['type'] == 'id', f"Column {col} should be type 'id'"
        assert 'stats' in col_analysis['analysis'], f"Column {col} should have stats"
        stats = col_analysis['analysis']['stats']
        assert 'is_unique' in stats, f"Column {col} should have 'is_unique' stat"
        assert 'format_type' in stats, f"Column {col} should have 'format_type' stat"
        assert 'potential_primary_key' in stats, f"Column {col} should have 'potential_primary_key' stat"
        print(f"  ✓ {col}: {stats['format_type']}, unique={stats['is_unique']}, pk={stats['potential_primary_key']}")

    print("\n" + "=" * 60)
    print("✅ ALL ID ANALYSIS TESTS PASSED!")
    print("=" * 60)

    return True

if __name__ == '__main__':
    success = test_id_analysis()
    sys.exit(0 if success else 1)
