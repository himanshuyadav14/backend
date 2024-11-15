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
    nodes: list
    edges: list

# Function to check if the graph is a DAG
def checkDAG(nodes: list, edges: list) -> bool:
    adj_list = {node['id']: [] for node in nodes}  # Construct adjacency list
    for edge in edges:
        adj_list[edge['source']].append(edge['target'])

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

    # Create an adjacency list for the graph
    adj_list = {node: [] for node in nodes}
    for edge in edges:
        src, dest = edge
        adj_list[src].append(dest)

    # Initialize visited arrays
    visited = {node: False for node in nodes}
    rec_stack = {node: False for node in nodes}  # To keep track of nodes in the current recursion stack

    def dfs(node: str) -> bool:
        # If the node is in the current recursion stack, a cycle is detected
        if rec_stack[node]:
            return True
        # If the node is already visited, no need to visit again
        if visited[node]:
            return False
        
        # Mark the node as visited and part of the recursion stack
        visited[node] = True
        rec_stack[node] = True
        
        # Recurse for all the neighbors
        for neighbor in adj_list[node]:
            if dfs(neighbor):
                return True
        
        rec_stack[node] = False
        return False

    for node in nodes:
        if not visited[node]: 
            if dfs(node):
                return False

    return True 

# Root route
@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

# Route to parse the pipeline and check if it's a DAG
@app.post('/pipelines/parse')
async def parse_pipeline(pipeline: Pipeline):

    print("Received nodes:", pipeline.nodes)
    print("Received edges:", pipeline.edges)

    nodes = pipeline.nodes
    edges = pipeline.edges

    num_nodes = len(nodes)
    num_edges = len(edges)

    is_dag = checkDAG(nodes, edges)

    return {'num_nodes': num_nodes, 'num_edges': num_edges, 'is_dag': is_dag}
