#!/usr/bin/env python3
"""
Monthly Report Generation Script Example

This script demonstrates how to generate comprehensive monthly health data reports:
- Multi-indicator data collection
- Data analysis and visualization
- Generate HTML and Excel format reports
- Include data quality assessment

Usage:
    python monthly_report.py [--month YYYY-MM]
    
Examples:
    python monthly_report.py --month 2024-01  # Generate January 2024 report
    python monthly_report.py                   # Generate last month report
"""

import asyncio
import argparse
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from pydhis2 import AsyncDHIS2Client, DHIS2Config
from pydhis2.core.types import AnalyticsQuery
from pydhis2.dqr import CompletenessMetrics, ConsistencyMetrics


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonthlyReportGenerator:
    """Monthly report generator"""
    
    def __init__(self, config: DHIS2Config):
        self.config = config
        self.report_data = {}
        
    async def collect_data(self, month_period: str):
        """Collect data for specified month"""
        logger.info(f"Starting data collection for {month_period}...")
        
        async with AsyncDHIS2Client(self.config) as client:
            # Define key health indicators
            indicators = {
                'maternal_health': {
                    'name': 'Maternal Health',
                    'indicators': [
                        'Uvn6LCg7dVU',  # ANC 1st visit
                        'OdiHJayrsKo',  # ANC 3rd visit
                        'dwEq7wi6nXV',  # Skilled birth attendance
                    ]
                },
                'child_health': {
                    'name': 'Child Health',
                    'indicators': [
                        'cYeuwXTCPkU',  # BCG coverage
                        'Tt5TAvdfdVK',  # DPT3 coverage
                        'OfR8wBReTNI',  # Measles coverage
                    ]
                },
                'nutrition': {
                    'name': 'Nutrition Status',
                    'indicators': [
                        'ReUHfIn0pTQ',  # Vitamin A supplementation
                        'yTHydhurQQU',  # Iron folate supplementation
                    ]
                }
            }
            
            # Collect data for each category
            for category, info in indicators.items():
                logger.info(f"Collecting {info['name']} data...")
                
                query = AnalyticsQuery(
                    dx=info['indicators'],
                    ou="LEVEL-3",  # Provincial level data
                    pe=month_period
                )
                
                df = await client.analytics.to_pandas(query)
                self.report_data[category] = {
                    'name': info['name'],
                    'data': df,
                    'indicators': info['indicators']
                }
                
                logger.info(f"✅ {info['name']}: {len(df)} records")
    
    def analyze_data(self):
        """Analyze collected data"""
        logger.info("Starting data analysis...")
        
        self.analysis_results = {}
        
        for category, data_info in self.report_data.items():
            df = data_info['data']
            
            if df.empty:
                logger.warning(f"{data_info['name']} has no data")
                continue
            
            # Basic statistics
            numeric_values = pd.to_numeric(df['value'], errors='coerce').dropna()
            
            analysis = {
                'total_records': len(df),
                'org_units_count': df['organisationUnit'].nunique(),
                'indicators_count': df['dataElement'].nunique(),
                'mean_value': numeric_values.mean() if len(numeric_values) > 0 else 0,
                'median_value': numeric_values.median() if len(numeric_values) > 0 else 0,
                'std_value': numeric_values.std() if len(numeric_values) > 0 else 0,
                'min_value': numeric_values.min() if len(numeric_values) > 0 else 0,
                'max_value': numeric_values.max() if len(numeric_values) > 0 else 0,
            }
            
            # Data quality assessment
            completeness = CompletenessMetrics()
            comp_results = completeness.calculate(df)
            
            consistency = ConsistencyMetrics()
            cons_results = consistency.calculate(df)
            
            analysis['completeness_score'] = comp_results[0].value if comp_results else 0
            analysis['consistency_score'] = cons_results[0].value if cons_results else 0
            
            # Summary by organization unit
            org_summary = df.groupby('organisationUnit')['value'].agg([
                'count', 'mean', 'std'
            ]).round(2)
            analysis['org_summary'] = org_summary
            
            self.analysis_results[category] = analysis
            logger.info(f"✅ {data_info['name']} analysis completed")
    
    def generate_excel_report(self, output_file: Path):
        """Generate Excel report"""
        logger.info(f"Generating Excel report: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 1. Report overview
            overview_data = []
            for category, analysis in self.analysis_results.items():
                overview_data.append({
                    'Indicator Category': self.report_data[category]['name'],
                    'Total Records': analysis['total_records'],
                    'Organization Units': analysis['org_units_count'],
                    'Indicator Count': analysis['indicators_count'],
                    'Average Value': f"{analysis['mean_value']:.1f}",
                    'Completeness Score': f"{analysis['completeness_score']:.1%}",
                    'Consistency Score': f"{analysis['consistency_score']:.1%}"
                })
            
            overview_df = pd.DataFrame(overview_data)
            overview_df.to_excel(writer, sheet_name='Report Overview', index=False)
            
            # 2. Detailed data by category
            for category, data_info in self.report_data.items():
                if not data_info['data'].empty:
                    data_info['data'].to_excel(
                        writer, 
                        sheet_name=f"{data_info['name']}_Raw_Data", 
                        index=False
                    )
                    
                    # Organization unit summary
                    if category in self.analysis_results:
                        org_summary = self.analysis_results[category]['org_summary']
                        org_summary.to_excel(
                            writer, 
                            sheet_name=f"{data_info['name']}_Summary"
                        )
            
            # 3. Report information
            report_info = pd.DataFrame({
                'Item': [
                    'Report Generation Time',
                    'Data Source',
                    'Report Period',
                    'Total Records',
                    'Data Quality Rating'
                ],
                'Value': [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'DHIS2 Demo Server',
                    self.month_period,
                    sum(a['total_records'] for a in self.analysis_results.values()),
                    self._calculate_overall_quality()
                ]
            })
            report_info.to_excel(writer, sheet_name='Report Info', index=False)
    
    def generate_html_report(self, output_file: Path):
        """Generate HTML report"""
        logger.info(f"Generating HTML report: {output_file}")
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Monthly Health Data Report - {self.month_period}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
                .quality-good {{ color: #28a745; }}
                .quality-warning {{ color: #ffc107; }}
                .quality-poor {{ color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Monthly Health Data Report</h1>
                <p>Report Period: {self.month_period}</p>
                <p>Generation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        """
        
        # Add overview section
        html_content += """
            <div class="section">
                <h2>📊 Report Overview</h2>
        """
        
        total_records = sum(a['total_records'] for a in self.analysis_results.values())
        overall_quality = self._calculate_overall_quality()
        
        html_content += f"""
                <div class="metric">
                    <strong>Total Records</strong><br>
                    {total_records:,}
                </div>
                <div class="metric">
                    <strong>Data Categories</strong><br>
                    {len(self.analysis_results)}
                </div>
                <div class="metric">
                    <strong>Overall Quality</strong><br>
                    <span class="{self._get_quality_class(overall_quality)}">{overall_quality}</span>
                </div>
            </div>
        """
        
        # Add category details
        for category, analysis in self.analysis_results.items():
            category_name = self.report_data[category]['name']
            html_content += f"""
            <div class="section">
                <h3>📈 {category_name}</h3>
                <p><strong>Records:</strong> {analysis['total_records']:,}</p>
                <p><strong>Organization Units:</strong> {analysis['org_units_count']}</p>
                <p><strong>Average Value:</strong> {analysis['mean_value']:.1f}</p>
                <p><strong>Completeness:</strong> {analysis['completeness_score']:.1%}</p>
                <p><strong>Consistency:</strong> {analysis['consistency_score']:.1%}</p>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _calculate_overall_quality(self) -> str:
        """Calculate overall data quality rating"""
        if not self.analysis_results:
            return "No Data"
        
        avg_completeness = sum(a['completeness_score'] for a in self.analysis_results.values()) / len(self.analysis_results)
        avg_consistency = sum(a['consistency_score'] for a in self.analysis_results.values()) / len(self.analysis_results)
        
        overall_score = (avg_completeness + avg_consistency) / 2
        
        if overall_score >= 0.9:
            return "Excellent"
        elif overall_score >= 0.8:
            return "Good"
        elif overall_score >= 0.7:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _get_quality_class(self, quality: str) -> str:
        """Get CSS class for quality rating"""
        if quality in ["Excellent", "Good"]:
            return "quality-good"
        elif quality == "Fair":
            return "quality-warning"
        else:
            return "quality-poor"
    
    async def generate_report(self, month_period: str):
        """Generate complete report"""
        self.month_period = month_period
        
        # 1. Collect data
        await self.collect_data(month_period)
        
        # 2. Analyze data
        self.analyze_data()
        
        # 3. Create output directory
        output_dir = Path("reports") / month_period
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. Generate reports
        excel_file = output_dir / f"monthly_report_{month_period}.xlsx"
        html_file = output_dir / f"monthly_report_{month_period}.html"
        
        self.generate_excel_report(excel_file)
        self.generate_html_report(html_file)
        
        logger.info("✅ Monthly report generation completed")
        logger.info(f"📁 Excel report: {excel_file}")
        logger.info(f"🌐 HTML report: {html_file}")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate monthly health data report')
    parser.add_argument('--month', help='Report month (format: YYYY-MM)', default=None)
    args = parser.parse_args()
    
    # Determine report month
    if args.month:
        month_period = args.month.replace('-', '')
    else:
        # Default to last month
        last_month = datetime.now().replace(day=1) - timedelta(days=1)
        month_period = last_month.strftime('%Y%m')
    
    logger.info(f"Generating {month_period} monthly report")
    
    # Configure DHIS2 connection
    config = DHIS2Config(
        base_url="https://play.dhis2.org/stable-2-41-1",
        auth=("admin", "district"),
        rps=5.0
    )
    
    # Generate report
    generator = MonthlyReportGenerator(config)
    
    try:
        await generator.generate_report(month_period)
        print("\n🎉 Monthly report generation successful!")
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
