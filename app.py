"""
CogDB Graph Explorer - Interactive Graph Database Demo with Streamlit
Showcase CogDB's graph capabilities: add triples, query, traverse, visualize
"""

import streamlit as st
import streamlit.components.v1 as components
import uuid
from cog.torque import Graph

# --- Config ---
GRAPH_NAME = "cogdb_demo"

# --- Example Datasets ---
EXAMPLES = {
    "Social Network": [
        ("alice", "follows", "bob"),
        ("bob", "follows", "charlie"),
        ("charlie", "follows", "alice"),
        ("alice", "likes", "python"),
        ("bob", "likes", "javascript"),
        ("charlie", "likes", "python"),
        ("alice", "works_at", "startup"),
        ("bob", "works_at", "bigcorp"),
        ("charlie", "works_at", "startup"),
    ],
    "Movies": [
        ("inception", "directed_by", "christopher_nolan"),
        ("interstellar", "directed_by", "christopher_nolan"),
        ("the_dark_knight", "directed_by", "christopher_nolan"),
        ("inception", "stars", "leonardo_dicaprio"),
        ("inception", "genre", "scifi"),
        ("interstellar", "genre", "scifi"),
        ("the_dark_knight", "genre", "action"),
        ("leonardo_dicaprio", "born_in", "los_angeles"),
        ("christopher_nolan", "born_in", "london"),
    ],
    "Knowledge Base": [
        ("python", "is_a", "programming_language"),
        ("javascript", "is_a", "programming_language"),
        ("python", "used_for", "data_science"),
        ("python", "used_for", "web_development"),
        ("javascript", "used_for", "web_development"),
        ("streamlit", "written_in", "python"),
        ("cogdb", "written_in", "python"),
        ("cogdb", "is_a", "graph_database"),
        ("streamlit", "is_a", "web_framework"),
    ],
}

# --- Initialize ---
st.set_page_config(page_title="CogDB Explorer", page_icon="🔗", layout="wide")
g = Graph(GRAPH_NAME)

# --- Sidebar ---
with st.sidebar:
    st.title("🔗 CogDB Explorer")
    st.caption("Interactive Graph Database Demo")
    
    st.divider()
    
    # Stats
    st.subheader("📊 Graph Stats")
    try:
        nodes = g.scan(10000)
        edges = g.scan(10000, 'e')
        node_count = len(nodes.get("result", []))
        edge_count = len(edges.get("result", []))
    except:
        node_count = 0
        edge_count = 0
    
    col1, col2 = st.columns(2)
    col1.metric("Nodes", node_count)
    col2.metric("Edges", edge_count)
    
    st.divider()
    
    # Load Examples
    st.subheader("📦 Load Example")
    for name, triples in EXAMPLES.items():
        if st.button(f"Load {name}", use_container_width=True, key=f"load_{name}"):
            for s, p, o in triples:
                g.put(s, p, o)
            st.success(f"Added {len(triples)} triples!")
            st.rerun()
    
    st.divider()
    
    # Clear Graph
    if st.button("🗑️ Clear Graph", use_container_width=True, type="secondary"):
        g.close()
        import shutil, os
        graph_path = f"/tmp/cog-test/{GRAPH_NAME}"
        if os.path.exists(graph_path):
            shutil.rmtree(graph_path)
        st.rerun()

# --- Main Content ---
st.title("🔗 CogDB Graph Explorer")
st.caption("An embedded graph database for Python — no setup required!")

# Create tabs for different features
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Data", "🔍 Query", "🗺️ Traverse", "📊 Visualize"])

# --- Tab 1: Add Data ---
with tab1:
    st.header("Add Triples")
    st.markdown("A **triple** is the fundamental unit: `(subject, predicate, object)`")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        subject = st.text_input("Subject", placeholder="alice", key="add_subject")
    with col2:
        predicate = st.text_input("Predicate", placeholder="follows", key="add_predicate")
    with col3:
        obj = st.text_input("Object", placeholder="bob", key="add_object")
    
    if st.button("Add Triple", type="primary"):
        if subject and predicate and obj:
            g.put(subject.lower().strip(), predicate.lower().strip(), obj.lower().strip())
            st.success(f"✓ Added: `{subject}` → `{predicate}` → `{obj}`")
            st.rerun()
        else:
            st.warning("Please fill in all three fields.")
    
    st.divider()
    
    # Show recent data
    st.subheader("Current Data")
    try:
        nodes = g.scan(20)
        if nodes.get("result"):
            node_list = [n["id"] for n in nodes["result"]]
            st.write("**Nodes:**", ", ".join(f"`{n}`" for n in node_list[:15]))
            if len(node_list) > 15:
                st.caption(f"... and {len(node_list) - 15} more")
        else:
            st.info("No data yet. Add some triples or load an example from the sidebar!")
    except:
        st.info("No data yet. Add some triples or load an example from the sidebar!")

