import streamlit as st
import ast
import networkx as nx
from pyvis.network import Network
import tempfile
import os

# ------------------------
# Build Control Flow Graph
# ------------------------
def build_cfg(code):
    tree = ast.parse(code)
    cfg = nx.DiGraph()
    prev_node = None

    for node in ast.walk(tree):
        if hasattr(node, 'lineno'):
            node_label = f"{type(node).__name__} (line {node.lineno})"
            cfg.add_node(node_label)
            if prev_node and prev_node != node_label:
                cfg.add_edge(prev_node, node_label)
            prev_node = node_label
    return cfg

# ------------------------
# Static Program Slicing
# ------------------------
def static_slice(code, variable):
    tree = ast.parse(code)
    lines_to_keep = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == variable:
                    lines_to_keep.add(node.lineno)
        elif isinstance(node, ast.Name) and node.id == variable:
            if hasattr(node, 'lineno'):
                lines_to_keep.add(node.lineno)

    sliced_code = "\n".join(
        line for i, line in enumerate(code.splitlines(), 1) if i in lines_to_keep
    )
    return sliced_code

# ------------------------
# Visualize CFG with PyVis
# ------------------------
def visualize_cfg(cfg):
    net = Network(height="500px", width="100%", directed=True)
    net.from_nx(cfg)
    temp_dir = tempfile.mkdtemp()
    html_path = os.path.join(temp_dir, "cfg.html")
    net.save_graph(html_path)
    return html_path

# ------------------------
# Streamlit UI
# ------------------------
st.set_page_config(page_title="Program Slicing Tool", layout="wide")
st.title("🔍 Program Slicing Tool")
st.write("Upload a Python program, choose a variable, and see the slice and Control Flow Graph.")

uploaded_file = st.file_uploader("Upload Python file", type=["py"])
if uploaded_file:
    code = uploaded_file.read().decode("utf-8")
    st.subheader("📜 Original Code")
    st.code(code, language="python")

    variable = st.text_input("Enter variable name for slicing:")
    if st.button("Perform Static Slice") and variable:
        sliced = static_slice(code, variable)
        st.subheader(f"✂️ Sliced Code for variable '{variable}'")
        st.code(sliced if sliced.strip() else "# No relevant lines found", language="python")

    if st.button("Show Control Flow Graph"):
        cfg = build_cfg(code)
        html_file = visualize_cfg(cfg)
        with open(html_file, "r", encoding="utf-8") as f:
            components_html = f.read()
        st.components.v1.html(components_html, height=550, scrolling=True)
