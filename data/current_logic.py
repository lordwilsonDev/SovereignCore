
def improved_decision(context):
    """Adaptive decision making."""
    v, e = context.get("volition", 50), context.get("energy", 50)
    history = context.get("history", [])
    
    # Adaptive: learn from history
    if len(history) > 5:
        recent_success = sum(1 for h in history[-5:] if h.get("success", False))
        if recent_success > 3:
            return "ESCALATE"
        elif recent_success < 2:
            return "RETREAT"
    
    # Default logic
    return "ACT_BOLDLY" if v > 80 else "CONSERVE" if e < 20 else "EXPLORE"
