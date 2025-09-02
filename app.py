import random
import csv
from collections import Counter
import re
import pandas as pd
import streamlit as st
from tcg_utils import *
import time

# Custom CSS for professional styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Custom font for the entire app */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom title styling */
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: fadeInDown 1s ease-out;
    }
    
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        animation: fadeInUp 1s ease-out 0.3s both;
    }
    
    /* Card-like containers */
    .custom-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        animation: slideInUp 0.8s ease-out;
    }
    
    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        animation: scaleIn 0.6s ease-out;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.4);
    }
    
    div[data-testid="metric-container"] > div {
        color: white !important;
    }
    
    div[data-testid="metric-container"] label {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Success/Error messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px;
        border-left: 4px solid;
        animation: slideInRight 0.5s ease-out;
    }
    
    /* Expandable sections */
    .streamlit-expanderHeader {
        border-radius: 8px;
        background: #f8fafc;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: #f1f5f9;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes scaleIn {
        from {
            opacity: 0;
            transform: scale(0.9);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.05);
        }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .custom-card {
            padding: 1.5rem;
        }
    }
    
    /* Code blocks */
    .stCode {
        border-radius: 8px;
        background: #1e293b;
        border: 1px solid #334155;
    }
    
    /* Custom status indicators */
    .status-good {
        color: #10b981;
        font-weight: 600;
    }
    
    .status-warning {
        color: #f59e0b;
        font-weight: 600;
    }
    
    .status-error {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Card composition styling */
    .card-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 1rem;
        background: #f8fafc;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .card-item:hover {
        background: #e2e8f0;
        transform: translateX(5px);
    }
    
    /* Attacker identification */
    .attacker-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .attacker-item:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        transform: translateX(5px);
    }
    </style>
    """, unsafe_allow_html=True)

def create_animated_header():
    st.markdown("""
    <div class="main-title" style="display: flex; align-items: center; justify-content: center;">
        <img src=".streamlit/static/Pokeball.png" alt="" style="height: 2.5rem; margin-right: 1rem; vertical-align: middle;" />
        Pokemon TCG Pocket Deck Simulator
    </div>
    <div class="subtitle">
        Analyze your deck's consistency and opening hand potential with advanced simulation
    </div>
    """, unsafe_allow_html=True)

def create_metrics_section(brick_rate, attacker_rate, key_card_rate):
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric(
            "🧱 Brick Rate", 
            f"{brick_rate:.1f}%",
            help="Percentage of games that resulted in unplayable hands"
        )
    
    with col_b:
        st.metric(
            "⚔️ No Attacker Rate", 
            f"{attacker_rate:.1f}%",
            help="Percentage of games with insufficient attackers developed"
        )
    
    with col_c:
        st.metric(
            "🔑 Key Cards Stuck Rate", 
            f"{key_card_rate:.1f}%",
            help="Percentage of games where key cards weren't drawn"
        )

def display_deck_composition(parsed_deck):
    card_counts = Counter(card['name'] for card in parsed_deck)
    
    for card, count in sorted(card_counts.items()):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{card.title()}**")
        with col2:
            st.markdown(f'<span style="background: #667eea; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.875rem; display: inline-block;">{count}x</span>', unsafe_allow_html=True)

def display_main_attackers(main_attackers, evolution_methods):
    if main_attackers:
        for attacker in main_attackers:
            method = evolution_methods.get(attacker, 'N/A')
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**{attacker.title()}**")
            with col2:
                st.markdown(f'<span style="color: #667eea; font-weight: 500;">{method}</span>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ No main attackers identified!")

def create_results_summary(total_bricks, attacker_bricks, key_card_bricks, total_trials, brick_rate, attacker_rate, key_card_rate):
    summary_status = "status-good" if brick_rate < 15 else "status-warning" if brick_rate < 30 else "status-error"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 2rem; border-radius: 16px; border-left: 4px solid #667eea; margin: 1.5rem 0;">
        <h4 style="color: #1e293b; margin-bottom: 1rem;">📈 Simulation Analysis</h4>
        <p style="font-size: 1.1rem; color: #475569; line-height: 1.6;">
            <strong>Summary of {total_trials:,} trials:</strong><br>
            • <span class="{summary_status}">{total_bricks:,} games resulted in strict bricks ({brick_rate:.2f}%)</span><br>
            • <strong>{attacker_bricks:,}</strong> games had insufficient main attackers ({attacker_rate:.2f}%)<br>
            • <strong>{key_card_bricks:,}</strong> of those were due to key cards not being drawn ({key_card_rate:.2f}% of all games)
        </p>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Pokemon TCG Pocket Deck Simulator",
        page_icon=".streamlit/static/Pokeball.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Create animated header
    create_animated_header()
    
    # Load card data
    data = load_card_data("ALL_SETS.csv")

    # Enhanced sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Simulation Settings")
        st.markdown("---")
        
        # Number of trials slider with enhanced styling
        trials = st.slider(
            "🔄 Number of Trials", 
            min_value=100, 
            max_value=5000, 
            value=1000, 
            step=100,
            help="More trials = more accurate results but slower computation"
        )
        
        # Progress indicator for trial count
        trial_quality = "Excellent" if trials >= 2000 else "Good" if trials >= 1000 else "Basic"
        trial_color = "#10b981" if trials >= 2000 else "#f59e0b" if trials >= 1000 else "#6b7280"
        
        st.markdown(f"""
        <div style="background: {trial_color}20; padding: 0.5rem 1rem; border-radius: 8px; border-left: 3px solid {trial_color}; margin-bottom: 1rem;">
            <small style="color: {trial_color}; font-weight: 600;">Accuracy Level: {trial_quality}</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Number of turns slider
        max_turns = st.slider(
            "🎯 Turns to Simulate", 
            min_value=4, 
            max_value=10, 
            value=5,
            help="How many turns to simulate before evaluating the hand"
        )
        
        # Number of examples
        show_examples = st.number_input(
            "📝 Example Hands to Show",
            min_value=0,
            max_value=10,
            value=3 if trials < 500 else 2,
            help="Shows detailed logs of bricked games for analysis"
        )
    
    # Main content area with enhanced layout
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown("### 📝 Deck List Input")
        
        # Default deck list
        default_deck = """2 Charmander A1 33
1 Charizard A1 35
1 Charizard ex A1 36
2 Moltres ex A1 47
1 Farfetch'd A1 198

2 Professor's Research P-A 7
1 Sabrina A1 225
1 Leaf A1a 68
1 Dawn A2 154
2 Poké Ball P-A 5
2 Rare Candy A3 144
1 Potion P-A 1
1 X Speed P-A 2
1 Red Card P-A 6
1 Giant Cape A2 147"""
        
        decklist_input = st.text_area(
            "Enter your deck list",
            value=default_deck,
            height=400,
            help="Format: [quantity] [card name] [set code] [card number]",
            placeholder="2 Charmander A1 33\n1 Charizard A1 35\n..."
        )
    
    with col2:
        st.markdown("### 🚀 Analysis Controls")
        
        if st.button("🎯 Analyze Deck", type="primary", use_container_width=True):
            if not decklist_input.strip():
                st.error("📝 Please enter a deck list!")
                return
                
            # Enhanced progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Parse deck
            status_text.text("🔍 Parsing deck list...")
            progress_bar.progress(20)
            time.sleep(0.5)
            try:
                parsed_deck = parse_decklist(decklist_input)
            except ValueError as e:
                st.error(f"Deck parsing error: {e}")
                return
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                return
            # Step 2: Identify attackers
            status_text.text("⚔️ Identifying main attackers...")
            progress_bar.progress(40)
            time.sleep(0.5)
            
            main_attackers, evolution_methods = get_main_attackers_and_evolution_methods(parsed_deck)
            
            # Step 3: Run simulation
            status_text.text(f"🎲 Running {trials:,} simulations...")
            progress_bar.progress(60)
            time.sleep(0.5)
            
            total_bricks, attacker_bricks, key_card_bricks, total_trials, example_logs = simulate_brick_rate_with_examples(
                parsed_deck, 
                main_attackers, 
                trials=trials, 
                show_examples=show_examples, 
                maxturns=max_turns
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
            st.success(f"✅ Successfully analyzed {len(parsed_deck)} cards!")
        
        st.markdown("---")
        st.markdown("### 📊 Quick Tips")
        st.markdown("""
        **Brick Rate Guidelines for 5 turns Consistency (for lower or higher turn counts percentages will vary)\n
        You change for how many turns u want to simulate in the side panel:**
        - 🟢 **< 10%**: Excellent consistency
        - 🟡 **10-20%**: Good consistency
        - 🔴 **> 20%**: Needs improvement
        """)
    
    # Results section (only show if analysis was run)
    if 'parsed_deck' in locals() and parsed_deck:
        st.markdown("---")
        colA, colB = st.columns(2)
        with colA:
            with st.expander("📊 Deck Composition", expanded=True):
                display_deck_composition(parsed_deck)
        with colB:
            with st.expander("⚔️ Main Attackers Found", expanded=True):
                display_main_attackers(main_attackers, evolution_methods)
        
        # Results metrics
        if 'total_bricks' in locals():
            st.markdown("---")
            st.markdown("## 📈 Simulation Results")
            
            # Calculate rates
            brick_rate = (total_bricks / total_trials) * 100
            attacker_rate = (attacker_bricks / total_trials) * 100
            key_card_rate = (key_card_bricks / total_trials) * 100
            
            # Display metrics
            create_metrics_section(brick_rate, attacker_rate, key_card_rate)
            
            # Results summary
            create_results_summary(total_bricks, attacker_bricks, key_card_bricks, total_trials, brick_rate, attacker_rate, key_card_rate)
            
            # Example bricked games
            if example_logs and show_examples > 0:
                st.markdown("---")
                st.markdown("## 🔍 Example Analysis")
                st.markdown("Detailed play-by-play examples of games that resulted in bricks:")
                
                for i, example in enumerate(example_logs, 1):
                    with st.expander(f"🧱 Bricked Game Example #{i}", expanded=False):
                        st.code('\n'.join(example), language='text')
            elif 'total_bricks' in locals() and total_bricks == 0:
                st.balloons()
                st.success(f"🎉 Exceptional! No bricked games found in this simulation! of {total_trials}")
            elif show_examples == 0:
                st.info("💡 Set 'Example Hands to Show' > 0 to see detailed examples of bricked games.")

if __name__ == "__main__":
    main()