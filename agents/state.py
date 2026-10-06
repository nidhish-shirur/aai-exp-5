import uuid
import time


def create_workflow_state(user_query):

    return {
        "workflow_id": str(uuid.uuid4()),
        "user_query": user_query,

        "requirements": {},
        "plan": {},
        "messages": [],

        "search_results": [],
        "filtered_results": [],
        "comparison": [],
        "ranking": [],

        "validation": {},
        "human_approval": None,
        "final_recommendation": [],

        "errors": [],

        "trace": [],

        "metrics": {
            "agent_calls": 0,
            "tool_calls": 0,
            "retries": 0,
            "start_time": None,
            "end_time": None,
            "execution_time": 0,
            "sequential_time": 0,
            "parallel_time": 0,
            "speedup": 0
        }
    }


def add_trace(state, agent, task, status, details=""):

    state["trace"].append({
        "agent": agent,
        "task": task,
        "status": status,
        "details": details,
        "timestamp": time.strftime("%H:%M:%S")
    })

    if status == "Completed":
        state["metrics"]["agent_calls"] += 1