-- Pregunta 2: filas con incumplimientos de reglas numéricas o cronológicas.
SELECT row_id, order_id, order_date, ship_date, sales, quantity, discount
FROM superstore_alexander_2mom.superstore
WHERE order_date IS NULL OR ship_date IS NULL OR sales IS NULL
   OR quantity IS NULL OR discount IS NULL OR sales <= 0 OR quantity <= 0
   OR discount < 0 OR discount > 1 OR ship_date < order_date
ORDER BY row_id;

-- Observaciones de formato postal: no constituyen por sí mismas errores.
SELECT row_id, postal_code, city, state
FROM superstore_alexander_2mom.superstore
WHERE postal_code RLIKE '^[0-9]{4}$'
ORDER BY row_id
LIMIT 5;
