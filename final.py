import ast
import glob
from typing import Dict
from pathlib import Path
import json
from datetime import datetime
from ai_documenter import AIDocumenter

class EnhancedCodeAnalyzer:
    def __init__(self, path: str):
        self.path = path
        self.is_directory = Path(path).is_dir()
        self.analyzers = {}
        self.project_name = Path(path).name.upper()
        self.ai_documenter = AIDocumenter()
        self.initialize_analyzers()

    def initialize_analyzers(self):
        if self.is_directory:
            for file in glob.glob(f"{self.path}/**/*.py", recursive=True):
                self.analyzers[file] = CodeSemanticAnalyzer(file)
        else:
            self.analyzers[self.path] = CodeSemanticAnalyzer(self.path)

    def analyze_with_details(self) -> Dict:
        results = {}
        for file_path, analyzer in self.analyzers.items():
            functions = {}
            for node in ast.walk(analyzer.tree):
                if isinstance(node, ast.FunctionDef):
                    functions[node.name] = analyzer.analyze_function(node)

            file_summary = analyzer.generate_file_summary(functions)
            results[file_path] = {
                'purpose': file_summary,
                'functions': functions
            }
        return results


    def generate_project_structure(self) -> str:
        structure = []
        base_path = Path(self.path)
        for file_path in self.analyzers.keys():
            rel_path = Path(file_path).relative_to(base_path)
            structure.append(f"├── {rel_path}")
        return "\n".join(structure)

    def save_analysis_report(self, results, output_file='project_documentation.md'):
        with open(output_file, 'w', encoding='utf-8') as f:
            # Project Header
            f.write(f"# {self.project_name}\n\n")

            # Description
            f.write("## Description\n")
            f.write(self._generate_project_description(results))
            f.write("\n\n")

            # Features
            f.write("## Features\n")
            features = self._extract_key_features(results)
            for feature in features:
                f.write(f"- {feature}\n")
            f.write("\n")

            # Project Structure
            f.write("## Project Structure\n")
            f.write("```\n")
            f.write(self.generate_project_structure())
            f.write("\n```\n\n")

            # Module Details
            f.write("## Module Details\n")
            for file_path, analysis in results.items():
                rel_path = Path(file_path).relative_to(Path(self.path))
                f.write(f"### {rel_path}\n")
                f.write(f"{analysis['purpose']}\n\n")
                f.write("#### Functions\n")
                for func_name, details in analysis['functions'].items():
                    f.write(f"- `{func_name}()`: {details['description']}\n")
                f.write("\n")

            # Dependencies
            f.write("## Dependencies\n")
            f.write("- Python 3.x\n")
            f.write("- Required packages listed in requirements.txt\n\n")

            # Add new AI Insights section
            f.write("## AI Analysis Insights\n\n")
            for file_path, analysis in results.items():
                f.write(f"### {Path(file_path).name}\n")
                code_insights = self.ai_documenter.generate_description(self.analyzers[file_path].code)
                f.write(f"{code_insights}\n\n")

            # Add Architecture Patterns
            f.write("## Architecture Patterns\n\n")


            # Usage
            f.write("## Usage\n")
            f.write("```python\n")
            f.write("# Example usage of key functions\n")
            self._write_example_usage(f, results)
            f.write("```\n\n")

            # Footer
            f.write(f"\n*Documentation generated on {datetime.now().strftime('%Y-%m-%d')}*\n")

    def _generate_project_description(self, results) -> str:
        total_modules = len(results)
        total_functions = sum(len(analysis['functions']) for analysis in results.values())
        return f"A Python project consisting of {total_modules} modules with {total_functions} functions implementing various data processing and analysis capabilities."

    def _extract_key_features(self, results) -> list:
        features = set()
        for analysis in results.values():
            for func_details in analysis['functions'].values():
                for operation in func_details.get('operations', []):
                    if operation.startswith('API'):
                        features.add(f"Implements {operation.split(':')[1].strip()} functionality")
                    else:
                        features.add(f"Supports {operation.lower()}")
        return sorted(list(features))

    def _write_example_usage(self, file, results):
        # Write example usage for the first meaningful function found
        for analysis in results.values():
            for func_name, details in analysis['functions'].items():
                if func_name.startswith('_'):
                    continue
                file.write(f"# Using {func_name}\n")
                file.write(f"result = {func_name}(input_data)\n")
                break


class CodeSemanticAnalyzer:
    def __init__(self, file_path: str):
        self.file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as file:
            self.code = file.read()
        self.tree = ast.parse(self.code)

    def analyze_function(self, node: ast.FunctionDef) -> Dict:
        operations = self._get_operations(node)
        return {
            'description': self._generate_function_description(node, operations),
            'operations': operations
        }

    def _get_operations(self, node: ast.FunctionDef) -> list:
        operations = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if hasattr(child.func, 'attr'):
                    operations.add(f"API: {child.func.attr}")
            elif isinstance(child, ast.With):
                operations.add("Resource management")
            elif isinstance(child, (ast.For, ast.While)):
                operations.add("Iteration")
            elif isinstance(child, ast.If):
                operations.add("Conditional logic")
        return list(operations)

    def _generate_function_description(self, node: ast.FunctionDef, operations: list) -> str:
        if not operations:
            return "Utility function with no external operations"
        return f"Handles {', '.join(operations).lower()}"

    def generate_file_summary(self, functions: Dict) -> str:
        all_operations = set()
        for func_details in functions.values():
            all_operations.update(op.lower() for op in func_details['operations'])

        return f"A module implementing {len(functions)} functions for {', '.join(all_operations)}"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Code Analysis Tool')
    parser.add_argument('--path', type=str, required=True, help='Path to file or directory')
    args = parser.parse_args()

    print(f"Analyzing: {args.path}")
    analyzer = EnhancedCodeAnalyzer(args.path)
    results = analyzer.analyze_with_details()
    analyzer.save_analysis_report(results)
    print("Documentation generated successfully!")
