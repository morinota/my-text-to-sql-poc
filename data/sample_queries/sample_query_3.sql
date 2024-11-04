-- 3. 各映画カテゴリごとの平均レンタル日数を取得
SELECT c.name AS category_name, AVG(julianday(r.return_date) - julianday(r.rental_date)) AS avg_rental_days
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film_category fc ON i.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
GROUP BY c.name;

