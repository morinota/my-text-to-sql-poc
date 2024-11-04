-- 1. 各顧客の累計支払い金額を取得
SELECT customer_id, SUM(amount) AS total_amount
FROM payment
GROUP BY customer_id;

