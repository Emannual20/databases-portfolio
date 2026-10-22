.headers on
.mode box

SELECT COUNT(*) AS total_rows FROM readings;

SELECT machine,
       ROUND(AVG(temp_c), 2) AS avg_temp,
       ROUND(MAX(vib_rms), 3) AS max_vib
FROM readings
GROUP BY machine;