-- 5. 各俳優が出演した映画の総数を取得
SELECT a.actor_id, a.first_name || ' ' || a.last_name AS actor_name, COUNT(fa.film_id) AS film_count
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
GROUP BY a.actor_id, actor_name
ORDER BY film_count DESC;

