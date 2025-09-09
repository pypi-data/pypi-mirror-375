#!/usr/bin/env python3
"""
Custom Pipeline Steps Example

This file demonstrates how to create custom Pipeline steps, including:
- Data transformation steps
- Data validation steps
- Report generation steps
- External system integration steps

Usage:
    Reference these custom steps in pipeline.yml configuration files
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import logging
from typing import Dict, Any, Optional
from pydhis2.pipeline import PipelineStep, StepRegistry
from pydhis2.core.types import AnalyticsQuery


logger = logging.getLogger(__name__)


class DataTransformStep(PipelineStep):
    """Data transformation step"""
    
    async def execute(self, client=None, context=None) -> Dict[str, Any]:
        """Execute data transformation"""
        input_file = self.params.get('input_file')
        output_file = self.params.get('output_file')
        transform_type = self.params.get('transform_type', 'pivot')
        
        logger.info(f"Starting data transformation: {transform_type}")
        
        # Read input data
        if input_file.endswith('.parquet'):
            df = pd.read_parquet(input_file)
        elif input_file.endswith('.csv'):
            df = pd.read_csv(input_file)
        else:
            raise ValueError(f"Unsupported file format: {input_file}")
        
        # Execute transformation
        if transform_type == 'pivot':
            # Create pivot table
            transformed_df = df.pivot_table(
                values='value',
                index=['organisationUnit', 'period'],
                columns='dataElement',
                aggfunc='first'
            ).reset_index()
            
        elif transform_type == 'aggregate':
            # Aggregate by organization unit
            transformed_df = df.groupby(['organisationUnit', 'dataElement'])['value'].agg([
                'count', 'mean', 'sum', 'std'
            ]).reset_index()
            
        elif transform_type == 'normalize':
            # Data normalization
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df_normalized = df.copy()
            df_normalized[numeric_cols] = (df[numeric_cols] - df[numeric_cols].mean()) / df[numeric_cols].std()
            transformed_df = df_normalized
            
        else:
            raise ValueError(f"Unsupported transformation type: {transform_type}")
        
        # Save results
        if output_file.endswith('.parquet'):
            transformed_df.to_parquet(output_file, index=False)
        elif output_file.endswith('.csv'):
            transformed_df.to_csv(output_file, index=False)
        
        logger.info(f"Data transformation completed: {len(transformed_df)} rows")
        
        return {
            'status': 'success',
            'input_rows': len(df),
            'output_rows': len(transformed_df),
            'transform_type': transform_type,
            'output_file': output_file
        }


class DataValidationStep(PipelineStep):
    """Data validation step"""
    
    async def execute(self, client=None, context=None) -> Dict[str, Any]:
        """Execute data validation"""
        input_file = self.params.get('input_file')
        validation_rules = self.params.get('rules', {})
        
        logger.info("Starting data validation...")
        
        # Read data
        if input_file.endswith('.parquet'):
            df = pd.read_parquet(input_file)
        else:
            df = pd.read_csv(input_file)
        
        validation_results = {
            'total_records': len(df),
            'validation_errors': [],
            'warnings': [],
            'passed': True
        }
        
        # 1. Required columns check
        required_columns = validation_rules.get('required_columns', [])
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_results['validation_errors'].append(
                f"Missing required columns: {missing_columns}"
            )
            validation_results['passed'] = False
        
        # 2. Data type check
        if 'value' in df.columns:
            non_numeric = pd.to_numeric(df['value'], errors='coerce').isna().sum()
            if non_numeric > 0:
                validation_results['warnings'].append(
                    f"Found {non_numeric} non-numeric records"
                )
        
        # 3. Range check
        value_range = validation_rules.get('value_range')
        if value_range and 'value' in df.columns:
            numeric_values = pd.to_numeric(df['value'], errors='coerce')
            out_of_range = (
                (numeric_values < value_range['min']) | 
                (numeric_values > value_range['max'])
            ).sum()
            
            if out_of_range > 0:
                validation_results['warnings'].append(
                    f"Found {out_of_range} values out of range"
                )
        
        # 4. Duplicate records check
        if validation_rules.get('check_duplicates', False):
            duplicate_columns = validation_rules.get('duplicate_columns', df.columns.tolist())
            duplicates = df.duplicated(subset=duplicate_columns).sum()
            if duplicates > 0:
                validation_results['warnings'].append(
                    f"Found {duplicates} duplicate records"
                )
        
        # 5. Completeness check
        completeness_threshold = validation_rules.get('completeness_threshold', 0.8)
        missing_rate = df.isnull().sum().sum() / (len(df) * len(df.columns))
        if missing_rate > (1 - completeness_threshold):
            validation_results['validation_errors'].append(
                f"Data completeness insufficient: {(1-missing_rate)*100:.1f}% < {completeness_threshold*100}%"
            )
            validation_results['passed'] = False
        
        # Save validation report
        report_file = input_file.replace('.csv', '_validation.json').replace('.parquet', '_validation.json')
        with open(report_file, 'w') as f:
            json.dump(validation_results, f, indent=2)
        
        logger.info(f"Data validation completed: {'Passed' if validation_results['passed'] else 'Failed'}")
        
        return validation_results


class ReportGenerationStep(PipelineStep):
    """Report generation step"""
    
    async def execute(self, client=None, context=None) -> Dict[str, Any]:
        """Generate report"""
        input_files = self.params.get('input_files', [])
        output_file = self.params.get('output_file')
        report_type = self.params.get('report_type', 'summary')
        
        logger.info(f"Starting report generation: {report_type}")
        
        # Read all input files
        dataframes = {}
        for file_path in input_files:
            file_name = Path(file_path).stem
            if file_path.endswith('.parquet'):
                dataframes[file_name] = pd.read_parquet(file_path)
            else:
                dataframes[file_name] = pd.read_csv(file_path)
        
        if report_type == 'excel':
            # Generate Excel report
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                # Overview page
                overview_data = []
                for name, df in dataframes.items():
                    overview_data.append({
                        'Dataset': name,
                        'Records': len(df),
                        'Columns': len(df.columns),
                        'Missing Values': df.isnull().sum().sum(),
                        'Completeness': f"{(1 - df.isnull().sum().sum() / (len(df) * len(df.columns)))*100:.1f}%"
                    })
                
                overview_df = pd.DataFrame(overview_data)
                overview_df.to_excel(writer, sheet_name='Overview', index=False)
                
                # Dataset details
                for name, df in dataframes.items():
                    df.to_excel(writer, sheet_name=name[:30], index=False)  # Excel sheet name limit
        
        elif report_type == 'html':
            # Generate HTML report
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Data Processing Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Data Processing Report</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
            """
            
            for name, df in dataframes.items():
                html_content += f"""
                <div class="section">
                    <h2>{name}</h2>
                    <p>Records: {len(df)}</p>
                    <p>Columns: {len(df.columns)}</p>
                    {df.head().to_html(classes='table')}
                </div>
                """
            
            html_content += "</body></html>"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        logger.info(f"Report generation completed: {output_file}")
        
        return {
            'status': 'success',
            'report_type': report_type,
            'output_file': output_file,
            'datasets_count': len(dataframes),
            'total_records': sum(len(df) for df in dataframes.values())
        }


