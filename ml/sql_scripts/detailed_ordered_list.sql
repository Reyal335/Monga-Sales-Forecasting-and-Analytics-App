select * from orders;
select * from stores;
select * from order_items order by order_id asc;
select * from menu_items;

-- All orders with all items and store information
SELECT 
	o.order_id,
	o.store_id,
	s.store_name,
	mi.item_name,
	oi.quantity,
	mi.unit_price,
	(mi.unit_price * oi.quantity) as "total_price"
FROM orders o 
RIGHT JOIN order_items oi
ON o.order_id = oi.order_id
LEFT JOIN stores s 
ON s.store_id = o.store_id
LEFT JOIN menu_items mi
ON mi.item_id = oi.item_id
ORDER BY order_id