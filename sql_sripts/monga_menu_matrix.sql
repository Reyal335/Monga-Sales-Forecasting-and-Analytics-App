WITH item_data AS (
	SELECT
	    m.item_id,
	    m.item_name,
	    m.category,
	    m.unit_price,
	    SUM(i.cost_per_unit * b.quantity_required) AS total_recipe_cost,
		(m.unit_price - SUM(i.cost_per_uanit * b.quantity_required)) AS contribution_margin
	FROM menu_items m
	INNER JOIN bill_of_materials b
	    ON b.item_id = m.item_id
	INNER JOIN ingredients i
	    ON i.ingredient_id = b.ingredient_id
	GROUP BY 
	    m.item_id,
	    m.item_name,
	    m.category,
	    m.unit_price
	ORDER BY m.item_id
), item_count AS (
	SELECT 
		oi.item_id,
		COUNT(oi.item_id) as item_count
	FROM orders o
	INNER JOIN order_items oi
	ON o.order_id = oi.order_id
	GROUP BY oi.item_id
)

SELECT 
	d.*, 
	(d.unit_price * c.item_count) as total_revenue,
	(d.contribution_margin * c.item_count) as total_profit
FROM item_data d
INNER JOIN item_count c
ON d.item_id = c.item_id
	