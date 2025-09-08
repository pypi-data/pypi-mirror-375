"""
CausalLLM Web Interface

Streamlit-based web interface for interactive causal inference analysis.
"""
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from causallm import CausalLLM, __version__
from causallm.core.utils.logging import setup_package_logging


def setup_page():
    """Setup Streamlit page configuration."""
    st.set_page_config(
        page_title="CausalLLM Web Interface",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔬 CausalLLM - Causal Inference with LLMs")
    st.markdown(f"*Version {__version__} - Open Source Causal Inference powered by Large Language Models*")


def setup_sidebar():
    """Setup the sidebar with configuration options."""
    st.sidebar.header("Configuration")
    
    # LLM Configuration
    st.sidebar.subheader("LLM Settings")
    llm_provider = st.sidebar.selectbox("LLM Provider", ["openai", "anthropic"], index=0)
    llm_model = st.sidebar.selectbox(
        "Model", 
        ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet"] if llm_provider == "openai" else ["claude-3-sonnet", "claude-3-haiku"],
        index=0
    )
    
    # Method Configuration
    st.sidebar.subheader("Analysis Settings")
    method = st.sidebar.selectbox("Discovery Method", ["hybrid", "llm", "statistical"], index=0)
    domain = st.sidebar.selectbox(
        "Domain Context", 
        ["", "healthcare", "marketing", "education", "insurance", "experimentation"],
        index=0
    )
    
    # Logging
    verbose = st.sidebar.checkbox("Verbose Logging", False)
    
    return {
        'llm_provider': llm_provider,
        'llm_model': llm_model,
        'method': method,
        'domain': domain,
        'verbose': verbose
    }


def load_sample_data():
    """Load or generate sample datasets."""
    sample_datasets = {
        "Healthcare Example": {
            "description": "Patient treatment outcomes dataset",
            "data": pd.DataFrame({
                'age': [25, 35, 45, 55, 65, 30, 40, 50, 60, 28],
                'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F'],
                'treatment': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                'severity': [2, 3, 4, 3, 5, 2, 4, 3, 5, 2],
                'outcome': [8, 5, 9, 7, 3, 8, 4, 9, 2, 7]
            })
        },
        "Marketing Example": {
            "description": "Marketing campaign effectiveness",
            "data": pd.DataFrame({
                'age': [22, 35, 45, 55, 65, 30, 40, 50, 60, 28],
                'income': [30000, 50000, 70000, 80000, 60000, 45000, 65000, 75000, 55000, 40000],
                'campaign_exposure': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1],
                'previous_purchases': [2, 5, 3, 7, 4, 1, 6, 8, 2, 3],
                'conversion': [1, 0, 1, 1, 0, 1, 0, 1, 0, 1]
            })
        }
    }
    return sample_datasets


def data_upload_section():
    """Handle data upload and preview."""
    st.header("📊 Data Input")
    
    data_source = st.radio("Choose data source:", ["Upload File", "Use Sample Data", "Manual Entry"])
    
    data = None
    
    if data_source == "Upload File":
        uploaded_file = st.file_uploader("Upload CSV or JSON file", type=['csv', 'json'])
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    data = pd.read_json(uploaded_file)
                st.success(f"Loaded {data.shape[0]} rows, {data.shape[1]} columns")
            except Exception as e:
                st.error(f"Error loading file: {e}")
    
    elif data_source == "Use Sample Data":
        sample_datasets = load_sample_data()
        selected_sample = st.selectbox("Select sample dataset:", list(sample_datasets.keys()))
        if selected_sample:
            data = sample_datasets[selected_sample]["data"]
            st.info(sample_datasets[selected_sample]["description"])
    
    elif data_source == "Manual Entry":
        st.info("Enter data manually (JSON format):")
        manual_data = st.text_area("Data (JSON format)", height=200)
        if manual_data:
            try:
                data_dict = json.loads(manual_data)
                data = pd.DataFrame(data_dict)
            except Exception as e:
                st.error(f"Error parsing JSON: {e}")
    
    if data is not None:
        st.subheader("Data Preview")
        st.dataframe(data.head(10))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows", data.shape[0])
        with col2:
            st.metric("Columns", data.shape[1])
    
    return data


