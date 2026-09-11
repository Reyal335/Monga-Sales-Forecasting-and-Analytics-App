from sql_guard import input_guardrails, prompt_guardrails

def build_sql_generation_prompt(user_query: str, branch_id: int) -> str:

    # check prompt for malicious, profane content
    input_guardrails(user_query)

    guardrails = prompt_guardrails()


    # Explicit schema definition of whitelisted read-only views
    schema = """
    View: v_orders (order_id INT, branch_id INT, total_amount FLOAT, created_at TIMESTAMP)
    View: v_order_items (order_id INT, item_id INT, item_name TEXT, quantity INT, unit_price FLOAT, branch_id INT)
    View: v_bill_of_materials (item_id INT, ingredient_id INT, ingredient_name TEXT, quantity_required FLOAT)
    """
    
    return f"""You are a PostgreSQL expert. Translate the question into a valid SQL query.
        Rules:
        1. Return ONLY the raw SQL string inside ```sql ... ``` code fences.
        2. Only write SELECT queries.
        3. You MUST include 'WHERE branch_id = {branch_id}' on query tables containing branch_id.

        Database Schema:
        {schema}

        User Question: {user_query}
        SQL Query:
        
        Guardrails
        {guardrails.core}
        """  

        