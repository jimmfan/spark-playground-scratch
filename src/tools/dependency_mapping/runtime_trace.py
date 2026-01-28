# runtime_trace.py
import json

call_stack = []
call_log = []

def tracer(func):
    def wrapper(*args, **kwargs):
        caller = call_stack[-1] if call_stack else 'START'
        call_log.append((caller, func.__name__))
        call_stack.append(func.__name__)
        result = func(*args, **kwargs)
        call_stack.pop()
        return result
    return wrapper

def save_trace(filename="call_trace.json"):
    with open(filename, "w") as f:
        json.dump(call_log, f)


### Example usage to export metadata
from runtime_trace import tracer, save_trace

@tracer
def main():
    load_data()
    transform()

@tracer
def load_data(): pass

@tracer
def transform():
    clean()
    enrich()

@tracer
def clean(): pass

@tracer
def enrich(): pass

main()
save_trace()  # <- Save after execution

### Python 3.12
# visualize_trace.py
import json
import networkx as nx
import matplotlib.pyplot as plt

def visualize_trace(json_file="call_trace.json", output_file="call_graph.png"):
    with open(json_file) as f:
        calls = json.load(f)

    G = nx.DiGraph()
    for caller, callee in calls:
        G.add_edge(caller, callee)

    nx.draw(G, with_labels=True, node_size=2000, font_size=10)
    plt.savefig(output_file)
    plt.show()

visualize_trace()