def causal_discovery_section(data: pd.DataFrame, config: Dict[str, Any]):
    """Causal discovery analysis section."""
    st.header("🔍 Causal Discovery")
    
    if data is None:
        st.warning("Please upload data first")
        return
    
    # Variable selection
    variables = st.multiselect("Select variables for analysis:", data.columns.tolist())
    
    if not variables:
        st.info("Please select variables to analyze")
        return
    
    # Additional options
    col1, col2 = st.columns(2)
    with col1:
        significance_level = st.slider("Significance Level", 0.01, 0.10, 0.05, 0.01)
    with col2:
        max_conditioning_set_size = st.slider("Max Conditioning Set Size", 1, 5, 3)
    
    # Run analysis
    if st.button("Run Causal Discovery", type="primary"):
        with st.spinner("Discovering causal relationships..."):
            try:
                causal_llm = CausalLLM(method=config['method'])
                
                # Run discovery (async wrapper)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    causal_llm.discover_causal_relationships(
                        data=data,
                        variables=variables,
                        domain_context=config['domain']
                    )
                )
                loop.close()
                
                # Display results
                st.success("Analysis completed!")
                
                # Results tabs
                tab1, tab2, tab3 = st.tabs(["Graph", "Relationships", "Statistics"])
                
                with tab1:
                    st.subheader("Causal Graph")
                    if hasattr(results, 'graph') and results.graph:
                        # Create network visualization
                        fig = create_causal_graph_viz(results.graph, variables)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Graph visualization not available")
                
                with tab2:
                    st.subheader("Discovered Relationships")
                    if hasattr(results, 'relationships'):
                        for rel in results.relationships:
                            st.write(f"• {rel}")
                    else:
                        st.write("Relationships information not available")
                
                with tab3:
                    st.subheader("Statistical Summary")
                    st.json(results if isinstance(results, dict) else {"results": str(results)})
                
            except Exception as e:
                st.error(f"Error during analysis: {e}")


def causal_effect_section(data: pd.DataFrame, config: Dict[str, Any]):
    """Causal effect estimation section."""
    st.header("⚡ Causal Effect Estimation")
    
    if data is None:
        st.warning("Please upload data first")
        return
    
    # Variable selection
    col1, col2 = st.columns(2)
    with col1:
        treatment = st.selectbox("Treatment Variable:", [""] + list(data.columns))
    with col2:
        outcome = st.selectbox("Outcome Variable:", [""] + list(data.columns))
    
    if not treatment or not outcome:
        st.info("Please select treatment and outcome variables")
        return
    
    # Confounders
    available_confounders = [col for col in data.columns if col not in [treatment, outcome]]
    confounders = st.multiselect("Confounding Variables:", available_confounders)
    
    # Method selection
    estimation_method = st.selectbox("Estimation Method:", ["backdoor", "iv", "regression_discontinuity"])
    
    # Run analysis
    if st.button("Estimate Causal Effect", type="primary"):
        with st.spinner("Estimating causal effect..."):
            try:
                causal_llm = CausalLLM()
                
                # Run effect estimation
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(
                    causal_llm.estimate_causal_effect(
                        data=data,
                        treatment=treatment,
                        outcome=outcome,
                        confounders=confounders,
                        method=estimation_method
                    )
                )
                loop.close()
                
                # Display results
                st.success("Effect estimation completed!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Estimated Effect", f"{results.get('effect', 'N/A')}")
                with col2:
                    st.metric("Confidence Interval", f"{results.get('confidence_interval', 'N/A')}")
                
                st.subheader("Detailed Results")
                st.json(results)
                
            except Exception as e:
                st.error(f"Error during effect estimation: {e}")


def counterfactual_section(data: pd.DataFrame, config: Dict[str, Any]):
    """Counterfactual analysis section."""
    st.header("🔮 Counterfactual Analysis")
    
    if data is None:
        st.warning("Please upload data first")
        return
    
    # Intervention specification
    st.subheader("Specify Intervention")
    intervention_var = st.selectbox("Variable to intervene on:", data.columns)
    
    if intervention_var:
        var_type = data[intervention_var].dtype
        if pd.api.types.is_numeric_dtype(var_type):
            intervention_value = st.number_input(f"Set {intervention_var} to:", value=float(data[intervention_var].mean()))
        else:
            unique_values = data[intervention_var].unique()
            intervention_value = st.selectbox(f"Set {intervention_var} to:", unique_values)
        
        num_samples = st.slider("Number of counterfactual samples:", 10, 1000, 100)
        
        if st.button("Generate Counterfactuals", type="primary"):
            with st.spinner("Generating counterfactual scenarios..."):
                try:
                    causal_llm = CausalLLM()
                    
                    intervention = {intervention_var: intervention_value}
                    
                    # Run counterfactual analysis
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    results = loop.run_until_complete(
                        causal_llm.generate_counterfactuals(
                            data=data,
                            intervention=intervention,
                            num_samples=num_samples
                        )
                    )
                    loop.close()
                    
                    # Display results
                    st.success("Counterfactual analysis completed!")
                    
                    if isinstance(results, dict) and 'counterfactuals' in results:
                        counterfactuals_df = pd.DataFrame(results['counterfactuals'])
                        st.dataframe(counterfactuals_df.head(20))
                        
                        # Summary statistics
                        st.subheader("Summary Statistics")
                        st.write(counterfactuals_df.describe())
                    else:
                        st.json(results)
                        
                except Exception as e:
                    st.error(f"Error during counterfactual analysis: {e}")


