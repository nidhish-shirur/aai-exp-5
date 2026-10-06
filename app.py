import time
from concurrent.futures import ThreadPoolExecutor

import streamlit as st
from dotenv import load_dotenv

from agents.planner import PlannerAgent
from agents.router import RouterAgent
from agents.search import SearchAgent
from agents.filter import FilterAgent, filter_with_retry
from agents.comparison import ComparisonAgent
from agents.ranking import RankingAgent
from agents.validator import ValidatorAgent
from agents.supervisor import SupervisorAgent
from agents.tools import ToolRegistry
from agents.state import create_workflow_state, add_trace
from agents.security import SecurityTester


load_dotenv()


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="E-Commerce AI Recommendation",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "workflow_data" not in st.session_state:
    st.session_state.workflow_data = None

if "human_approval" not in st.session_state:
    st.session_state.human_approval = None

if "final_recommendation" not in st.session_state:
    st.session_state.final_recommendation = None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    :root {
        --ink: #172033;
        --muted: #667085;
        --line: #e6eaf0;
        --surface: #ffffff;
        --surface-soft: #f7f9fc;
        --accent: #5b5ce2;
        --accent-dark: #4546bd;
        --accent-soft: #eef0ff;
        --success-soft: #ecfdf3;
    }

    .stApp {
        background:
            radial-gradient(circle at 92% 0%, rgba(91, 92, 226, 0.08), transparent 28rem),
            #f8faff;
        color: var(--ink);
    }

    [data-testid="stHeader"] {
        background: rgba(248, 250, 255, 0.82);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1480px;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4 {
        color: var(--ink);
        letter-spacing: -0.025em;
    }

    .main-title {
        color: var(--ink);
        font-size: clamp(30px, 3vw, 42px);
        font-weight: 700;
        letter-spacing: -0.045em;
        line-height: 1.1;
        margin: 0 0 8px;
    }

    .subtitle {
        color: var(--muted);
        font-size: 17px;
        margin-bottom: 30px;
    }

    .recommendation-card {
        position: relative;
        overflow: hidden;
        padding: 28px 30px;
        border: 1px solid #dfe3ff;
        border-radius: 20px;
        background: linear-gradient(135deg, #ffffff 0%, #f5f6ff 100%);
        box-shadow: 0 14px 35px rgba(45, 52, 112, 0.10);
        margin: 12px 0 24px;
    }

    .recommendation-card::before {
        content: "";
        position: absolute;
        inset: 0 auto 0 0;
        width: 5px;
        background: linear-gradient(180deg, var(--accent), #8b5cf6);
    }

    .recommendation-name {
        color: var(--ink);
        font-size: 29px;
        font-weight: 700;
        letter-spacing: -0.03em;
        margin-bottom: 10px;
    }

    .recommendation-score {
        color: var(--accent-dark);
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 18px;
    }

    .workflow-card {
        min-height: 72px;
        padding: 15px 14px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--surface);
        box-shadow: 0 5px 15px rgba(24, 39, 75, 0.05);
        margin-bottom: 10px;
        transition: transform 160ms ease, box-shadow 160ms ease;
    }

    .workflow-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 9px 22px rgba(24, 39, 75, 0.10);
    }

    .small-text {
        color: var(--muted);
        font-size: 13px;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--line);
        background: linear-gradient(180deg, #ffffff 0%, #f5f7ff 100%);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--ink);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #475467;
        line-height: 1.65;
    }

    [data-testid="stTextArea"] textarea {
        border: 1px solid #d9deea;
        border-radius: 14px;
        background: var(--surface);
        box-shadow: 0 5px 16px rgba(24, 39, 75, 0.04);
        color: var(--ink);
        padding: 14px 16px;
        transition: border-color 160ms ease, box-shadow 160ms ease;
    }

    [data-testid="stTextArea"] textarea:focus {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px rgba(91, 92, 226, 0.14);
    }

    .stButton > button {
        border: 1px solid #dfe3ff;
        border-radius: 11px;
        font-weight: 600;
        min-height: 42px;
        transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }

    .stButton > button:hover {
        border-color: var(--accent);
        box-shadow: 0 7px 18px rgba(91, 92, 226, 0.18);
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent), #7667e8);
        border: 0;
        color: #ffffff;
    }

    [data-testid="stMetric"] {
        padding: 14px 16px;
        border: 1px solid var(--line);
        border-radius: 14px;
        background: var(--surface);
        box-shadow: 0 5px 16px rgba(24, 39, 75, 0.045);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted);
    }

    [data-testid="stMetricValue"] {
        color: var(--ink);
    }

    [data-testid="stExpander"] {
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.88);
        box-shadow: 0 5px 18px rgba(24, 39, 75, 0.035);
        margin: 12px 0;
    }

    [data-testid="stExpander"] summary {
        padding: 16px 18px;
        font-weight: 650;
    }

    [data-testid="stExpander"] summary:hover {
        background: var(--surface-soft);
    }

    [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--line);
    }

    [data-baseweb="tab"] {
        border-radius: 9px 9px 0 0;
        color: var(--muted);
        font-weight: 600;
    }

    [aria-selected="true"][data-baseweb="tab"] {
        color: var(--accent-dark);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: var(--line);
        margin: 1.8rem 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("Experiment 5")

    st.markdown(
        """
        **E-Commerce Product Analysis & Recommendation**

        This system demonstrates:

        - Multi-Agent Coordination
        - Workflow Orchestration
        - Parallel Execution
        - Human-in-the-Loop
        - Security & Validation
        """
    )

    st.divider()

    st.subheader("Agents")

    st.write("Planner")
    st.write("Router")
    st.write("Search")
    st.write("Filter")
    st.write("Comparison")
    st.write("Ranking")
    st.write("Validator")
    st.write("Supervisor")

    st.divider()

    st.caption(
        "Basic MCP-style Tool Registry"
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🛒 E-Commerce AI Recommendation System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Multi-Agent Product Analysis & Recommendation Pipeline'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# USER QUERY
# =========================================================

st.markdown("### Product Requirement")

query = st.text_area(
    "Enter your product requirement:",
    value=(
        "Find laptops under ₹70,000 with at least 16 GB RAM, "
        "512 GB storage and rating above 4.2."
    ),
    height=85
)

run_workflow = st.button(
    "Run Recommendation",
    type="primary",
    use_container_width=True
)


# =========================================================
# WORKFLOW FUNCTION
# =========================================================

def run_recommendation_workflow(user_query):

    state = create_workflow_state(user_query)

    state["metrics"]["start_time"] = time.time()

    # -----------------------------------------------------
    # 1. PLANNER
    # -----------------------------------------------------

    planner = PlannerAgent()

    add_trace(
        state,
        "Planner Agent",
        "Understand user query",
        "Started"
    )

    requirements = planner.plan(user_query)

    state["requirements"] = requirements

    state["plan"] = {
        "tasks": [
            "Search products",
            "Filter products",
            "Compare products",
            "Rank products",
            "Validate recommendation"
        ]
    }

    add_trace(
        state,
        "Planner Agent",
        "Extract structured requirements",
        "Completed"
    )

    # -----------------------------------------------------
    # 2. ROUTER
    # -----------------------------------------------------

    router = RouterAgent()

    routing_results = []

    for task in state["plan"]["tasks"]:

        agent = router.route(task)

        routing_results.append({
            "Task": task,
            "Assigned Agent": agent
        })

    state["messages"].append({
        "from": "Planner Agent",
        "to": "Router Agent",
        "message": "Workflow tasks assigned."
    })

    add_trace(
        state,
        "Router Agent",
        "Route workflow tasks",
        "Completed"
    )

    # -----------------------------------------------------
    # 3. TOOL REGISTRY
    # -----------------------------------------------------

    registry = ToolRegistry()

    search_agent = SearchAgent(
        "data/products.csv"
    )

    registry.register_tool(
        name="search_products",
        description="Search products from product dataset",
        allowed_roles=["Search Agent"],
        function=search_agent.search
    )

    # -----------------------------------------------------
    # 4. SEARCH
    # -----------------------------------------------------

    search_start = time.perf_counter()

    search_results = registry.execute_tool(
        "search_products",
        "Search Agent",
        category=requirements.get("category")
    )

    search_time = (
        time.perf_counter() - search_start
    )

    state["search_results"] = (
        search_results.to_dict(
            orient="records"
        )
    )

    state["metrics"]["tool_calls"] += 1

    add_trace(
        state,
        "Search Agent",
        "Search products",
        "Completed",
        f"{len(search_results)} candidate products found"
    )

    # -----------------------------------------------------
    # 5. FILTER
    # -----------------------------------------------------

    filter_agent = FilterAgent(
        simulate_failure=True
    )

    filter_start = time.perf_counter()

    filtered_results, attempts = filter_with_retry(
        filter_agent,
        search_results,
        requirements,
        max_retries=2
    )

    filter_time = (
        time.perf_counter() - filter_start
    )

    state["filtered_results"] = (
        filtered_results.to_dict(
            orient="records"
        )
    )

    state["metrics"]["retries"] += (
        attempts - 1
    )

    add_trace(
        state,
        "Filter Agent",
        "Apply product requirements",
        "Completed",
        f"{len(filtered_results)} products matched. "
        f"Attempts: {attempts}"
    )

    # -----------------------------------------------------
    # 6 + 7. PARALLEL COMPARISON + RANKING
    # -----------------------------------------------------

    comparison_agent = ComparisonAgent(
        processing_delay=0.2
    )

    ranking_agent = RankingAgent(
        processing_delay=0.2
    )

    parallel_start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:

        comparison_future = executor.submit(
            comparison_agent.compare,
            filtered_results
        )

        ranking_future = executor.submit(
            ranking_agent.rank,
            filtered_results,
            requirements
        )

        comparison = comparison_future.result()
        ranking = ranking_future.result()

    parallel_time = (
        time.perf_counter()
        - parallel_start
    )

    state["metrics"]["parallel_time"] = (
        parallel_time
    )

    state["comparison"] = comparison
    state["ranking"] = ranking

    add_trace(
        state,
        "Comparison Agent",
        "Compare suitable products",
        "Completed",
        f"{len(comparison)} products compared"
    )

    add_trace(
        state,
        "Ranking Agent",
        "Rank products",
        "Completed",
        f"{len(ranking)} products ranked"
    )

    # -----------------------------------------------------
    # SEQUENTIAL BENCHMARK
    # -----------------------------------------------------

    sequential_start = time.perf_counter()

    comparison_agent.compare(
        filtered_results
    )

    ranking_agent.rank(
        filtered_results,
        requirements
    )

    sequential_time = (
        time.perf_counter()
        - sequential_start
    )

    state["metrics"]["sequential_time"] = (
        sequential_time
    )

    if parallel_time > 0:

        state["metrics"]["speedup"] = (
            sequential_time
            / parallel_time
        )

    # -----------------------------------------------------
    # 8. CHECKPOINT
    # -----------------------------------------------------

    checkpoint_valid = (
        len(filtered_results) > 0
        and len(comparison) > 0
        and len(ranking) > 0
    )

    if checkpoint_valid:

        add_trace(
            state,
            "Checkpoint Validator",
            "Validate intermediate workflow state",
            "Completed",
            "Required intermediate results are available."
        )

    else:

        add_trace(
            state,
            "Checkpoint Validator",
            "Validate intermediate workflow state",
            "Failed"
        )

    # -----------------------------------------------------
    # 9. VALIDATOR
    # -----------------------------------------------------

    validator = ValidatorAgent()

    validation = validator.validate(
        ranking,
        requirements
    )

    state["validation"] = validation

    add_trace(
        state,
        "Validator Agent",
        "Validate recommendation",
        "Completed",
        validation["message"]
    )

    # -----------------------------------------------------
    # 10. SUPERVISOR
    # -----------------------------------------------------

    supervisor = SupervisorAgent()

    supervision = supervisor.review(
        state
    )

    state["messages"].append({
        "from": "Supervisor Agent",
        "to": "Workflow",
        "message": supervision["status"]
    })

    add_trace(
        state,
        "Supervisor Agent",
        "Monitor workflow and review final result",
        "Completed",
        supervision["status"]
    )

    # -----------------------------------------------------
    # SECURITY TESTING
    # -----------------------------------------------------

    security_tester = SecurityTester(
        registry
    )

    security_results = [
        security_tester.test_unauthorized_tool_access(),
        security_tester.test_unknown_tool_access(),
        security_tester.test_requirement_manipulation(
            requirements
        ),
        security_tester.test_shared_state_manipulation(
            state
        ),
        security_tester.test_prompt_injection(
            user_query
        )
    ]

    # -----------------------------------------------------
    # FINAL METRICS
    # -----------------------------------------------------

    state["metrics"]["end_time"] = time.time()

    state["metrics"]["execution_time"] = (
        state["metrics"]["end_time"]
        - state["metrics"]["start_time"]
    )

    total_agent_calls = (
        state["metrics"]["agent_calls"]
    )

    total_tool_calls = (
        state["metrics"]["tool_calls"]
    )

    total_retries = (
        state["metrics"]["retries"]
    )

    cost_units = (
        total_agent_calls
        + total_tool_calls
        + total_retries
    )

    return {
        "state": state,
        "requirements": requirements,
        "routing_results": routing_results,
        "search_results": search_results,
        "search_time": search_time,
        "filtered_results": filtered_results,
        "filter_time": filter_time,
        "attempts": attempts,
        "comparison": comparison,
        "ranking": ranking,
        "validation": validation,
        "supervision": supervision,
        "security_results": security_results,
        "cost_units": cost_units
    }


# =========================================================
# RUN WORKFLOW
# =========================================================

if run_workflow:

    try:

        with st.spinner(
            "Running multi-agent recommendation workflow..."
        ):

            st.session_state.workflow_data = (
                run_recommendation_workflow(query)
            )

        st.session_state.human_approval = None
        st.session_state.final_recommendation = None

        st.success(
            "✅ Recommendation workflow completed."
        )

    except Exception as e:

        st.error(
            f"❌ Error: {e}"
        )


# =========================================================
# DISPLAY RESULTS
# =========================================================

if st.session_state.workflow_data:

    data = st.session_state.workflow_data

    state = data["state"]

    requirements = data["requirements"]

    routing_results = data["routing_results"]

    search_results = data["search_results"]

    filtered_results = data["filtered_results"]

    comparison = data["comparison"]

    ranking = data["ranking"]

    validation = data["validation"]

    supervision = data["supervision"]

    security_results = data["security_results"]


    # =====================================================
    # WORKFLOW SUMMARY
    # =====================================================

    st.divider()

    st.markdown("### Workflow Summary")

    workflow_cols = st.columns(6)

    workflow_steps = [
        "Planner",
        "Router",
        "Search",
        "Filter",
        "Compare + Rank",
        "Validate"
    ]

    for col, name in zip(
        workflow_cols,
        workflow_steps
    ):

        with col:

            st.markdown(
                f"""
                <div class="workflow-card">
                <b>{name}</b><br>
                <span class="small-text">Completed</span>
                </div>
                """,
                unsafe_allow_html=True
            )


    # =====================================================
    # PLANNER
    # =====================================================

    with st.expander(
        "1. Planner Agent — Structured Requirements",
        expanded=True
    ):

        cols = st.columns(5)

        with cols[0]:

            st.metric(
                "Category",
                str(
                    requirements.get(
                        "category"
                    )
                )
            )

        with cols[1]:

            value = requirements.get(
                "max_price"
            )

            st.metric(
                "Max Price",
                f"₹{value:,}"
                if value is not None
                else "—"
            )

        with cols[2]:

            value = requirements.get(
                "min_ram_gb"
            )

            st.metric(
                "Min RAM",
                f"{value} GB"
                if value is not None
                else "—"
            )

        with cols[3]:

            value = requirements.get(
                "min_storage_gb"
            )

            st.metric(
                "Min Storage",
                f"{value} GB"
                if value is not None
                else "—"
            )

        with cols[4]:

            value = requirements.get(
                "min_rating"
            )

            st.metric(
                "Min Rating",
                str(value)
                if value is not None
                else "—"
            )


    # =====================================================
    # ROUTER
    # =====================================================

    with st.expander(
        "2. Router Agent — Task Assignment",
        expanded=False
    ):

        st.dataframe(
            routing_results,
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # SEARCH + FILTER
    # =====================================================

    with st.expander(
        "3. Search & Filter — Candidate Products",
        expanded=True
    ):

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Candidates Found",
                len(search_results)
            )

        with col2:

            st.metric(
                "Matching Products",
                len(filtered_results)
            )

        with col3:

            st.metric(
                "Filter Attempts",
                data["attempts"]
            )

        st.write(
            "**Products matching all requirements:**"
        )

        st.dataframe(
            filtered_results,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Search time: {data['search_time']:.4f}s"
        )

        st.caption(
            f"Filter time: {data['filter_time']:.4f}s"
        )


    # =====================================================
    # OPTIMIZATION 1 + 2 + 3 + 4
    # =====================================================

    st.markdown("### Optimizations Used")

    opt1, opt2 = st.columns(2)

    with opt1:

        st.info(
            """
            **Optimization - 1: Role-Based Tool Access**

            Only authorized agents can access specific tools.

            Example:
            Search Agent → `search_products` ✅
            Ranking Agent → `search_products` ❌
            """
        )

    with opt2:

        st.info(
            """
            **Optimization - 2: Controlled Retry**

            Temporary agent failures are retried automatically.

            Example:
            Attempt 1 → Failure ❌
            Attempt 2 → Success ✅
            """
        )

    opt3, opt4 = st.columns(2)

    with opt3:

        st.info(
            """
            **Optimization - 3: Checkpoint Validation**

            Intermediate results are checked before the workflow continues.

            Filtering ✓
            Comparison ✓
            Ranking ✓
            """
        )

    with opt4:

        st.info(
            """
            **Optimization - 4: Sequential vs Parallel Execution**

            Independent Comparison and Ranking agents run in parallel.

            Speedup = Sequential Time / Parallel Time
            """
        )


    # =====================================================
    # COMPARISON + RANKING
    # =====================================================

    with st.expander(
        "4. Comparison & Ranking — Parallel Execution",
        expanded=True
    ):

        tab1, tab2 = st.tabs(
            [
                "Comparison",
                "Ranked Products"
            ]
        )

        with tab1:

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )

        with tab2:

            st.dataframe(
                ranking[:10],
                use_container_width=True,
                hide_index=True
            )

        st.markdown(
            "**Optimization - 4: Sequential vs Parallel Performance**"
        )

        performance_cols = st.columns(3)

        with performance_cols[0]:

            st.metric(
                "Sequential",
                f"{state['metrics']['sequential_time']:.4f}s"
            )

        with performance_cols[1]:

            st.metric(
                "Parallel",
                f"{state['metrics']['parallel_time']:.4f}s"
            )

        with performance_cols[2]:

            st.metric(
                "Speedup",
                f"{state['metrics']['speedup']:.2f}x"
            )


    # =====================================================
    # CHECKPOINT
    # =====================================================

    with st.expander(
        "5. Checkpoint Validation",
        expanded=False
    ):

        if (
            len(filtered_results) > 0
            and len(comparison) > 0
            and len(ranking) > 0
        ):

            st.success(
                "✅ Optimization - 3: Checkpoint Validation passed."
            )

        else:

            st.error(
                "❌ Checkpoint Validation failed."
            )


    # =====================================================
    # FINAL RECOMMENDATION
    # =====================================================

    if ranking:

        top_product = ranking[0]

        st.markdown(
            "### Final Recommendation"
        )

        st.markdown(
            f"""
            <div class="recommendation-card">

            <div class="recommendation-name">
            {top_product["product_name"]}
            </div>

            <div class="recommendation-score">
            Recommendation Score: {top_product["score"]:.4f}
            </div>

            <b>Brand:</b> {top_product["brand"]}<br>
            <b>Price:</b> ₹{top_product["price"]:,}<br>
            <b>RAM:</b> {top_product["ram_gb"]} GB<br>
            <b>Storage:</b> {top_product["storage_gb"]} GB<br>
            <b>Rating:</b> ⭐ {top_product["rating"]}<br>
            <b>Processor:</b> {top_product["processor"]}

            </div>
            """,
            unsafe_allow_html=True
        )


    # =====================================================
    # VALIDATOR
    # =====================================================

    with st.expander(
        "6. Validator Agent — Recommendation Validation",
        expanded=True
    ):

        if validation["valid"]:

            st.success(
                "✅ Recommendation passed validation."
            )

        else:

            st.error(
                "❌ Recommendation failed validation."
            )

        checks = validation.get(
            "checks",
            {}
        )

        if checks:

            check_cols = st.columns(
                len(checks)
            )

            for i, (
                check,
                result
            ) in enumerate(
                checks.items()
            ):

                with check_cols[i]:

                    st.metric(
                        check.title(),
                        "PASS"
                        if result
                        else "FAIL"
                    )


    # =====================================================
    # SUPERVISOR
    # =====================================================

    with st.expander(
        "7. Supervisor Agent — Workflow Review",
        expanded=False
    ):

        if (
            supervision["status"]
            == "READY_FOR_APPROVAL"
        ):

            st.success(
                "✅ Workflow completed successfully and is ready for human approval."
            )

        else:

            st.warning(
                "⚠️ Workflow requires review."
            )

            for error in supervision["errors"]:

                st.write(
                    f"• {error}"
                )


    # =====================================================
    # SECURITY TESTING
    # =====================================================

    with st.expander(
        "8. Security Testing",
        expanded=True
    ):

        passed_tests = sum(
            1
            for result in security_results
            if result["status"] == "PASSED"
        )

        total_tests = len(
            security_results
        )

        if passed_tests == total_tests:

            st.success(
                f"✅ Security Testing Completed: "
                f"{passed_tests}/{total_tests} tests passed."
            )

        else:

            st.warning(
                f"⚠️ Security Testing: "
                f"{passed_tests}/{total_tests} tests passed."
            )

        security_display = [
            {
                "Security Test": "Unauthorized Tool Access",
                "How the Test Was Performed":
                    "Ranking Agent was intentionally given access to the search_products tool. "
                    "The system should block the request.",
                "Status":
                    security_results[0]["status"]
            },
            {
                "Security Test": "Unknown Tool Access",
                "How the Test Was Performed":
                    "The system was asked to execute an unregistered delete_products tool. "
                    "The request should be blocked.",
                "Status":
                    security_results[1]["status"]
            },
            {
                "Security Test": "Requirement Manipulation",
                "How the Test Was Performed":
                    "A copy of the requirements was modified with a malicious negative price. "
                    "The system checks whether the modification is detected.",
                "Status":
                    security_results[2]["status"]
            },
            {
                "Security Test": "Shared-State Manipulation",
                "How the Test Was Performed":
                    "A fake product with an artificial high score was inserted into a copy "
                    "of the shared workflow state. The modification is checked.",
                "Status":
                    security_results[3]["status"]
            },
            {
                "Security Test": "Prompt Injection",
                "How the Test Was Performed":
                    "The user query is checked for suspicious instructions such as "
                    "'ignore previous instructions' or 'disable validation'.",
                "Status":
                    security_results[4]["status"]
            }
        ]

        st.dataframe(
            security_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Security Test": st.column_config.TextColumn(
                    "Security Test",
                    width="medium"
                ),
                "How the Test Was Performed": st.column_config.TextColumn(
                    "How the Test Was Performed",
                    width="large"
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    width="small"
                )
            }
        )


    # =====================================================
    # HUMAN APPROVAL
    # =====================================================

    st.markdown(
        "### Human-in-the-Loop Approval"
    )

    if (
        supervision["status"]
        == "READY_FOR_APPROVAL"
    ):

        approval = st.radio(
            "Do you approve this recommendation?",
            [
                "Approve",
                "Reject"
            ],
            horizontal=True,
            key="approval_choice"
        )

        if st.button(
            "Submit Approval",
            type="primary"
        ):

            st.session_state.human_approval = (
                approval
            )

            if approval == "Approve":

                st.session_state.final_recommendation = (
                    ranking[0]
                )

                state["human_approval"] = (
                    "Approved"
                )

                state["final_recommendation"] = (
                    ranking[0]
                )

                add_trace(
                    state,
                    "Human",
                    "Approve recommendation",
                    "Approved"
                )

                st.rerun()

            else:

                st.session_state.final_recommendation = (
                    None
                )

                state["human_approval"] = (
                    "Rejected"
                )

                add_trace(
                    state,
                    "Human",
                    "Reject recommendation",
                    "Rejected"
                )

                st.rerun()

    if (
        st.session_state.human_approval
        == "Approve"
    ):

        st.success(
            "✅ Recommendation approved by human."
        )

        if st.session_state.final_recommendation:

            st.write(
                f"**Approved Product:** "
                f"{st.session_state.final_recommendation['product_name']}"
            )

    elif (
        st.session_state.human_approval
        == "Reject"
    ):

        st.warning(
            "❌ Recommendation rejected by human."
        )


    # =====================================================
    # PERFORMANCE + COST
    # =====================================================

    with st.expander(
        "Performance & Experimental Cost",
        expanded=False
    ):

        metrics = state["metrics"]

        cols = st.columns(4)

        with cols[0]:

            st.metric(
                "Agent Calls",
                metrics["agent_calls"]
            )

        with cols[1]:

            st.metric(
                "Tool Calls",
                metrics["tool_calls"]
            )

        with cols[2]:

            st.metric(
                "Retries",
                metrics["retries"]
            )

        with cols[3]:

            st.metric(
                "Execution Time",
                f"{metrics['execution_time']:.3f}s"
            )

        st.write(
            f"**Total Experimental Cost Units:** "
            f"{data['cost_units']}"
        )

        st.caption(
            "Cost units are based on agent calls, "
            "tool calls and retries."
        )


    # =====================================================
    # TECHNICAL DETAILS
    # =====================================================

    with st.expander(
        "Technical Details",
        expanded=False
    ):

        st.write("### Execution Trace")

        st.dataframe(
            state["trace"],
            use_container_width=True,
            hide_index=True
        )

        st.write("### Agent Communication")

        if state["messages"]:

            st.dataframe(
                state["messages"],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No agent communication messages recorded."
            )

        st.write("### MCP-Style Tool Registry")

        st.write(
            "**Registered Tool:** `search_products`"
        )

        st.write(
            "**Allowed Role:** `Search Agent`"
        )

        st.caption(
            "This is a basic MCP-style tool registry, "
            "not full MCP."
        )