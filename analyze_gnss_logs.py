#!/usr/bin/env python3
"""
Main script to analyze GNSS logs for anomalies and root causes.

Usage:
    python analyze_gnss_logs.py <log_file> [--ai] [--model gpt-4]
"""

import argparse
import sys
import json
from pathlib import Path
from gnss_analyzer.parsers import GNSSLogParser
from gnss_analyzer.analyzers import PositionAnalyzer, AIAnalyzer


def print_separator(char="=", length=80):
    """Print a separator line."""
    print(char * length)


def analyze_log_file(filepath: str, use_ai: bool = False, model: str = "gpt-3.5-turbo"):
    """Analyze a GNSS log file for anomalies."""

    print_separator()
    print(f"GNSS Log Analyzer - Analyzing: {filepath}")
    print_separator()

    # Parse the log file
    print("\n[1/4] Parsing GNSS log file...")
    parser = GNSSLogParser()

    try:
        points = parser.parse_file(filepath)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        return 1
    except Exception as e:
        print(f"Error parsing file: {e}")
        return 1

    if not points:
        print("Error: No valid GNSS points found in file")
        return 1

    print(f"  ✓ Parsed {len(points)} GNSS points")

    # Get statistics
    stats = parser.get_statistics()
    print(f"\n  Statistics:")
    print(f"    Time span: {stats['time_span']:.1f} seconds")
    print(f"    Avg satellites: {stats['avg_satellites']:.1f}")
    print(f"    Avg HDOP: {stats['avg_hdop']:.2f}")
    print(f"    Quality distribution:")
    print(f"      No fix: {stats['quality_distribution']['no_fix']}")
    print(f"      GPS fix: {stats['quality_distribution']['gps_fix']}")
    print(f"      DGPS fix: {stats['quality_distribution']['dgps_fix']}")

    # Analyze for anomalies
    print("\n[2/4] Detecting position anomalies...")
    position_analyzer = PositionAnalyzer(max_speed_mps=30.0)  # 30 m/s = 108 km/h

    anomalies = position_analyzer.analyze_all(points)

    print(f"  ✓ Found {len(anomalies)} anomalies")

    if not anomalies:
        print("\n✓ No anomalies detected! GNSS log looks clean.")
        return 0

    # Display anomalies
    print(f"\n[3/4] Anomaly Details:")
    print_separator("-")

    for i, anomaly in enumerate(anomalies, 1):
        print(f"\nAnomaly #{i} [{anomaly.severity}]")
        print(f"  Type: {anomaly.anomaly_type}")
        print(f"  Time: {anomaly.point.timestamp}")
        print(f"  {anomaly.description}")
        print(f"  Position: ({anomaly.point.latitude:.6f}, {anomaly.point.longitude:.6f})")
        print(f"  Satellites: {anomaly.point.satellites}, HDOP: {anomaly.point.hdop:.1f}")

        if anomaly.distance_jump > 0:
            print(f"  Distance jump: {anomaly.distance_jump:.1f}m")

        print_separator("-")

    # AI Analysis
    print(f"\n[4/4] Root Cause Analysis...")

    if use_ai:
        print("  Using AI-powered analysis...")
        ai_analyzer = AIAnalyzer(model=model)

        if not ai_analyzer.client:
            print("  ⚠ Warning: OpenAI API key not found. Using rule-based analysis.")
            print("  Set OPENAI_API_KEY environment variable to enable AI analysis.")

        # Analyze patterns across all anomalies
        pattern_analysis = ai_analyzer.analyze_multiple_anomalies(anomalies)

        print_separator()
        print("\n  PATTERN ANALYSIS:")
        print_separator("-")
        print(f"  Model: {pattern_analysis.get('ai_model', 'unknown')}")
        print(f"\n  Patterns Detected:")
        for pattern in pattern_analysis.get('patterns', []):
            print(f"    • {pattern}")

        print(f"\n  Primary Root Cause:")
        print(f"    {pattern_analysis.get('primary_root_cause', 'Unknown')}")

        if pattern_analysis.get('systemic_issues'):
            print(f"\n  Systemic Issues:")
            for issue in pattern_analysis['systemic_issues']:
                print(f"    • {issue.get('issue')} [{issue.get('severity')}]")
                print(f"      Affects anomalies: {issue.get('affected_anomalies', [])}")

        print(f"\n  Priority Actions:")
        for action in pattern_analysis.get('priority_actions', []):
            print(f"    1. {action}")

        print(f"\n  Overall Assessment:")
        print(f"    {pattern_analysis.get('overall_assessment', 'N/A')}")

        # Detailed analysis of first few critical anomalies
        critical_anomalies = [a for a in anomalies if a.severity == "CRITICAL"][:3]

        if critical_anomalies:
            print_separator()
            print("\n  DETAILED ANALYSIS OF CRITICAL ANOMALIES:")
            print_separator("-")

            for i, anomaly in enumerate(critical_anomalies, 1):
                print(f"\n  Critical Anomaly #{i}:")
                analysis = ai_analyzer.analyze_anomaly(anomaly)

                print(f"\n    Root Causes:")
                for cause in analysis.get('root_causes', []):
                    print(f"      • {cause['cause']} (confidence: {cause['confidence']}%)")
                    for evidence in cause.get('evidence', []):
                        print(f"        - {evidence}")

                print(f"\n    Recommendations:")
                for rec in analysis.get('recommendations', []):
                    print(f"      • {rec}")

    else:
        print("  Using rule-based analysis (use --ai for AI-powered analysis)")

        # Basic categorization
        by_type = {}
        by_severity = {}

        for anomaly in anomalies:
            by_type[anomaly.anomaly_type] = by_type.get(anomaly.anomaly_type, 0) + 1
            by_severity[anomaly.severity] = by_severity.get(anomaly.severity, 0) + 1

        print_separator("-")
        print(f"\n  Summary:")
        print(f"    By Type:")
        for atype, count in by_type.items():
            print(f"      {atype}: {count}")

        print(f"\n    By Severity:")
        for severity, count in by_severity.items():
            print(f"      {severity}: {count}")

        print(f"\n  Recommendations:")
        print(f"    • Use --ai flag for detailed AI-powered root cause analysis")
        print(f"    • Review satellite visibility and signal quality")
        print(f"    • Check for environmental obstructions")
        print(f"    • Verify GNSS receiver configuration")

    print_separator()
    print(f"\n✓ Analysis complete!")
    print(f"  Total anomalies: {len(anomalies)}")
    print(f"  Critical: {sum(1 for a in anomalies if a.severity == 'CRITICAL')}")
    print(f"  High: {sum(1 for a in anomalies if a.severity == 'HIGH')}")
    print(f"  Medium: {sum(1 for a in anomalies if a.severity == 'MEDIUM')}")
    print_separator()

    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze GNSS logs for position anomalies and root causes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python analyze_gnss_logs.py sample_data/gnss_log.txt

  # AI-powered analysis with GPT-3.5
  python analyze_gnss_logs.py sample_data/gnss_log.txt --ai

  # AI-powered analysis with GPT-4
  python analyze_gnss_logs.py sample_data/gnss_log.txt --ai --model gpt-4

Environment:
  OPENAI_API_KEY: Required for AI-powered analysis
        """
    )

    parser.add_argument('log_file', help='Path to GNSS log file')
    parser.add_argument('--ai', action='store_true',
                       help='Enable AI-powered root cause analysis')
    parser.add_argument('--model', default='gpt-3.5-turbo',
                       choices=['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo'],
                       help='AI model to use (default: gpt-3.5-turbo)')

    args = parser.parse_args()

    return analyze_log_file(args.log_file, args.ai, args.model)


if __name__ == '__main__':
    sys.exit(main())
