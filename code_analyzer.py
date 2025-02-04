from tree_sitter import Language, Parser
import os
from pathlib import Path
import glob
import re  # For pattern matching
from typing import Dict, List  # For type hints

class CodeAnalyzer:
    def __init__(self, directory_path: str):
        self.directory = directory_path
        self.parser, self.language = self.setup_parser()

    def setup_parser(self):
        LANGUAGE_PATH = os.path.expanduser('~/.tree-sitter/tree-sitter-python.so')
        language = Language(LANGUAGE_PATH, 'python')
        parser = Parser()
        parser.set_language(language)
        return parser, language

    def analyze_imports(self, node):
        import_query = self.language.query("""
        (import_statement) @import
        (import_from_statement) @import_from
        """)
        imports = []
        captures = import_query.captures(node)
        for node, _ in captures:
            imports.append(node.text.decode('utf8'))
        return imports
    def analyze_function_complexity(self, node):
        branch_query = self.language.query("""
            (if_statement) @if
            (for_statement) @for
            (while_statement) @while
            (try_statement) @try
        """)
        branches = len(branch_query.captures(node))

        call_query = self.language.query("(call) @call")
        calls = len(call_query.captures(node))

        return {
            'branches': branches,
            'calls': calls,
            'complexity_score': branches + calls
        }

    def analyze_operations(self, node):
        operation_patterns = {
            'sorting': '(call function: (identifier) @sort)',
            'arithmetic': '(binary_operator) @math',
            'json': '(call function: (attribute object: (identifier)) @json)',
            'list_ops': '(call function: (identifier) @list)',
            'string_ops': '(call function: (identifier) @str)'
        }
        detected_ops = {}
        for op_type, pattern in operation_patterns.items():
            query = self.language.query(pattern)
            if query.captures(node):
                detected_ops[op_type] = True

        return detected_ops

    def generate_accurate_description(self, func_name, operations):
        descriptions = []
        if operations.get('sorting'):
            descriptions.append("performs sorting operations")
        if operations.get('arithmetic'):
            descriptions.append("performs mathematical calculations")
        if operations.get('json'):
            descriptions.append("handles JSON data transformation")
        if operations.get('list_ops'):
            descriptions.append("manipulates lists")
        if operations.get('string_ops'):
            descriptions.append("processes strings")

        return f"Function {func_name} " + " and ".join(descriptions) if descriptions else f"Function {func_name}"

    def analyze_file(self, file_path: str):
        with open(file_path, 'r') as f:
            code = f.read()
        tree = self.parser.parse(bytes(code, "utf8"))

        file_description_query = self.language.query("""
            (module (comment)+ @file.doc)
        """)

        function_query = self.language.query("""
            (function_definition 
                name: (identifier) @function.name
                body: (block 
                    (expression_statement 
                        (string) @function.doc))?
                body: (block) @function.body)
        """)

        file_doc = ""
        file_captures = file_description_query.captures(tree.root_node)
        if file_captures:
            file_doc = file_captures[0][0].text.decode('utf8').strip('# ')

        functions = []
        current_function = None
        captures = function_query.captures(tree.root_node)

        for node, capture_name in captures:
            if capture_name == 'function.name':
                current_function = {'name': node.text.decode('utf8')}
            elif capture_name == 'function.doc' and current_function:
                current_function['description'] = node.text.decode('utf8').strip('"""')
            elif capture_name == 'function.body' and current_function:
                current_function['complexity'] = self.analyze_function_complexity(node)
                current_function['operations'] = self.analyze_operations(node)
                current_function['description'] = self.generate_accurate_description(
                    current_function['name'],
                    current_function['operations']
                )
                functions.append(current_function)
                current_function = None

        return {
            'file': file_path,
            'description': file_doc,
            'imports': self.analyze_imports(tree.root_node),
            'functions': functions
        }

    def analyze_directory(self):
        results = []
        python_files = glob.glob(f"{self.directory}/**/*.py", recursive=True)
        for file in python_files:
            results.append(self.analyze_file(file))
        return results
    def generate_file_summary(self, file_data):
        num_functions = len(file_data['functions'])
        total_complexity = sum(f['complexity']['complexity_score'] for f in file_data['functions'])
        operations_used = set()
        for func in file_data['functions']:
            if 'operations' in func:
                operations_used.update(func['operations'].keys())

        return f"This file contains {num_functions} functions with total complexity of {total_complexity}. " \
               f"Main operations: {', '.join(operations_used)}."

    def generate_project_summary(self, results):
        total_files = len(results)
        total_functions = sum(len(r['functions']) for r in results)
        project_complexity = sum(sum(f['complexity']['complexity_score']
                                     for f in r['functions'])
                                 for r in results)

        return f"Project Overview:\n" \
           f"Total Files: {total_files}\n" \
           f"Total Functions: {total_functions}\n" \
           f"Overall Complexity: {project_complexity}"

if __name__ == "__main__":
    analyzer = CodeAnalyzer("data_analysis_project")
    results = analyzer.analyze_directory()

    # Project Summary
    print("\nProject Analysis:")
    print(analyzer.generate_project_summary(results))

    # Individual File Results
    for result in results:
        print(f"\nFile: {result['file']}")
        print(f"Summary: {analyzer.generate_file_summary(result)}")
        print(f"Purpose: {result.get('description', 'Data processing and analysis module')}")
        print("Imports:")
        for imp in result.get('imports', []):
            print(f"  {imp}")
        for func in result['functions']:
            print(f"\n  {func['name']}:")
            print(f"  Description: {func.get('description', 'Handles ' + func['name'].replace('_', ' '))}")
            print(f"  Complexity Score: {func['complexity']['complexity_score']}")
            print(f"  Branches: {func['complexity']['branches']}")
            print(f"  Function Calls: {func['complexity']['calls']}")
