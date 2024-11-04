-- 8. 特定の俳優が出演した映画リスト（例：ジョニー・デップ）
SELECT f.title
FROM film f
JOIN film_actor fa ON f.film_id = fa.film_id
JOIN actor a ON fa.actor_id = a.actor_id
WHERE a.first_name = 'JOHNNY' AND a.last_name = 'DEPP';

