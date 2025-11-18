"""
Simple test script for custom chart API (no pytest required)
"""
import sys
import pandas as pd
from io import BytesIO, StringIO
sys.path.append('backend')

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def create_test_csv():
    """Create a test CSV file in memory"""
    df = pd.DataFrame({
        'numeric1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'numeric2': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        'category': ['A', 'B', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B'],
        'text_col': ['hello', 'world', 'test', 'data', 'analysis',
                     'chart', 'graph', 'plot', 'visual', 'insight']
    })

    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer


def test_upload_and_analyze():
    """Test file upload and analysis"""
    print("\n" + "=" * 60)
    print("TEST 1: Upload and Analyze CSV")
    print("=" * 60)

    csv_buffer = create_test_csv()

    response = client.post(
        "/analyze",
        files={"file": ("test_data.csv", csv_buffer, "text/csv")}
    )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()

    assert 'cache_key' in data, "Missing cache_key in response"
    assert 'analysis' in data, "Missing analysis in response"

    print(f"✓ File uploaded successfully")
    print(f"✓ Cache key: {data['cache_key']}")
    print(f"✓ Columns analyzed: {len(data['analysis']['columns'])}")

    return data['cache_key']


def test_scatter_plot(cache_key):
    """Test scatter plot generation"""
    print("\n" + "=" * 60)
    print("TEST 2: Scatter Plot")
    print("=" * 60)

    payload = {
        "cache_key": cache_key,
        "chart_type": "scatter",
        "x_column": "numeric1",
        "y_column": "numeric2",
        "color_scheme": "viridis"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data['status'] == 'success', "Chart generation failed"
    assert 'chart' in data, "Missing chart in response"

    print("✓ Scatter plot generated successfully")


def test_line_chart(cache_key):
    """Test line chart generation (with y_columns as array)"""
    print("\n" + "=" * 60)
    print("TEST 3: Line Chart (with y_columns array)")
    print("=" * 60)

    payload = {
        "cache_key": cache_key,
        "chart_type": "line",
        "x_column": "numeric1",
        "y_columns": ["numeric2"],  # Must be an array
        "color_scheme": "plasma"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    data = response.json()
    assert data['status'] == 'success', "Chart generation failed"

    print("✓ Line chart generated successfully")
    print("✓ y_columns sent as array correctly")


def test_box_plot(cache_key):
    """Test box plot generation"""
    print("\n" + "=" * 60)
    print("TEST 4: Box Plot")
    print("=" * 60)

    payload = {
        "cache_key": cache_key,
        "chart_type": "box",
        "columns": ["numeric1", "numeric2"],
        "color_scheme": "blues"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    print("✓ Box plot generated successfully")


def test_pie_chart(cache_key):
    """Test pie chart generation"""
    print("\n" + "=" * 60)
    print("TEST 5: Pie Chart")
    print("=" * 60)

    payload = {
        "cache_key": cache_key,
        "chart_type": "pie",
        "x_column": "category",
        "top_n": 5,
        "color_scheme": "sunset"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    print("✓ Pie chart generated successfully")


def test_bar_chart(cache_key):
    """Test bar chart generation"""
    print("\n" + "=" * 60)
    print("TEST 6: Bar Chart")
    print("=" * 60)

    payload = {
        "cache_key": cache_key,
        "chart_type": "bar",
        "x_column": "category",
        "y_column": "numeric1",
        "color_scheme": "rainbow"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    print("✓ Bar chart generated successfully")


def test_correlation_heatmap(cache_key):
    """Test correlation heatmap"""
    print("\n" + "=" * 60)
    print("TEST 7: Correlation Heatmap")
    print("=" * 60)

    payload = {
        "cache_key": cache_key,
        "chart_type": "correlation",
        "color_scheme": "inferno"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    print("✓ Correlation heatmap generated successfully")


def test_error_handling():
    """Test error handling for bad requests"""
    print("\n" + "=" * 60)
    print("TEST 8: Error Handling")
    print("=" * 60)

    # Test with invalid cache key
    payload = {
        "cache_key": "nonexistent_key",
        "chart_type": "scatter",
        "x_column": "col1",
        "y_column": "col2"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 404, "Should return 404 for invalid cache key"
    print("✓ Returns 404 for invalid cache key")

    # Test with missing required fields
    cache_key = test_upload_and_analyze()
    payload = {
        "cache_key": cache_key,
        "chart_type": "scatter",
        # Missing x_column and y_column
        "color_scheme": "viridis"
    }

    response = client.post("/custom_chart", json=payload)
    assert response.status_code == 400, "Should return 400 for missing required fields"
    print("✓ Returns 400 for missing required fields")


def test_all_color_schemes(cache_key):
    """Test all color schemes work"""
    print("\n" + "=" * 60)
    print("TEST 9: All Color Schemes")
    print("=" * 60)

    schemes = ['viridis', 'plasma', 'inferno', 'blues', 'purples',
               'ocean', 'sunset', 'rainbow', 'pastel', 'bold']

    for scheme in schemes:
        payload = {
            "cache_key": cache_key,
            "chart_type": "scatter",
            "x_column": "numeric1",
            "y_column": "numeric2",
            "color_scheme": scheme
        }

        response = client.post("/custom_chart", json=payload)
        assert response.status_code == 200, f"Failed for scheme: {scheme}"

    print(f"✓ All {len(schemes)} color schemes work correctly")


def test_column_info(cache_key):
    """Test column info endpoint"""
    print("\n" + "=" * 60)
    print("TEST 10: Column Info Endpoint")
    print("=" * 60)

    response = client.get(f"/column_info/{cache_key}")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    assert 'all_columns' in data
    assert 'numeric_columns' in data
    assert 'categorical_columns' in data

    print(f"✓ Numeric columns: {data['numeric_columns']}")
    print(f"✓ Categorical columns: {data['categorical_columns']}")


def main():
    """Run all tests"""
    print("\n" + "🧪" * 30)
    print("CUSTOM CHART API TEST SUITE")
    print("🧪" * 30)

    try:
        # Upload test data
        cache_key = test_upload_and_analyze()

        # Test all chart types
        test_scatter_plot(cache_key)
        test_line_chart(cache_key)
        test_box_plot(cache_key)
        test_pie_chart(cache_key)
        test_bar_chart(cache_key)
        test_correlation_heatmap(cache_key)

        # Test utilities
        test_column_info(cache_key)
        test_all_color_schemes(cache_key)

        # Test error handling
        test_error_handling()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe custom chart API is working correctly.")
        print("All chart types, color schemes, and error handling verified.\n")

        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
