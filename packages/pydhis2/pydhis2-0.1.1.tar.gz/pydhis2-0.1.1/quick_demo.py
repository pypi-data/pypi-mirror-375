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
import pandas as pd
from datetime import datetime
from pydhis2 import AsyncDHIS2Client, DHIS2Config
from pydhis2.core.types import AnalyticsQuery


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
    
    # Configure DHIS2 connection (using public demo server)
    config = DHIS2Config(
        base_url="https://play.dhis2.org/stable-2-41-1",
        auth=("admin", "district"),
        rps=3.0,  # Conservative request rate
        max_retries=5
    )
    
    try:
        async with AsyncDHIS2Client(config) as client:
            # 1. Test connection
            print("1. Testing DHIS2 connection...")
            try:
                system_info = await client.get_system_info()
                print("✅ Connection successful!")
                print(f"   System: {system_info.get('systemName', 'DHIS2 Demo')}")
                print(f"   Version: {system_info.get('version', 'Unknown')}")
                print(f"   URL: {config.base_url}")
                print()
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                return
            
            # 2. Query Analytics data
            print("2. Querying Analytics data...")
            query = AnalyticsQuery(
                dx=["Uvn6LCg7dVU"],  # ANC 1st visit coverage
                ou="ImspTQPwCqd",    # Sierra Leone
                pe="LAST_12_MONTHS"  # Last 12 months
            )
            
            try:
                df = await client.analytics.to_pandas(query)
                print(f"✅ Retrieved {len(df)} data records")
                print()
            except Exception as e:
                print(f"❌ Data query failed: {e}")
                return
            
            # 3. Data preview
            print("3. Data preview:")
            print_section("")
            if not df.empty:
                # Show first few rows
                print(df.head().to_string(index=False))
                print()
            else:
                print("No data available for the specified query.")
                return
            
            # 4. Data statistics
            print("4. Data statistics:")
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
            
            # 5. Monthly trends (simple text chart)
            print("5. Monthly trends:")
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
            
            # 6. Data quality assessment
            print("6. Data Quality Assessment:")
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
    print(f"Starting pydhis2 demo at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
    
    print("\nThank you for trying pydhis2! 🚀")