class ExternalSystemIntegrationStep(PipelineStep):
    """External system integration step"""
    
    async def execute(self, client=None, context=None) -> Dict[str, Any]:
        """Integrate with external systems"""
        input_file = self.params.get('input_file')
        system_type = self.params.get('system_type')
        config = self.params.get('config', {})
        
        logger.info(f"Starting external system integration: {system_type}")
        
        # Read data
        if input_file.endswith('.parquet'):
            df = pd.read_parquet(input_file)
        else:
            df = pd.read_csv(input_file)
        
        if system_type == 'email':
            # Send email notification
            return await self._send_email_notification(df, config)
            
        elif system_type == 'webhook':
            # Send webhook
            return await self._send_webhook(df, config)
            
        elif system_type == 'database':
            # Write to database
            return await self._write_to_database(df, config)
            
        else:
            raise ValueError(f"Unsupported system type: {system_type}")
    
    async def _send_email_notification(self, df: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Send email notification (mock)"""
        # This should implement real email sending logic
        logger.info(f"Mock email notification sent: {len(df)} records processed")
        
        return {
            'status': 'success',
            'action': 'email_sent',
            'recipients': config.get('recipients', []),
            'records_count': len(df)
        }
    
    async def _send_webhook(self, df: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Send webhook (mock)"""
        # This should implement real HTTP request
        webhook_url = config.get('url')
        logger.info(f"Mock webhook sent to: {webhook_url}")
        
        return {
            'status': 'success',
            'action': 'webhook_sent',
            'url': webhook_url,
            'records_count': len(df)
        }
    
    async def _write_to_database(self, df: pd.DataFrame, config: Dict) -> Dict[str, Any]:
        """Write to database (mock)"""
        # This should implement real database writing logic
        table_name = config.get('table_name', 'dhis2_data')
        logger.info(f"Mock database write to table: {table_name}")
        
        return {
            'status': 'success',
            'action': 'database_written',
            'table_name': table_name,
            'records_written': len(df)
        }


# Register custom steps
StepRegistry.register('data_transform', DataTransformStep)
StepRegistry.register('data_validation', DataValidationStep)
StepRegistry.register('report_generation', ReportGenerationStep)
StepRegistry.register('external_integration', ExternalSystemIntegrationStep)


# Usage example
if __name__ == "__main__":
    print("Custom Pipeline steps defined:")
    print("- data_transform: Data transformation")
    print("- data_validation: Data validation")
    print("- report_generation: Report generation")
    print("- external_integration: External system integration")
    print()
    print("Use these steps in pipeline.yml:")
    print("""
steps:
  - type: "data_transform"
    name: "transform_data"
    params:
      input_file: "data/raw.csv"
      output_file: "data/transformed.csv"
      transform_type: "pivot"
      
  - type: "data_validation"
    name: "validate_data"
    params:
      input_file: "data/transformed.csv"
      rules:
        required_columns: ["organisationUnit", "period", "value"]
        value_range: {"min": 0, "max": 100}
        completeness_threshold: 0.8
    """)
