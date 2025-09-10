#!/usr/bin/env python3
"""
pydhis2 Quick Demo Script

This script demonstrates the basic functionality of pydhis2, including:
- Connecting to DHIS2 demo server
- Querying Analytics data
- Data analysis and visualization
- Generating reports

Usage:
    python quick_demo.py
"""

import asyncio
import sys
from datetime import datetime

import pandas as pd

from pydhis2 import DHIS2Config, get_client
from pydhis2.core.types import AnalyticsQuery

# Fix for Windows asyncio compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def print_banner():
    """Print banner"""
    print("=" * 60)
    print("pydhis2 Quick Demo")
    print("=" * 60)
    print()


def print_section(title):
    """Print section title"""
    print(f"{title}")
    print("-" * 60)


def create_progress_bar(value, max_value, width=30):
    """Create simple progress bar"""
    filled = int(width * value / max_value)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {value}"


async def main():
    """Main demo function"""
    print_banner()

    # Get client class
    AsyncDHIS2Client, SyncDHIS2Client = get_client()  # noqa: N806

    # Configure DHIS2 connection (using public demo server)
    config = DHIS2Config(
        base_url="https://play.dhis2.org/dev",
        auth=("admin", "district"),
        rps=3.0,  # Conservative request rate
        max_retries=5
    )

    try:
        async with AsyncDHIS2Client(config) as client:
            # 1. Test connection
            print("1. Testing DHIS2 connection...")
            try:
                # Get system information using the system/info endpoint
                system_info = await client.get("system/info")
                print("✅ Connection successful!")
                print(f"   System: {system_info.get('systemName', 'DHIS2 Demo')}")
                print(f"   Version: {system_info.get('version', 'Unknown')}")
                print(f"   URL: {config.base_url}")
                print()
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return

            # 2. Get metadata information
            print("2. Getting metadata information...")
            try:
                # Try to get organisation units (may be restricted in demo server)
                org_units = await client.get("organisationUnits", {
                    "fields": "id,displayName",
                    "pageSize": 3
                })
                org_units_data = org_units.get("organisationUnits", [])
                if org_units_data:
                    print(f"✅ Found {len(org_units_data)} organisation units")
                    for org in org_units_data[:2]:
                        print(f"   - {org.get('displayName', 'Unknown')}")
                else:
                    print("ℹ️  Organisation units not accessible (demo server restriction)")
                print()

            except Exception as e:
                print(f"ℹ️  Metadata query limited (demo server): {type(e).__name__}")
                print("   This is normal for demo servers with restricted access")
                print()

            # 3. Try to get analytics data
            print("3. Querying Analytics data...")
            query = AnalyticsQuery(
                dx=["ReUHfIn0pTQ"],  # Vitamin A supplementation
                ou="LEVEL-3",         # Provincial level
                pe="2023"            # 2023 year
            )

            # Try to get analytics data, or create demo data if not available
            df = pd.DataFrame()  # Initialize empty DataFrame

            try:
                df = await client.analytics.to_pandas(query)
                if not df.empty:
                    print(f"✅ Retrieved {len(df)} data records from DHIS2")
                else:
                    print("ℹ️  No data returned from DHIS2, creating sample data...")
                    raise Exception("Empty data response")
                print()
            except Exception as e:
                print(f"ℹ️  Using sample data for demonstration: {type(e).__name__}")
                print("   This is normal - demo servers often have limited data access")
                demo_data = {
                    'dataElement': ['ANC_1_Visit', 'ANC_3_Visit', 'Vitamin_A_Supp'] * 2,
                    'period': ['202301', '202301', '202301', '202302', '202302', '202302'],
                    'organisationUnit': ['District A', 'District B', 'District C'] * 2,
                    'value': [245, 189, 156, 267, 203, 178]
                }
                df = pd.DataFrame(demo_data)
                print(f"   ✅ Created sample dataset with {len(df)} records")
                print()

            # 4. Data preview
            print("4. Data preview:")
            print_section("")
            if not df.empty:
                # Show first few rows
                print(df.head().to_string(index=False))
                print()
            else:
                print("No data available for the specified query.")
                return

            # 5. Data statistics
            print("5. Data statistics:")
            print_section("")
            if 'value' in df.columns:
                values = pd.to_numeric(df['value'], errors='coerce').dropna()
                if not values.empty:
                    print(f"   Total records: {len(values)}")
                    print(f"   Sum of values: {values.sum():,.0f}")
                    print(f"   Average: {values.mean():.1f}")
                    print(f"   Maximum: {values.max():,.0f}")
                    print(f"   Minimum: {values.min():,.0f}")
                    print()
                else:
                    print("   No numeric values found.")
                    return

            # 6. Monthly trends (simple text chart)
            print("6. Monthly trends:")
            print_section("")
            if 'period' in df.columns and 'value' in df.columns:
                # Group by period and calculate average
                monthly_data = df.groupby('period')['value'].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').mean()
                ).dropna().sort_index()

                if not monthly_data.empty:
                    max_value = monthly_data.max()
                    for period, value in monthly_data.items():
                        bar = create_progress_bar(value, max_value)
                        print(f"   {period}: {bar} {value:.0f}")
                    print()
                else:
                    print("   No trend data available.")

            # 7. Data quality assessment
            print("7. Data Quality Assessment:")
            print_section("")

            # Completeness check
            total_expected = len(df)
            missing_values = df['value'].isna().sum() if 'value' in df.columns else 0
            completeness = (total_expected - missing_values) / total_expected * 100 if total_expected > 0 else 0

            print(f"   Data Completeness: {completeness:.1f}%")
            print(f"   Total records: {total_expected}")
            print(f"   Missing values: {missing_values}")

            # Outlier detection
            if 'value' in df.columns:
                numeric_values = pd.to_numeric(df['value'], errors='coerce').dropna()
                if len(numeric_values) > 0:
                    mean_val = numeric_values.mean()
                    std_val = numeric_values.std()
                    outliers = numeric_values[(numeric_values > mean_val + 3*std_val) |
                                            (numeric_values < mean_val - 3*std_val)]
                    print(f"   Outliers detected: {len(outliers)} ({len(outliers)/len(numeric_values)*100:.1f}%)")

            print()

            # 7. Save results
            print("7. Saving results...")
            try:
                # Save as CSV
                df.to_csv("demo_results.csv", index=False)
                print("✅ Results saved to demo_results.csv")

                # Generate simple statistical report
                if 'value' in df.columns:
                    summary_stats = df.groupby('period')['value'].agg([
                        'count', 'mean', 'std', 'min', 'max'
                    ]).round(2)
                    summary_stats.to_csv("demo_summary.csv")
                    print("✅ Summary statistics saved to demo_summary.csv")

            except Exception as e:
                print(f"⚠️ Could not save files: {e}")

            print()
            print("🎉 Demo completed successfully!")
            print("   Check the generated CSV files for detailed results.")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("   Please check your internet connection and try again.")


