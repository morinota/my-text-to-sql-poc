-- 6. 各店舗のレンタル数を取得
SELECT store_id, COUNT(*) AS rental_count
FROM rental
GROUP BY store_id;

