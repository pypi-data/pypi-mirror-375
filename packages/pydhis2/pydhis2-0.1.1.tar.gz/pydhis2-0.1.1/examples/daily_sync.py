#!/usr/bin/env python3
"""
Daily Data Synchronization Script Example

This script demonstrates how to set up daily automatic synchronization tasks:
- Pull yesterday's data from DHIS2
- Perform basic data quality checks
- Save to local file system
- Can be used with cron or Windows Task Scheduler

Usage:
    python daily_sync.py
    
Scheduled task setup (Linux cron):
    # Execute daily at 2 AM
    0 2 * * * /usr/bin/python3 /path/to/daily_sync.py
    
Scheduled task setup (Windows):
    schtasks /create /tn "DHIS2 Daily Sync" /tr "python C:\path\to\daily_sync.py" /sc daily /st 02:00
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from pydhis2 import AsyncDHIS2Client, DHIS2Config
from pydhis2.core.types import AnalyticsQuery


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def daily_sync():
    """Execute daily data synchronization"""
    logger.info("Starting daily data synchronization...")
    
    # Calculate yesterday's date
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    logger.info(f"Sync date: {yesterday}")
    
    # DHIS2 configuration
    config = DHIS2Config(
        base_url="https://play.dhis2.org/stable-2-41-1",
        auth=("admin", "district"),
        rps=5.0,  # Moderate request rate
        max_retries=8
    )
    
    try:
        async with AsyncDHIS2Client(config) as client:
            # 1. Test connection
            logger.info("Testing DHIS2 connection...")
            system_info = await client.get_system_info()
            logger.info(f"Connection successful: {system_info.get('systemName', 'DHIS2')}")
            
            # 2. Define indicators to synchronize
            indicators = [
                "Uvn6LCg7dVU",  # ANC 1st visit
                "OdiHJayrsKo",  # ANC 3rd visit
                "dwEq7wi6nXV",  # Skilled birth attendance
            ]
            
            # 3. Query yesterday's data
            logger.info(f"Querying indicator data: {len(indicators)} indicators")
            query = AnalyticsQuery(
                dx=indicators,
                ou="USER_ORGUNIT",  # User organization unit
                pe=yesterday
            )
            
            df = await client.analytics.to_pandas(query)
            logger.info(f"Retrieved {len(df)} records")
            
            if df.empty:
                logger.warning("No data retrieved, possibly weekend or holiday")
                return
            
            # 4. Data quality checks
            logger.info("Performing data quality checks...")
            
            # Check missing values
            missing_count = df['value'].isna().sum()
            total_count = len(df)
            completeness = (total_count - missing_count) / total_count * 100
            
            logger.info(f"Data completeness: {completeness:.1f}% ({total_count - missing_count}/{total_count})")
            
            # Check outliers
            numeric_values = pd.to_numeric(df['value'], errors='coerce').dropna()
            if len(numeric_values) > 0:
                mean_val = numeric_values.mean()
                std_val = numeric_values.std()
                outliers = numeric_values[
                    (numeric_values > mean_val + 3*std_val) | 
                    (numeric_values < mean_val - 3*std_val)
                ]
                logger.info(f"Outlier detection: found {len(outliers)} outliers")
            
            # 5. Save data
            data_dir = Path("data/daily")
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Save raw data
            csv_file = data_dir / f"{yesterday}.csv"
            df.to_csv(csv_file, index=False)
            logger.info(f"Data saved to: {csv_file}")
            
            # Save summary statistics
            summary_stats = df.groupby('dataElement')['value'].agg([
                'count', 'mean', 'std', 'min', 'max'
            ]).round(2)
            
            summary_file = data_dir / f"{yesterday}_summary.csv"
            summary_stats.to_csv(summary_file)
            logger.info(f"Summary statistics saved to: {summary_file}")
            
            # 6. Generate sync report
            report = {
                'sync_date': yesterday,
                'sync_time': datetime.now().isoformat(),
                'total_records': len(df),
                'indicators_count': len(df['dataElement'].unique()),
                'completeness_pct': completeness,
                'outliers_count': len(outliers) if 'outliers' in locals() else 0,
                'status': 'success'
            }
            
            report_file = data_dir / f"{yesterday}_report.json"
            import json
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info("✅ Daily sync completed")
            logger.info(f"Sync report: {report}")
            
    except Exception as e:
        logger.error(f"❌ Sync failed: {e}")
        
        # Record failure report
        error_report = {
            'sync_date': yesterday,
            'sync_time': datetime.now().isoformat(),
            'status': 'failed',
            'error': str(e)
        }
        
        data_dir = Path("data/daily")
        data_dir.mkdir(parents=True, exist_ok=True)
        error_file = data_dir / f"{yesterday}_error.json"
        
        import json
        with open(error_file, 'w') as f:
            json.dump(error_report, f, indent=2)
        
        raise


async def main():
    """Main function"""
    try:
        await daily_sync()
    except KeyboardInterrupt:
        logger.info("Sync interrupted by user")
    except Exception as e:
        logger.error(f"Error during sync process: {e}")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())