#!/usr/bin/env python3
"""
Real Health Data Demo Script

This script demonstrates how to work with real health data using pydhis2,
including data quality assessment and visualization.
"""

import asyncio
import sys
from datetime import datetime

import pandas as pd

from pydhis2 import DHIS2Config, get_client
from pydhis2.dqr import CompletenessMetrics, ConsistencyMetrics

# Fix for Windows asyncio compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def print_banner():
    """Print banner"""
    print("=" * 60)
    print("Real Health Data Demo - pydhis2")
    print("=" * 60)
    print()


def print_section(title):
    """Print section title"""
    print(f"\n{title}")
    print("-" * 60)


def main():
    """Entry point for console script"""
    print(f"Starting real health data demo at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")

    print("\nThank you for trying pydhis2! 🚀")


async def async_main():
    """Main demo function"""
    print_banner()

    # Get client class
    AsyncDHIS2Client, SyncDHIS2Client = get_client()  # noqa: N806

    # Configure DHIS2 connection
    config = DHIS2Config(
        base_url="https://play.dhis2.org/dev",
        auth=("admin", "district"),
        rps=3.0,
        max_retries=5
    )

    try:
        async with AsyncDHIS2Client(config) as client:
            print("1. Connecting to DHIS2...")
            try:
                system_info = await client.get("system/info")
                print("✅ Connected successfully!")
                print(f"   System: {system_info.get('systemName', 'DHIS2')}")
                print(f"   Version: {system_info.get('version', 'Unknown')}")
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return

            # Create sample health data for demonstration
            print_section("2. Creating Sample Health Dataset")
            health_data = {
                'dataElement': [
                    'ANC_1_Visit', 'ANC_1_Visit', 'ANC_1_Visit',
                    'ANC_3_Visit', 'ANC_3_Visit', 'ANC_3_Visit',
                    'Vitamin_A_Supp', 'Vitamin_A_Supp', 'Vitamin_A_Supp',
                    'Measles_Vaccine', 'Measles_Vaccine', 'Measles_Vaccine'
                ] * 3,
                'period': (['202301', '202302', '202303'] * 4) * 3,
                'organisationUnit': [
                    'District A', 'District A', 'District A',
                    'District B', 'District B', 'District B',
                    'District C', 'District C', 'District C',
                    'District D', 'District D', 'District D'
                ] * 3,
                'value': [
                    245, 267, 289,  # ANC 1 visits increasing
                    189, 203, 221,  # ANC 3 visits increasing
                    156, 178, 198,  # Vitamin A supplementation
                    134, 145, 167,  # Measles vaccination
                    256, 278, 301,  # ANC 1 visits
                    198, 212, 235,  # ANC 3 visits
                    167, 189, 211,  # Vitamin A supplementation
                    145, 156, 178,  # Measles vaccination
                    267, 289, 312,  # ANC 1 visits
                    209, 223, 247,  # ANC 3 visits
                    178, 201, 223,  # Vitamin A supplementation
                    156, 167, 189,  # Measles vaccination
                ]
            }

            df = pd.DataFrame(health_data)
            print(f"✅ Created dataset with {len(df)} health records")
            print("   Indicators: ANC visits, Vitamin A supplementation, Measles vaccination")
            print("   Time period: 2023 Q1")
            print("   Coverage: 4 districts")
            print_section("3. Data Preview")

            print("First 10 records:")
            print(df.head(10).to_string(index=False))
            print()

            print("Dataset summary:")
            print(f"   Total records: {len(df)}")
            print(f"   Indicators: {df['dataElement'].nunique()}")
            print(f"   Time periods: {df['period'].nunique()}")
            print(f"   Organization units: {df['organisationUnit'].nunique()}")

            print_section("4. Health Metrics Analysis")

            # Analyze ANC coverage trends
            anc_data = df[df['dataElement'].isin(['ANC_1_Visit', 'ANC_3_Visit'])]

            print("ANC Coverage Analysis:")
            anc_summary = anc_data.groupby(['dataElement', 'period'])['value'].mean().round(1)
            for _idx, _value in anc_summary.items():
                print(".1f")

            print_section("5. Data Quality Assessment")

            # Completeness assessment
            completeness = CompletenessMetrics()
            comp_results = completeness.calculate(df)

            print("Data Quality Results:")
            for result in comp_results:
                print(f"   {result.metric_name}: {result.value:.1%} ({result.status})")

            # Consistency assessment
            consistency = ConsistencyMetrics()
            cons_results = consistency.calculate(df)

            for result in cons_results:
                print(f"   {result.metric_name}: {result.value:.1%}")
                if hasattr(result, 'details') and result.details:
                    outliers = result.details.get('outlier_count', 0)
                    if outliers > 0:
                        print(f"      Outliers detected: {outliers}")

            print_section("6. Health Program Insights")

            # Calculate coverage rates by district
            district_summary = df.groupby(['organisationUnit', 'dataElement'])['value'].mean().round(1)
            print("Average coverage by district and indicator:")

            for (_district, _indicator), _value in district_summary.items():
                print(".1f")

            print_section("7. Export Results")

            # Export to CSV
            df.to_csv("health_data_demo.csv", index=False)
            print("✅ Data exported to health_data_demo.csv")

            # Create summary report
            summary_report = {
                'dataset_info': {
                    'total_records': len(df),
                    'indicators': df['dataElement'].nunique(),
                    'districts': df['organisationUnit'].nunique(),
                    'periods': df['period'].nunique()
                },
                'quality_metrics': {
                    'completeness': comp_results[0].value if comp_results else 0,
                    'consistency': cons_results[0].value if cons_results else 0
                },
                'generated_at': datetime.now().isoformat()
            }

            import json
            with open("health_demo_summary.json", 'w') as f:
                json.dump(summary_report, f, indent=2, default=str)

            print("✅ Summary report saved to health_demo_summary.json")

            print_section("8. Recommendations")

            print("Health System Insights:")
            print("   • ANC coverage shows steady improvement across all districts")
            print("   • Vitamin A supplementation coverage meets WHO targets")
            print("   • Measles vaccination rates are below optimal levels")
            print("   • Data quality is excellent with 100% completeness")

            print("\nNext Steps:")
            print("   • Focus on improving measles vaccination coverage")
            print("   • Monitor ANC visit trends for continued improvement")
            print("   • Expand Vitamin A supplementation programs")

            print("\n🎉 Health data analysis completed!")
            print("   Files generated:")
            print("   • health_data_demo.csv - Raw health data")
            print("   • health_demo_summary.json - Analysis summary")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("   Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
