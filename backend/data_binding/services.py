"""
Data Binding Services
"""

import json
import csv
import io
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import requests
from django.utils import timezone


class DataFetcher:
    """Fetch data from various sources."""
    
    @staticmethod
    def fetch(data_source) -> Dict[str, Any]:
        """Fetch data from source."""
        fetcher_map = {
            'csv': DataFetcher.fetch_csv,
            'json': DataFetcher.fetch_json,
            'rest_api': DataFetcher.fetch_rest_api,
            'graphql': DataFetcher.fetch_graphql,
        }
        
        fetcher = fetcher_map.get(data_source.source_type)
        if not fetcher:
            raise ValueError(f"Unsupported source type: {data_source.source_type}")
        
        return fetcher(data_source)
    
    @staticmethod
    def fetch_csv(data_source) -> Dict[str, Any]:
        """Fetch and parse CSV file."""
        if data_source.file:
            content = data_source.file.read().decode('utf-8')
        elif data_source.url:
            response = requests.get(data_source.url)
            response.raise_for_status()
            content = response.text
        else:
            return {'data': [], 'error': 'No file or URL provided'}
        
        reader = csv.DictReader(io.StringIO(content))
        data = list(reader)
        
        return {
            'data': data,
            'count': len(data),
            'fields': reader.fieldnames or []
        }
    
    @staticmethod
    def fetch_json(data_source) -> Dict[str, Any]:
        """Fetch and parse JSON file."""
        if data_source.file:
            content = data_source.file.read().decode('utf-8')
            data = json.loads(content)
        elif data_source.url:
            response = requests.get(data_source.url)
            response.raise_for_status()
            data = response.json()
        else:
            return {'data': [], 'error': 'No file or URL provided'}
        
        # Extract data using path
        if data_source.data_path:
            data = DataFetcher._get_by_path(data, data_source.data_path)
        
        if isinstance(data, list):
            return {'data': data, 'count': len(data)}
        return {'data': [data], 'count': 1}
    
    @staticmethod
    def fetch_rest_api(data_source) -> Dict[str, Any]:
        """Fetch data from REST API."""
        headers = data_source.headers.copy()
        
        # Add authentication
        if data_source.auth_type == 'bearer':
            token = data_source.auth_config.get('token', '')
            headers['Authorization'] = f'Bearer {token}'
        elif data_source.auth_type == 'api_key':
            key_name = data_source.auth_config.get('key_name', 'X-API-Key')
            key_value = data_source.auth_config.get('key_value', '')
            headers[key_name] = key_value
        
        response = requests.request(
            method=data_source.method,
            url=data_source.url,
            headers=headers,
            params=data_source.query_params,
            data=data_source.body_template if data_source.method in ['POST', 'PUT', 'PATCH'] else None
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data_source.data_path:
            data = DataFetcher._get_by_path(data, data_source.data_path)
        
        if isinstance(data, list):
            return {'data': data, 'count': len(data)}
        return {'data': [data], 'count': 1}
    
    @staticmethod
    def fetch_graphql(data_source) -> Dict[str, Any]:
        """Fetch data from GraphQL API."""
        headers = {
            'Content-Type': 'application/json',
            **data_source.headers
        }
        
        # Add authentication
        if data_source.auth_type == 'bearer':
            token = data_source.auth_config.get('token', '')
            headers['Authorization'] = f'Bearer {token}'
        
        body = {
            'query': data_source.body_template,
            'variables': data_source.query_params
        }
        
        response = requests.post(
            data_source.url,
            headers=headers,
            json=body
        )
        response.raise_for_status()
        
        result = response.json()
        data = result.get('data', {})
        
        if data_source.data_path:
            data = DataFetcher._get_by_path(data, data_source.data_path)
        
        if isinstance(data, list):
            return {'data': data, 'count': len(data)}
        return {'data': [data], 'count': 1}
    
    @staticmethod
    def _get_by_path(data: Any, path: str) -> Any:
        """Get nested value by dot-notation path."""
        keys = path.split('.')
        result = data
        
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
            elif isinstance(result, list) and key.isdigit():
                result = result[int(key)]
            else:
                return None
        
        return result


class DataTransformer:
    """Transform data values."""
    
    @staticmethod
    def transform(value: Any, transform_type: str, config: Dict) -> Any:
        """Apply transformation to value."""
        transformers = {
            'format_date': DataTransformer.format_date,
            'format_number': DataTransformer.format_number,
            'format_currency': DataTransformer.format_currency,
            'truncate': DataTransformer.truncate,
            'uppercase': lambda v, c: str(v).upper(),
            'lowercase': lambda v, c: str(v).lower(),
            'capitalize': lambda v, c: str(v).capitalize(),
            'replace': DataTransformer.replace,
        }
        
        transformer = transformers.get(transform_type)
        if transformer:
            return transformer(value, config)
        return value
    
    @staticmethod
    def format_date(value: Any, config: Dict) -> str:
        """Format date value."""
        if not value:
            return ''
        
        format_str = config.get('format', '%Y-%m-%d')
        
        if isinstance(value, str):
            # Try to parse common formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    value = datetime.strptime(value.split('.')[0], fmt)
                    break
                except ValueError:
                    continue
        
        if isinstance(value, datetime):
            return value.strftime(format_str)
        
        return str(value)
    
    @staticmethod
    def format_number(value: Any, config: Dict) -> str:
        """Format number value."""
        try:
            num = float(value)
            decimals = config.get('decimals', 2)
            separator = config.get('thousands_separator', ',')
            
            formatted = f"{num:,.{decimals}f}"
            if separator != ',':
                formatted = formatted.replace(',', separator)
            
            return formatted
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def format_currency(value: Any, config: Dict) -> str:
        """Format currency value."""
        try:
            num = float(value)
            currency = config.get('currency', 'USD')
            
            symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥'}
            symbol = symbols.get(currency, currency + ' ')
            
            return f"{symbol}{num:,.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    @staticmethod
    def truncate(value: Any, config: Dict) -> str:
        """Truncate text."""
        text = str(value)
        max_length = config.get('max_length', 100)
        suffix = config.get('suffix', '...')
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def replace(value: Any, config: Dict) -> str:
        """Find and replace in text."""
        text = str(value)
        find = config.get('find', '')
        replace_with = config.get('replace', '')
        use_regex = config.get('regex', False)
        
        if use_regex:
            return re.sub(find, replace_with, text)
        return text.replace(find, replace_with)


class BindingEvaluator:
    """Evaluate data bindings."""
    
    @staticmethod
    def evaluate(binding, data_context: Dict) -> Any:
        """Evaluate binding with data context."""
        variable = binding.variable
        
        # Get base value
        if variable.data_source and variable.field_path:
            value = DataFetcher._get_by_path(data_context, variable.field_path)
        else:
            value = variable.default_value
        
        # Apply condition if present
        if binding.condition:
            try:
                result = BindingEvaluator._evaluate_condition(binding.condition, value, data_context)
                if result:
                    return binding.true_value or value
                return binding.false_value or ''
            except Exception:
                pass
        
        # Apply template if present
        if binding.template:
            return BindingEvaluator._apply_template(binding.template, data_context)
        
        return value
    
    @staticmethod
    def _evaluate_condition(condition: str, value: Any, context: Dict) -> bool:
        """Evaluate a simple condition."""
        # Simple condition evaluator (safe subset)
        condition = condition.strip()
        
        # Check for simple comparisons
        if '==' in condition:
            left, right = condition.split('==', 1)
            return str(BindingEvaluator._resolve_value(left.strip(), value, context)) == right.strip().strip("'\"")
        
        if '!=' in condition:
            left, right = condition.split('!=', 1)
            return str(BindingEvaluator._resolve_value(left.strip(), value, context)) != right.strip().strip("'\"")
        
        if '>=' in condition:
            left, right = condition.split('>=', 1)
            return float(BindingEvaluator._resolve_value(left.strip(), value, context)) >= float(right.strip())
        
        if '<=' in condition:
            left, right = condition.split('<=', 1)
            return float(BindingEvaluator._resolve_value(left.strip(), value, context)) <= float(right.strip())
        
        # Truthy check
        resolved = BindingEvaluator._resolve_value(condition, value, context)
        return bool(resolved)
    
    @staticmethod
    def _resolve_value(expr: str, value: Any, context: Dict) -> Any:
        """Resolve expression to value."""
        if expr == 'value':
            return value
        if expr.startswith('data.'):
            return DataFetcher._get_by_path(context, expr[5:])
        return expr
    
    @staticmethod
    def _apply_template(template: str, context: Dict) -> str:
        """Apply template with context."""
        def replace_var(match):
            path = match.group(1)
            value = DataFetcher._get_by_path(context, path)
            return str(value) if value is not None else ''
        
        return re.sub(r'\{\{(\w+(?:\.\w+)*)\}\}', replace_var, template)


class SchemaInferrer:
    """Infer schema from data."""
    
    @staticmethod
    def infer_schema(data: List[Dict]) -> Dict:
        """Infer schema from data list."""
        if not data:
            return {'fields': []}
        
        fields = []
        sample = data[0]
        
        for key, value in sample.items():
            field_type = SchemaInferrer._infer_type(value)
            fields.append({
                'name': key,
                'type': field_type,
                'sample': str(value)[:100] if value else None
            })
        
        return {'fields': fields, 'count': len(data)}
    
    @staticmethod
    def _infer_type(value: Any) -> str:
        """Infer field type from value."""
        if value is None:
            return 'string'
        if isinstance(value, bool):
            return 'boolean'
        if isinstance(value, int):
            return 'number'
        if isinstance(value, float):
            return 'number'
        if isinstance(value, list):
            return 'array'
        if isinstance(value, dict):
            return 'json'
        
        # String analysis
        value_str = str(value)
        
        # Date patterns
        if re.match(r'^\d{4}-\d{2}-\d{2}$', value_str):
            return 'date'
        if re.match(r'^\d{4}-\d{2}-\d{2}T', value_str):
            return 'datetime'
        
        # URL pattern
        if value_str.startswith(('http://', 'https://')):
            if any(ext in value_str.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                return 'image'
            return 'url'
        
        # Color pattern
        if re.match(r'^#[0-9a-fA-F]{6}$', value_str):
            return 'color'
        
        return 'string'
