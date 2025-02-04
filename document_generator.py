class DocumentationGenerator:
    def __init__(self):
        self.doc_file = "project_documentation.md"

    def extract_features(self, analysis_results, dependency_data):
        features = set()

        # Extract from function names and descriptions
        for result in analysis_results:
            for func in result['functions']:
                if 'order' in func['name']:
                    features.add('Order Processing System')
                if 'inventory' in func['name']:
                    features.add('Inventory Management')
                if 'calculate' in func['name'] or 'total' in func['name']:
                    features.add('Financial Calculations')

        return sorted(list(features))


    def generate_docs(self, analysis_results, dependency_data, project_dir):
        with open(self.doc_file, "w") as f:
            # Project Overview
            f.write("# Project Documentation\n\n")
            f.write("## Overview\n")
            f.write(f"Analysis of project in: {project_dir}\n\n")

            # Function Documentation
            f.write("## Functions\n\n")
            for result in analysis_results:
                for func in result['functions']:
                    f.write(f"### {func['name']}\n")
                    f.write(f"{func['description']}\n\n")

            # Code Analysis Details
            f.write("## Code Analysis\n\n")
            for func_name, deps in dependency_data.items():
                f.write(f"### Function: {func_name}\n")
                complexity = len(deps.callees) + len(deps.variables_used)
                risk_level = "🟢 Green" if complexity <= 4 else "🟡 Yellow" if complexity <= 8 else "🔴 Red"
                f.write(f"**Complexity Score:** {complexity}\n")
                f.write(f"**Dependencies:** {', '.join(deps.callees)}\n")
                f.write(f"**Risk Level:** {risk_level}\n\n")
            # Contributing Guidelines
            f.write("## Contributing\n")
            f.write("Guidelines for contributing to this project\n\n")

            # License
            f.write("## License\n")
            f.write("MIT License\n")
