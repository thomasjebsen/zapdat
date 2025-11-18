"""
Enhanced test script for the analyzer with visualization output
"""
import pandas as pd
import sys
import json
sys.path.append('backend')
from analyzer import TableAnalyzer

def test_analyzer():
    """Test the analyzer with sample data and generate visualizations"""

    # Load sample data
    print("=" * 60)
    print("TESTING TABLE EDA ANALYZER")
    print("=" * 60)

    df = pd.read_csv('sample_data.csv')
    print(f"\n✓ Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
    print(f"✓ Columns: {', '.join(df.columns)}")

    # Initialize analyzer
    analyzer = TableAnalyzer(df)

    # Print detected types
    print(f"\n{'DETECTED COLUMN TYPES':^60}")
    print("-" * 60)
    for col, col_type in analyzer.column_types.items():
        emoji = {'numeric': '🔢', 'categorical': '🏷️', 'text': '📝', 'datetime': '📅', 'id': '🔑'}
        print(f"{emoji.get(col_type, '📊')} {col:<20} → {col_type}")

    # Get overview
    overview = analyzer.get_overview()
    print(f"\n{'DATASET OVERVIEW':^60}")
    print("-" * 60)
    print(f"📊 Rows:       {overview['rows']:>10,}")
    print(f"📊 Columns:    {overview['columns']:>10}")
    print(f"📊 Duplicates: {overview['duplicates']:>10}")

    total_missing = sum(overview['missing_values'].values())
    print(f"📊 Missing:    {total_missing:>10}")

    # Test numeric analysis
    print(f"\n{'NUMERIC ANALYSIS: age':^60}")
    print("-" * 60)
    age_analysis = analyzer.analyze_numeric('age')
    for key, value in age_analysis['stats'].items():
        if value is None:
            print(f"{key:<15} → N/A")
        elif isinstance(value, int):
            print(f"{key:<15} → {value:>10,}")
        elif isinstance(value, float):
            print(f"{key:<15} → {value:>10.2f}")
        else:
            print(f"{key:<15} → {value}")

    # Test categorical analysis
    print(f"\n{'CATEGORICAL ANALYSIS: department':^60}")
    print("-" * 60)
    dept_analysis = analyzer.analyze_categorical('department')
    for key, value in dept_analysis['stats'].items():
        if value is None:
            print(f"{key:<15} → N/A")
        elif isinstance(value, int):
            print(f"{key:<15} → {value:>10,}")
        else:
            print(f"{key:<15} → {value}")

    # Test full analysis
    print(f"\n{'RUNNING FULL ANALYSIS':^60}")
    print("-" * 60)
    full_analysis = analyzer.analyze_all()

    # Count visualizations
    viz_count = sum(1 for col_data in full_analysis['columns'].values()
                    if col_data.get('analysis', {}).get('plot'))

    print(f"✓ Analyzed {len(full_analysis['columns'])} columns")
    print(f"✓ Generated {viz_count} visualizations")

    # Generate HTML report
    print(f"\n{'GENERATING HTML REPORT':^60}")
    print("-" * 60)

    html_content = generate_html_report(full_analysis)

    with open('test_report.html', 'w') as f:
        f.write(html_content)

    print(f"✓ Report saved to: test_report.html")

    # Verify JSON serialization
    print(f"\n{'TESTING JSON SERIALIZATION':^60}")
    print("-" * 60)
    try:
        json_str = json.dumps(full_analysis)
        print(f"✓ Successfully serialized {len(json_str):,} bytes")
    except Exception as e:
        print(f"✗ JSON serialization failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nOpen test_report.html in your browser to see the visualizations!")

    return True


def generate_html_report(analysis):
    """Generate a standalone HTML report"""

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Analyzer Test Report</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            background: #f5f5f5;
        }
        h1 { color: #333; }
        .overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value { font-size: 2rem; font-weight: bold; }
        .stat-label { font-size: 0.9rem; opacity: 0.9; }
        .column-card {
            background: white;
            padding: 2rem;
            margin: 1rem 0;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .column-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        .column-type {
            background: #667eea;
            color: white;
            padding: 0.25rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 1rem 0;
        }
        .stat-item {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 6px;
        }
        .stat-item-label {
            font-size: 0.8rem;
            color: #666;
            text-transform: uppercase;
        }
        .stat-item-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <h1>📊 Table EDA Analyzer - Test Report</h1>

    <div class="overview">
"""

    overview = analysis['overview']
    total_missing = sum(overview['missing_values'].values())

    html += f"""
        <div class="stat-box">
            <div class="stat-value">{overview['rows']:,}</div>
            <div class="stat-label">Rows</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{overview['columns']}</div>
            <div class="stat-label">Columns</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{total_missing:,}</div>
            <div class="stat-label">Missing Values</div>
        </div>
        <div class="stat-box">
            <div class="stat-value">{overview['duplicates']:,}</div>
            <div class="stat-label">Duplicates</div>
        </div>
    </div>
"""

    # Add column cards
    for col_name, col_data in analysis['columns'].items():
        type_emoji = {'numeric': '🔢', 'categorical': '🏷️', 'text': '📝', 'datetime': '📅', 'id': '🔑'}
        emoji = type_emoji.get(col_data['type'], '📊')

        html += f"""
    <div class="column-card">
        <div class="column-header">
            <h2>{emoji} {col_name}</h2>
            <span class="column-type">{col_data['type']}</span>
        </div>
"""

        # Add stats
        if 'stats' in col_data.get('analysis', {}):
            html += '<div class="stats-grid">'
            for key, value in col_data['analysis']['stats'].items():
                if value is None:
                    display_value = 'N/A'
                elif isinstance(value, (int, float)):
                    if isinstance(value, int):
                        display_value = f"{value:,}"
                    else:
                        display_value = f"{value:.2f}"
                else:
                    display_value = str(value)

                html += f"""
                <div class="stat-item">
                    <div class="stat-item-label">{key}</div>
                    <div class="stat-item-value">{display_value}</div>
                </div>
"""
            html += '</div>'

        # Add plot
        if 'plot' in col_data.get('analysis', {}):
            plot_id = f"plot-{col_name.replace(' ', '-')}"
            html += f'<div id="{plot_id}"></div>'
            html += f"""
    <script>
        var plotData = {col_data['analysis']['plot']};
        Plotly.newPlot('{plot_id}', plotData.data, plotData.layout, {{responsive: true}});
    </script>
"""

        html += '</div>'

    html += """
</body>
</html>
"""

    return html


if __name__ == '__main__':
    success = test_analyzer()
    sys.exit(0 if success else 1)
