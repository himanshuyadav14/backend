from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Create the FastAPI app instance
app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:3000", 
]

# Add CORSMiddleware to handle cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

class Pipeline(BaseModel):
    nodes: List[dict]
    edges: List[dict]

# Function to check if the graph is a DAG
# def checkDAG(nodes: List[dict], edges: List[dict]) -> bool:
#     adj_list = {node['id']: [] for node in nodes}  # Construct adjacency list
#     for edge in edges:
#         adj_list[edge['source']].append(edge['target'])

#     visited = {node['id']: False for node in nodes}
#     rec_stack = {node['id']: False for node in nodes}

#     def dfs(node_id: str) -> bool:
#         if rec_stack[node_id]:  # Cycle detected
#             return True
#         if visited[node_id]:  # Already processed
#             return False

#         visited[node_id] = True
#         rec_stack[node_id] = True

#         # Recurse through all neighbors (target nodes)
#         for neighbor in adj_list[node_id]:
#             if dfs(neighbor):
#                 return True

#         rec_stack[node_id] = False
#         return False

#     # Check for cycles starting from each node
#     for node in nodes:
#         if not visited[node['id']]:  # Only start DFS if not visited
#             if dfs(node['id']):
#                 return False  # Cycle found

#     return True  # No cycle found, it's a DAG

def checkDAG(nodes: List[dict], edges: List[dict]) -> bool:
    # Construct adjacency list
    adj_list = {node['id']: [] for node in nodes}
    
    # Add edges to adjacency list
    for edge in edges:
        source = edge.get('source')
        target = edge.get('target')
        if source not in adj_list:
            print(f"Warning: Source node {source} is not in the nodes list.")
            continue  # Skip the edge
        if target not in adj_list:
            print(f"Warning: Target node {target} is not in the nodes list.")
            continue  # Skip the edge
        adj_list[source].append(target)

    visited = {node['id']: False for node in nodes}
    rec_stack = {node['id']: False for node in nodes}

    def dfs(node_id: str) -> bool:
        if rec_stack[node_id]:  # Cycle detected
            return True
        if visited[node_id]:  # Already processed
            return False

        visited[node_id] = True
        rec_stack[node_id] = True

        # Recurse through all neighbors (target nodes)
        for neighbor in adj_list[node_id]:
            if dfs(neighbor):
                return True

        rec_stack[node_id] = False
        return False

    # Check for cycles starting from each node
    for node in nodes:
        if not visited[node['id']]:  # Only start DFS if not visited
            if dfs(node['id']):
                return False  # Cycle found

    return True  # No cycle found, it's a DAG

# Root route
@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

# Route to parse the pipeline and check if it's a DAG
@app.post('/pipelines/parse')
async def parse_pipeline(pipeline: Pipeline):

    nodes = pipeline.nodes
    edges = pipeline.edges

    num_nodes = len(nodes)
    num_edges = len(edges)

    is_dag = checkDAG(nodes, edges)

    return {'num_nodes': num_nodes, 'num_edges': num_edges, 'is_dag': is_dag}
