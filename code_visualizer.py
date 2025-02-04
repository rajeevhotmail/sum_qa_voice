import networkx as nx
import plotly.graph_objects as go
from typing import Dict, Set
import matplotlib.pyplot as plt

class DependencyVisualizer:
    def __init__(self):
        self.graph = nx.DiGraph()

    def calculate_node_colors(self, dependency_data):
        colors = []
        for node in self.graph.nodes():
            if node in dependency_data:
                deps = dependency_data[node]
                complexity = len(deps.callees) + len(deps.variables_used)
                if complexity > 8:
                    colors.append('red')        # High complexity
                elif complexity > 4:
                    colors.append('yellow')     # Medium complexity
                else:
                    colors.append('lightgreen') # Low complexity
            else:
                colors.append('gray')  # Built-in functions
        return colors

    def save_multiple_formats(self):
        # Save interactive HTML
        self.generate_interactive_plot()

        # Save static PNG
        plt.figure(figsize=(12, 8))
        nx.draw(self.graph, with_labels=True, node_color='lightblue',
                node_size=1500, arrowsize=20, font_size=10)
        plt.savefig('dependency_graph.png')

        # Save SVG for high-quality prints
        plt.savefig('dependency_graph.svg', format='svg')


    def create_visualization(self, dependency_data):
        self.dependency_data = dependency_data  # Store the data as class attribute
        self.build_graph(dependency_data)
        self.save_multiple_formats()

    def build_graph(self, dependency_data):
        for func, deps in dependency_data.items():
            self.graph.add_node(func)
            for callee in deps.callees:
                self.graph.add_edge(func, callee)

    def create_edge_traces(self, pos):
        edge_x = []
        edge_y = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        return edge_x, edge_y

    def create_node_traces(self, pos):
        node_x = []
        node_y = []
        for node in self.graph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
        return node_x, node_y


    def generate_interactive_plot(self):
        pos = nx.spring_layout(self.graph)
        node_colors = self.calculate_node_colors(self.dependency_data)

        edge_x, edge_y = self.create_edge_traces(pos)
        node_x, node_y = self.create_node_traces(pos)

        fig = go.Figure(
            data=[
                go.Scatter(x=edge_x, y=edge_y,
                          line=dict(width=0.5, color='#888'),
                          hoverinfo='none',
                        mode='lines'),
                go.Scatter(x=node_x, y=node_y,
                          mode='markers+text',
                          marker=dict(color=node_colors, size=20),
                        text=list(self.graph.nodes()),
                        textposition='bottom center')
            ],
            layout=go.Layout(
                title='Code Dependency Map with Complexity Indicators',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40)
            )
        )

        fig.write_html("dependency_graph.html")