# --- Tab 2: Query ---
with tab2:
    st.header("Query the Graph")
    
    query_type = st.selectbox("Query Type", [
        "Get all connections from a node",
        "Get all nodes connected TO a node", 
        "Filter nodes by predicate value",
        "Find paths with specific predicate"
    ])
    
    if query_type == "Get all connections from a node":
        st.code('g.v("node").out().all()', language="python")
        node = st.text_input("Node name:", placeholder="alice", key="q1_node")
        if st.button("Run Query", key="q1_run") and node:
            try:
                result = g.v(node.lower().strip()).out().all()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif query_type == "Get all nodes connected TO a node":
        st.code('g.v("node").inc().all()', language="python")
        node = st.text_input("Node name:", placeholder="bob", key="q2_node")
        if st.button("Run Query", key="q2_run") and node:
            try:
                result = g.v(node.lower().strip()).inc().all()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif query_type == "Filter nodes by predicate value":
        st.code('g.v().has("predicate", "value").all()', language="python")
        col1, col2 = st.columns(2)
        pred = col1.text_input("Predicate:", placeholder="likes", key="q3_pred")
        val = col2.text_input("Value:", placeholder="python", key="q3_val")
        if st.button("Run Query", key="q3_run") and pred and val:
            try:
                result = g.v().has(pred.lower().strip(), val.lower().strip()).all()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif query_type == "Find paths with specific predicate":
        st.code('g.v("node").out("predicate").all()', language="python")
        col1, col2 = st.columns(2)
        node = col1.text_input("Start node:", placeholder="alice", key="q4_node")
        pred = col2.text_input("Predicate:", placeholder="follows", key="q4_pred")
        if st.button("Run Query", key="q4_run") and node:
            try:
                if pred:
                    result = g.v(node.lower().strip()).out(pred.lower().strip()).all()
                else:
                    result = g.v(node.lower().strip()).out().all()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")

# --- Tab 3: Traverse ---
with tab3:
    st.header("Graph Traversal")
    st.markdown("Chain multiple operations to traverse the graph!")
    
    st.subheader("Multi-hop Traversal")
    st.code('g.v("node").out("pred1").out("pred2").all()', language="python")
    
    start_node = st.text_input("Start node:", placeholder="alice", key="trav_node")
    
    col1, col2 = st.columns(2)
    hop1 = col1.text_input("First hop (predicate):", placeholder="follows", key="trav_hop1")
    hop2 = col2.text_input("Second hop (predicate):", placeholder="follows", key="trav_hop2")
    
    if st.button("Traverse", key="trav_run") and start_node:
        try:
            query = g.v(start_node.lower().strip())
            if hop1:
                query = query.out(hop1.lower().strip())
            if hop2:
                query = query.out(hop2.lower().strip())
            result = query.all()
            st.json(result)
        except Exception as e:
            st.error(f"Error: {e}")
    
    st.divider()
    
    st.subheader("Advanced Queries")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Unique Results**")
        st.code('g.v().out("follows").unique().all()')
        if st.button("Run Unique", key="adv_unique"):
            try:
                result = g.v().out("follows").unique().all()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        st.markdown("**Limit Results**")
        st.code('g.v().limit(5).all()')
        if st.button("Run Limit", key="adv_limit"):
            try:
                result = g.v().limit(5).all()
                st.json(result)
            except Exception as e:
                st.error(f"Error: {e}")

# --- Tab 4: Visualize ---
with tab4:
    st.header("Graph Visualization")
    
    try:
        nodes = g.scan(1000)
        if nodes.get("result") and len(nodes["result"]) > 0:
            view_name = f"cogdb_view_{uuid.uuid4().hex[:8]}"
            view = g.v().tag("from").out().tag("to").view(view_name)
            components.html(view.html, height=600, scrolling=True)
        else:
            st.info("Add some data to see the visualization. Try loading an example from the sidebar!")
    except Exception as e:
        st.info("Add some data to see the visualization. Try loading an example from the sidebar!")

# --- Footer ---
st.divider()
st.caption("Built with [CogDB](https://github.com/arun1729/cog) • [Streamlit](https://streamlit.io)")
