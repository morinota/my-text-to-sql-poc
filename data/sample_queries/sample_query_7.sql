-- 7. 1ヶ月以内に返却されなかったレンタルのリストを取得
SELECT r.rental_id, r.customer_id, r.rental_date, r.return_date
FROM rental r
WHERE julianday(r.return_date) - julianday(r.rental_date) > 30;