def main_sync():
    """Entry point for console script"""
    print(f"Starting pydhis2 demo at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    try:
        asyncio.run(main())
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

    # Configure DHIS2 connection (using public demo server)
    config = DHIS2Config(
        base_url="https://play.dhis2.org/dev",
        auth=("admin", "district"),
        rps=3.0,  # Conservative request rate
        max_retries=5
    )

    try:
        async with AsyncDHIS2Client(config) as client:
            # 1. Test connection
            print("1. Testing DHIS2 connection...")
            try:
                # Get system information using the system/info endpoint
                system_info = await client.get("system/info")
                print("✅ Connection successful!")
                print(f"   System: {system_info.get('systemName', 'DHIS2 Demo')}")
                print(f"   Version: {system_info.get('version', 'Unknown')}")
                print(f"   URL: {config.base_url}")
                print()
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return

            # 2. Get metadata information
            print("2. Getting metadata information...")
            try:
                # Try to get organisation units (may be restricted in demo server)
                org_units = await client.get("organisationUnits", {
                    "fields": "id,displayName",
                    "pageSize": 3
                })
                org_units_data = org_units.get("organisationUnits", [])
                if org_units_data:
                    print(f"✅ Found {len(org_units_data)} organisation units")
                    for org in org_units_data[:2]:
                        print(f"   - {org.get('displayName', 'Unknown')}")
                else:
                    print("ℹ️  Organisation units not accessible (demo server restriction)")
                print()

            except Exception as e:
                print(f"ℹ️  Metadata query limited (demo server): {type(e).__name__}")
                print("   This is normal for demo servers with restricted access")
                print()

            # 3. Try to get analytics data
            print("3. Querying Analytics data...")
            query = AnalyticsQuery(
                dx=["ReUHfIn0pTQ"],  # Vitamin A supplementation
                ou="LEVEL-3",         # Provincial level
                pe="2023"            # 2023 year
            )

            # Try to get analytics data, or create demo data if not available
            df = pd.DataFrame()  # Initialize empty DataFrame

            try:
                df = await client.analytics.to_pandas(query)
                if not df.empty:
                    print(f"✅ Retrieved {len(df)} data records from DHIS2")
                else:
                    print("ℹ️  No data returned from DHIS2, creating sample data...")
                    raise Exception("Empty data response")
                print()
            except Exception as e:
                print(f"ℹ️  Using sample data for demonstration: {type(e).__name__}")
                print("   This is normal - demo servers often have limited data access")
                demo_data = {
                    'dataElement': ['ANC_1_Visit', 'ANC_3_Visit', 'Vitamin_A_Supp'] * 2,
                    'period': ['202301', '202301', '202301', '202302', '202302', '202302'],
                    'organisationUnit': ['District A', 'District B', 'District C'] * 2,
                    'value': [245, 189, 156, 267, 203, 178]
                }
                df = pd.DataFrame(demo_data)
                print(f"   ✅ Created sample dataset with {len(df)} records")
                print()

            # 4. Data preview
            print("4. Data preview:")
            print_section("")
            if not df.empty:
                # Show first few rows
                print(df.head().to_string(index=False))
                print()
            else:
                print("No data available for the specified query.")
                return

            # 5. Data statistics
            print("5. Data statistics:")
            print_section("")
            if 'value' in df.columns:
                values = pd.to_numeric(df['value'], errors='coerce').dropna()
                if not values.empty:
                    print(f"   Total records: {len(values)}")
                    print(f"   Sum of values: {values.sum():,.0f}")
                    print(f"   Average: {values.mean():.1f}")
                    print(f"   Maximum: {values.max():,.0f}")
                    print(f"   Minimum: {values.min():,.0f}")
                    print()
                else:
                    print("   No numeric values found.")
                    return

            # 6. Monthly trends (simple text chart)
            print("6. Monthly trends:")
            print_section("")
            if 'period' in df.columns and 'value' in df.columns:
                # Group by period and calculate average
                monthly_data = df.groupby('period')['value'].apply(
                    lambda x: pd.to_numeric(x, errors='coerce').mean()
                ).dropna().sort_index()

                if not monthly_data.empty:
                    max_value = monthly_data.max()
                    for period, value in monthly_data.items():
                        bar = create_progress_bar(value, max_value)
                        print(f"   {period}: {bar} {value:.0f}")
                    print()
                else:
                    print("   No trend data available.")

            # 7. Data quality assessment
            print("7. Data Quality Assessment:")
            print_section("")

            # Completeness check
            total_expected = len(df)
            missing_values = df['value'].isna().sum() if 'value' in df.columns else 0
            completeness = (total_expected - missing_values) / total_expected * 100 if total_expected > 0 else 0

            print(f"   Data Completeness: {completeness:.1f}%")
            print(f"   Total records: {total_expected}")
            print(f"   Missing values: {missing_values}")

            # Outlier detection
            if 'value' in df.columns:
                numeric_values = pd.to_numeric(df['value'], errors='coerce').dropna()
                if len(numeric_values) > 0:
                    mean_val = numeric_values.mean()
                    std_val = numeric_values.std()
                    outliers = numeric_values[(numeric_values > mean_val + 3*std_val) |
                                            (numeric_values < mean_val - 3*std_val)]
                    print(f"   Outliers detected: {len(outliers)} ({len(outliers)/len(numeric_values)*100:.1f}%)")

            print()

            # 7. Save results
            print("7. Saving results...")
            try:
                # Save as CSV
                df.to_csv("demo_results.csv", index=False)
                print("✅ Results saved to demo_results.csv")

                # Generate simple statistical report
                if 'value' in df.columns:
                    summary_stats = df.groupby('period')['value'].agg([
                        'count', 'mean', 'std', 'min', 'max'
                    ]).round(2)
                    summary_stats.to_csv("demo_summary.csv")
                    print("✅ Summary statistics saved to demo_summary.csv")

            except Exception as e:
                print(f"⚠️ Could not save files: {e}")

            print()
            print("🎉 Demo completed successfully!")
            print("   Check the generated CSV files for detailed results.")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("   Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
