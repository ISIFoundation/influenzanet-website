/*
* Current season season data
*/

DELETE FROM epidb_fr.pollster_results_intake WHERE timestamp >= '2019-11-20';
DELETE FROM epidb_fr.pollster_results_weekly WHERE timestamp >= '2019-11-20';

/* 
* 2019-2020 intake
*/

INSERT INTO epidb_fr.pollster_results_intake
SELECT 'FR',
    global_id, "timestamp", 
	CASE WHEN "Q0"=3 OR "Q0"=1 THEN 1 ELSE "Q0" END AS "Q0", 
	"NOTE", 
	"Q1", "Q2", "Q3", 
	"Q4", "Q4b", "Q4b_0_open", "Q4c", "Q4d_0", "Q4d_1", "Q4d_2", "Q4d_3", "Q4d_4", "Q4d_5", 
	"Q5_0", "Q5_1", "Q5_2", "Q5_3", "Q5_4", 
	"Q6_0", "Q6_0_open", "Q6_1", "Q6_1_open", "Q6_2", "Q6_2_open", "Q6_3", "Q6_3_open", "Q6_4", "Q6_4_open", "Q6b", 
	"Q7", "Q7b", 
	CASE WHEN "Q8"=6 OR "Q8"=1 THEN 1 else "Q8" END, 
	"Q9", 
	"Q10", "Q10b", "Q10b_1_open", 
	CASE WHEN "Q10c_0"=True OR "Q10c_11"=True THEN True ELSE False END as "Q10c_0", "Q10c_1", "Q10c_2", "Q10c_3", "Q10c_4", "Q10c_5", "Q10c_6", "Q10c_7", "Q10c_8", "Q10c_9", 
	"Q10d_0", "Q10d_1", "Q10d_2", "Q10d_3", "Q10d_4", "Q10d_5", "Q10d_6", "Q10d_7", "Q10d_8", "Q10d_9", "Q10d_10", "Q10d_11", "Q10d_12", "Q10d_13", CASE WHEN  "Q10d_14"=True OR "Q10d_15"=True OR "Q10d_16" THEN True ELSE False END AS "Q10d_14", 
	"Q11_0", "Q11_1", "Q11_2", "Q11_3", "Q11_4", "Q11_5", "Q11_6", 
	"Q12", 
	NULL as "Q12b", /* Q12b not provided this year ? */
	CASE WHEN "Q13" = 5 OR "Q13"=6 THEN 0 ELSE "Q13" END, 
	"Q14_1", "Q14_2", "Q14_3", "Q14_4", "Q14_5", 
	NULL, NULL, NULL, NULL, NULL, /* "Q15_0", "Q15_1", "Q15_2", "Q15_3", "Q15_4", */
	"Q16_0", "Q16_1", "Q16_2", "Q16_3", "Q16_4", 
	"Q17_0", "Q17_1",
	CASE WHEN "Q17_8"=True OR "Q17_9"=True OR "Q17_10"=True OR "Q17_12"=True THEN True ELSE False END as "Q17_2", "Q17_3", "Q17_4", "Q17_5" /* "Q17_0", "Q17_1", "Q17_2", "Q17_3", "Q17_4", "Q17_5"  */
	FROM public.pollster_results_intake
	WHERE channel='';	
	
/* 
* 2019-2020 data
*/
INSERT INTO epidb_fr.pollster_results_weekly
SELECT 
	'FR', global_id, "timestamp", 
	"Q1_0", "Q1_1", "Q1_2", "Q1_3", "Q1_4", "Q1_5", "Q1_6", "Q1_7", "Q1_8", "Q1_9", "Q1_10", "Q1_11", "Q1_12", "Q1_13", "Q1_14", "Q1_15", "Q1_16", "Q1_17", "Q1_18", "Q1_19", 
	NULLIF("Q2", 9) as "Q2", 
	"N1", "Q3", "Q3_0_open", 
	"Q4", "Q4_0_open", 
	"Q5", 
	"Q6", "Q6_1_open", "Q6b", "Q6c", "Q6d", 
	"Q7_0", 
	"Q7_1", 
	"Q7_3", 
	"Q7_2",
	CASE WHEN "Q7_4"=True OR "Q7_7"=True OR "Q7_8"=True OR "Q7_6"=True OR "Q7_9"=True OR "Q7_10"=True THEN True ELSE False END as "Q7_4", 
	"Q7_5", 
	"Q7b_multi_row1_col1", NULL, "Q7b_multi_row3_col1", "Q7b_multi_row4_col1",
	"Q8_0", "Q8_1", "Q8_2", "Q8_3", "Q8_4", "Q8_5", 
	"Q8b_multi_row1_col1", "Q8b_multi_row2_col1", NULL, "Q8b_multi_row3_col1", /* row3 not provided, row4<-row3 */
	"Q9_0", "Q9_1", "Q9_2", "Q9_3", "Q9_4", "Q9_7" OR "Q9_5", "Q9_6", 
	"Q9b", 
	"Q10", "Q10b", "Q10c", 
	"Q11" FROM public.pollster_results_weekly
	WHERE channel='';

