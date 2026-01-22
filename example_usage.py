#!/usr/bin/env python3
"""
Example script demonstrating programmatic usage of the GNSS Analyzer.
"""

from gnss_analyzer.parsers import GNSSLogParser
from gnss_analyzer.analyzers import PositionAnalyzer, AIAnalyzer


def main():
    print("GNSS Analyzer - Programmatic Usage Example\n")

    # Step 1: Parse a GNSS log file
    print("1. Parsing GNSS log file...")
    parser = GNSSLogParser()
    points = parser.parse_file('sample_data/gnss_log_with_issues.txt')
    print(f"   Parsed {len(points)} GNSS points\n")

    # Step 2: Get statistics
    stats = parser.get_statistics()
    print("2. Log Statistics:")
    print(f"   Duration: {stats['time_span']:.1f} seconds")
    print(f"   Average satellites: {stats['avg_satellites']:.1f}")
    print(f"   Average HDOP: {stats['avg_hdop']:.2f}\n")

    # Step 3: Detect anomalies
    print("3. Detecting anomalies...")
    analyzer = PositionAnalyzer(
        max_speed_mps=30.0,  # 108 km/h
        max_acceleration=10.0
    )

    anomalies = analyzer.analyze_all(points)
    print(f"   Found {len(anomalies)} anomalies:\n")

    for i, anomaly in enumerate(anomalies, 1):
        print(f"   Anomaly {i}:")
        print(f"     Type: {anomaly.anomaly_type}")
        print(f"     Severity: {anomaly.severity}")
        print(f"     {anomaly.description}")
        print()

    # Step 4: AI Analysis (optional - requires API key)
    print("4. AI-Powered Root Cause Analysis:")
    ai_analyzer = AIAnalyzer(model='gpt-3.5-turbo')

    if ai_analyzer.client:
        print("   Running AI analysis...\n")

        # Analyze patterns
        pattern_analysis = ai_analyzer.analyze_multiple_anomalies(anomalies)

        print("   Patterns detected:")
        for pattern in pattern_analysis.get('patterns', []):
            print(f"     • {pattern}")

        print(f"\n   Primary root cause:")
        print(f"     {pattern_analysis.get('primary_root_cause', 'Unknown')}")

        # Detailed analysis of first anomaly
        if anomalies:
            print(f"\n   Detailed analysis of first anomaly:")
            detailed = ai_analyzer.analyze_anomaly(anomalies[0])

            print(f"   Root causes:")
            for cause in detailed.get('root_causes', []):
                print(f"     • {cause['cause']} ({cause['confidence']}% confidence)")

    else:
        print("   ⚠ OpenAI API key not found - skipping AI analysis")
        print("   Set OPENAI_API_KEY environment variable to enable AI features")
        print("\n   Fallback analysis:")

        # Use rule-based analysis
        for i, anomaly in enumerate(anomalies[:2], 1):  # Analyze first 2
            analysis = ai_analyzer.analyze_anomaly(anomaly)
            print(f"\n   Anomaly {i} Analysis:")
            print(f"     Root causes:")
            for cause in analysis.get('root_causes', []):
                print(f"       • {cause['cause']} ({cause['confidence']}% confidence)")

    print("\n✓ Analysis complete!")


if __name__ == '__main__':
    main()
