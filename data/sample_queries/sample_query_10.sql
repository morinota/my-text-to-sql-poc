-- 10. 最も多く支払いを行った顧客トップ5を取得
SELECT c.customer_id, c.first_name || ' ' || c.last_name AS customer_name, SUM(p.amount) AS total_payments
FROM customer c
JOIN payment p ON c.customer_id = p.customer_id
GROUP BY c.customer_id, customer_name
ORDER BY total_payments DESC
LIMIT 5;
