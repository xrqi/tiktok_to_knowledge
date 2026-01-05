import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from typing import List, Dict, Any, Optional
import json
from io import BytesIO
import base64

# Set matplotlib backend to avoid GUI issues in some environments
matplotlib.use('Agg')  # Use non-interactive backend

class MindMapGenerator:
    """Mind Map Generator - Creates visual representations of knowledge structure"""
    
    def __init__(self):
        self.graph = None
        
    def create_mind_map_from_knowledge(self, knowledge_points: List[Dict[str, Any]], 
                                     title: str = "Knowledge Mind Map") -> Optional[str]:
        """Create a mind map from knowledge points and return as base64 image string"""
        try:
            # Create a directed graph
            self.graph = nx.DiGraph()
            
            # Add central node for the main topic
            self.graph.add_node(title, type='central', level=0)
            
            # Add nodes for each knowledge point
            for i, kp in enumerate(knowledge_points):
                node_id = f"kp_{i}"
                node_label = kp.get('title', '')[:30]  # Limit label length
                self.graph.add_node(node_id, 
                                  title=kp.get('title', ''),
                                  content=kp.get('content', '')[:100],  # Limit content
                                  category=kp.get('category', ''),
                                  importance=kp.get('importance', 3),
                                  type='knowledge',
                                  level=1)
                
                # Connect knowledge point to central topic
                self.graph.add_edge(title, node_id)
                
                # Add sub-nodes for tags
                tags = kp.get('tags', [])
                for j, tag in enumerate(tags):
                    tag_node_id = f"tag_{i}_{j}"
                    self.graph.add_node(tag_node_id, 
                                      label=tag,
                                      type='tag',
                                      level=2)
                    self.graph.add_edge(node_id, tag_node_id)
            
            # Generate the visualization
            return self._render_mind_map(title)
            
        except Exception as e:
            print(f"Error creating mind map: {e}")
            return None
    
    def create_mind_map_from_text(self, text: str, title: str = "Text Mind Map") -> Optional[str]:
        """Create a mind map from text content"""
        try:
            # This is a simplified version - in a real implementation, 
            # you'd use NLP to extract key concepts and relationships
            import re
            
            # Extract potential concepts (this is a basic implementation)
            sentences = re.split(r'[.!?]+', text)
            concepts = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10:  # Only consider meaningful sentences
                    # Extract key phrases (simplified approach)
                    words = sentence.split()
                    if len(words) > 5:
                        concepts.append(sentence[:50])  # Take first 50 chars
            
            # Limit to top concepts
            concepts = concepts[:10]
            
            # Create graph
            self.graph = nx.DiGraph()
            self.graph.add_node(title, type='central', level=0)
            
            for i, concept in enumerate(concepts):
                node_id = f"concept_{i}"
                self.graph.add_node(node_id, 
                                  label=concept[:30],
                                  content=concept,
                                  type='concept',
                                  level=1)
                self.graph.add_edge(title, node_id)
            
            return self._render_mind_map(title)
            
        except Exception as e:
            print(f"Error creating mind map from text: {e}")
            return None
    
    def _render_mind_map(self, title: str) -> Optional[str]:
        """Render the mind map and return as base64 string"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Use spring layout for a more organic mind map feel
            pos = nx.spring_layout(self.graph, k=3, iterations=50)
            
            # Separate nodes by type for different styling
            central_nodes = [n for n, attr in self.graph.nodes(data=True) 
                           if attr.get('type') == 'central']
            knowledge_nodes = [n for n, attr in self.graph.nodes(data=True) 
                             if attr.get('type') == 'knowledge']
            concept_nodes = [n for n, attr in self.graph.nodes(data=True) 
                           if attr.get('type') == 'concept']
            tag_nodes = [n for n, attr in self.graph.nodes(data=True) 
                        if attr.get('type') == 'tag']
            
            # Draw edges
            nx.draw_networkx_edges(self.graph, pos, alpha=0.5, edge_color='gray')
            
            # Draw different types of nodes with different colors
            if central_nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=central_nodes, 
                                     node_color='red', node_size=2000, alpha=0.8)
            if knowledge_nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=knowledge_nodes, 
                                     node_color='lightblue', node_size=1000, alpha=0.8)
            if concept_nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=concept_nodes, 
                                     node_color='lightgreen', node_size=800, alpha=0.8)
            if tag_nodes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=tag_nodes, 
                                     node_color='yellow', node_size=600, alpha=0.8)
            
            # Add labels
            labels = {}
            for node, attrs in self.graph.nodes(data=True):
                if attrs.get('type') == 'central':
                    labels[node] = attrs.get('title', node)
                elif 'title' in attrs:
                    labels[node] = attrs['title'][:20] + "..." if len(attrs['title']) > 20 else attrs['title']
                elif 'label' in attrs:
                    labels[node] = attrs['label']
                else:
                    labels[node] = node
            
            nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
            
            plt.title(title)
            plt.axis('off')  # Turn off axis
            
            # Save to bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            
            # Convert to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()  # Close the figure to free memory
            
            return image_base64
            
        except Exception as e:
            print(f"Error rendering mind map: {e}")
            return None

# Example usage
if __name__ == "__main__":
    # Example knowledge points
    knowledge_points = [
        {
            "title": "Artificial Intelligence",
            "content": "AI is a branch of computer science that aims to create software or machines that exhibit human-like intelligence.",
            "category": "Technology",
            "tags": ["AI", "Machine Learning", "Computer Science"],
            "importance": 5
        },
        {
            "title": "Machine Learning",
            "content": "Machine learning is a method of data analysis that automates analytical model building.",
            "category": "Technology", 
            "tags": ["ML", "Algorithms", "Data Science"],
            "importance": 4
        },
        {
            "title": "Neural Networks",
            "content": "Neural networks are a series of algorithms that mimic the operations of a human brain to recognize relationships between vast amounts of data.",
            "category": "Technology",
            "tags": ["Deep Learning", "AI", "Algorithms"],
            "importance": 4
        }
    ]
    
    generator = MindMapGenerator()
    mind_map_base64 = generator.create_mind_map_from_knowledge(knowledge_points, "AI Concepts Mind Map")
    
    if mind_map_base64:
        print("Mind map generated successfully!")
        print(f"Base64 length: {len(mind_map_base64)}")
    else:
        print("Failed to generate mind map")