def create_causal_graph_viz(graph_data, variables):
    """Create a visualization of the causal graph."""
    import networkx as nx
    
    # Create networkx graph
    G = nx.DiGraph()
    G.add_nodes_from(variables)
    
    # Add edges if graph_data contains edge information
    if isinstance(graph_data, dict) and 'edges' in graph_data:
        G.add_edges_from(graph_data['edges'])
    
    # Create layout
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Create plotly figure
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='gray'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        hoverinfo='text',
        marker=dict(size=30, color='lightblue', line=dict(width=2, color='black'))
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       title="Causal Graph",
                       titlefont_size=16,
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=20,l=5,r=5,t=40),
                       annotations=[ dict(
                           text="Causal relationships discovered from data",
                           showarrow=False,
                           xref="paper", yref="paper",
                           x=0.005, y=-0.002,
                           xanchor="left", yanchor="bottom",
                           font=dict(color="gray", size=12)
                       )],
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                   ))
    
    return fig


def documentation_section():
    """Documentation and examples section."""
    st.header("📖 Documentation & Examples")
    
    tab1, tab2, tab3 = st.tabs(["Getting Started", "API Reference", "Examples"])
    
    with tab1:
        st.markdown("""
        ## Welcome to CausalLLM!
        
        CausalLLM is an open-source library that combines Large Language Models with statistical methods 
        for causal inference. Here's how to get started:
        
        ### 1. Upload Your Data
        - Use the **Data Input** section to upload CSV/JSON files
        - Or try our sample datasets to get familiar with the interface
        
        ### 2. Discover Causal Relationships
        - Select variables you want to analyze
        - Choose appropriate domain context (healthcare, marketing, etc.)
        - Run causal discovery to find relationships in your data
        
        ### 3. Estimate Causal Effects
        - Specify treatment and outcome variables
        - Control for confounders
        - Get quantified causal effects
        
        ### 4. Explore Counterfactuals
        - Generate "what-if" scenarios
        - Understand potential outcomes under different interventions
        """)
    
    with tab2:
        st.markdown("""
        ## API Reference
        
        ### Main Classes
        - `CausalLLM`: Main interface for causal inference
        - `CausalLLMCore`: Core causal inference engine
        - `DAGParser`: Parse and manipulate causal graphs
        - `DoOperatorSimulator`: Simulate interventions
        
        ### Key Methods
        ```python
        # Discovery
        await causallm.discover_causal_relationships(data, variables, domain_context)
        
        # Effect Estimation
        await causallm.estimate_causal_effect(data, treatment, outcome, confounders)
        
        # Counterfactuals
        await causallm.generate_counterfactuals(data, intervention)
        ```
        """)
    
    with tab3:
        st.markdown("""
        ## Examples
        
        ### Healthcare Analysis
        ```python
        import pandas as pd
        from causallm import CausalLLM
        
        # Load patient data
        data = pd.read_csv('patient_outcomes.csv')
        
        # Initialize CausalLLM
        causal_llm = CausalLLM()
        
        # Discover relationships
        results = await causal_llm.discover_causal_relationships(
            data=data,
            variables=['age', 'treatment', 'outcome'],
            domain_context='healthcare'
        )
        ```
        
        ### Marketing Attribution
        ```python
        # Estimate campaign effectiveness
        effect = await causal_llm.estimate_causal_effect(
            data=marketing_data,
            treatment='campaign_exposure',
            outcome='conversion',
            confounders=['age', 'income', 'previous_purchases']
        )
        ```
        """)


def main():
    """Main web application function."""
    setup_page()
    
    # Configuration sidebar
    config = setup_sidebar()
    
    if config['verbose']:
        setup_package_logging(level="DEBUG")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Data", "🔍 Discovery", "⚡ Effects", "🔮 Counterfactuals", "📖 Documentation"
    ])
    
    # Data upload and preview
    with tab1:
        data = data_upload_section()
    
    # Causal discovery
    with tab2:
        data = st.session_state.get('data', data)
        causal_discovery_section(data, config)
    
    # Effect estimation
    with tab3:
        data = st.session_state.get('data', data)
        causal_effect_section(data, config)
    
    # Counterfactual analysis
    with tab4:
        data = st.session_state.get('data', data)
        counterfactual_section(data, config)
    
    # Documentation
    with tab5:
        documentation_section()
    
    # Store data in session state
    if data is not None:
        st.session_state['data'] = data
    
    # Footer
    st.markdown("---")
    st.markdown(f"**CausalLLM v{__version__}** - Open Source Causal Inference | [GitHub](https://github.com/rdmurugan/causallm) | [Documentation](https://causallm.com/docs)")


def create_web_app(host="localhost", port=8080, debug=False):
    """Create and launch the web application."""
    import subprocess
    import sys
    
    # Check if streamlit is available
    try:
        import streamlit
    except ImportError:
        print("Streamlit not found. Install UI dependencies with:")
        print("pip install causallm[ui]")
        return
    
    # Launch streamlit app
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        __file__.replace('web.py', 'web.py'),
        "--server.address", host,
        "--server.port", str(port)
    ]
    
    if not debug:
        cmd.extend(["--logger.level", "error"])
    
    print(f"Launching CausalLLM web interface at http://{host}:{port}")
    subprocess.run(cmd)


if __name__ == "__main__":
    main()