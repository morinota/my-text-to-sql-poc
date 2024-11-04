-- 2. 2023年に発生したレンタルの総数を取得
SELECT COUNT(*) AS total_rentals
FROM rental
WHERE rental_date BETWEEN '2023-01-01' AND '2023-12-31';

