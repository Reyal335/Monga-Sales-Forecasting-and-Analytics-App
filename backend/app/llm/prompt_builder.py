from .sql_guard import input_guardrails, prompt_guardrails

def build_sql_generation_prompt(user_query: str) -> str:

    # check prompt for malicious, profane content
    input_guardrails(user_query)

    guardrails = prompt_guardrails()


    # Explicit schema definition of whitelisted read-only views
    schema = """
    View: audit_log (actor_user_id (uuid), details (jsonb), created_at (timestamp with time zone), audit_id (bigint), target_id (text), target_table (character varying), action (character varying))
    View: bill_of_materialss (item_id (character varying), bom_id (integer), quantity_required (numeric), ingredient_id (character varying))
    View: calendar_dim week_of_year (integer), calendar_date (date), month_name_short (character), epoch (bigint), quarter_name (character), is_weekend (boolean), day_of_year (integer), day_of_week (integer), year_actual (integer), month_number (integer), day_of_month (integer), day_name (character varying), quarter_number (integer), month_name (character varying), date_id (integer)
    View: ingredients cost_per_unit (numeric), ingredient_id (character varying), ingredient_name (character varying), unit_of_measure (character varying)
    View: menu_items (item_name (character varying), category (character varying), unit_price (numeric), item_id (character varying))
    View: order_items (order_id (integer), unit_price (numeric), item_id (character varying), quantity (integer), order_item_id (integer))
    View: orders (order_id (integer), order_timestamp (timestamp without time zone), store_id (character varying))
    View: roles (created_at (timestamp with time zone), description (text), role_name (character varying), role_id (smallint))
    View: stores (store_name (character varying), store_id (character varying))
    View: user_auth_tokens (token_id (uuid), token_type (character varying), token_hash (text), created_at (timestamp with time zone), used_at (timestamp with time zone), expires_at (timestamp with time zone), user_id (uuid))
    View: user_roles (user_id (uuid), assigned_at (timestamp with time zone), assigned_by (uuid), role_id (smallint))
    View: user_stores (user_id (uuid), store_id (character varying))
    View: users (updated_at (timestamp with time zone), phone_number (character varying), last_login_at (timestamp with time zone), is_active (boolean), full_name (character varying), user_id (uuid), password_hash (text), is_email_verified (boolean), created_at (timestamp with time zone), email (USER-DEFINED))
    """
    
    return f"""You are a PostgreSQL expert. Translate the question into a valid SQL query.
        Rules:
        1. Return ONLY the raw SQL string inside ``` ... ``` code fences. Do not put anything at the
        beginning or at the end of the SQL string, just the raw query
        2. Only write SELECT queries.

        ======== IMPORTANT ==========
        If with the given tables you cannot make a structured query from the user prompt, just go about answering the question
        as usual

        Database Schema:
        {schema}

        User Question: {user_query}
        SQL Query:
        
        Guardrails
        {guardrails["core"]}
        """  

        