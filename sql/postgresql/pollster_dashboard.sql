DROP VIEW IF EXISTS pollster_dashboard_badges;
CREATE VIEW pollster_dashboard_badges AS
SELECT DISTINCT 
			 global_id,
			 user_id AS "user",
			 count(*) OVER (PARTITION BY global_id) >= 1 AS is_novice,
			 count(*) OVER (PARTITION BY global_id) >= 3 AS is_junior,
			 count(*) OVER (PARTITION BY global_id) >= 6 AS is_senior,
			 count(*) OVER (PARTITION BY global_id) >= 10 AS is_gold,
			 count(*) OVER (PARTITION BY global_id) >= 20 AS is_platinum,
			 sum(cold) OVER (PARTITION BY global_id) >= 3 AS is_cold_season,
			 sum(ili) OVER (PARTITION BY global_id)  >= 2 AS is_ili_season,
			 sum(gastro) OVER (PARTITION BY global_id) >= 2 AS is_gastro_season
	FROM (
SELECT DISTINCT global_id,
			 user_id,			 
		   to_char(timestamp, 'YYYYWW'),
		   CASE true WHEN (status ILIKE '%COLD%') THEN 1 ELSE 0 END as cold,
		   CASE true WHEN (status = 'ILI') THEN 1 ELSE 0 END as ili,
		   CASE true WHEN (status ILIKE '%GASTRO%') THEN 1 ELSE 0 END as gastro
  FROM pollster_dashboard_healt_status ) A;

DROP VIEW IF EXISTS pollster_dashboard_healt_status;
CREATE VIEW pollster_dashboard_healt_status AS 
               SELECT W.user AS user_id,
                      global_id,
                      timestamp,
                      id as pollster_results_weekly_id,
                      case true
                          when "Q1_0"
                              then 'NO-SYMPTOMS'

                          when ("Q5" = 0 or "Q6b" = 0)
                           and ("Q1_1" or "Q1_2"  or "Q6d" = 3 or "Q6d" = 4 or "Q6d" = 5 or "Q1_11" or "Q1_8" or "Q1_9")
                           and ("Q1_5" or "Q1_6" or "Q1_7")
                              then 'ILI'

                          when 
                            (
                                (not "Q1_1") and (not "Q1_2") 
                                and (("Q6d" = 0) or ("Q6d" is null)) 
                                and ("Q1_3" or "Q1_4" or "Q1_14")
                                and ("Q11" = 2)
                            ) and (
                                case true when "Q1_17" then 1 else 0 end + 
                                case true when "Q1_15" then 1 else 0 end + 
                                case true when "Q1_16" then 1 else 0 end + 
                                case true when "Q1_18" then 1 else 0 end >= 2
                            ) then 'ALLERGY-or-HAY-FEVER-and-GASTROINTESTINAL'

                          when (not "Q1_1") and (not "Q1_2") 
                           and (("Q6d" = 0) or ("Q6d" is null)) 
                           and ("Q1_3" or "Q1_4" or "Q1_14")
                           and ("Q11" = 2)
                              then 'ALLERGY-or-HAY-FEVER' 

                          when
                            (
                                case true when "Q1_3" then 1 else 0 end + 
                                case true when "Q1_4" then 1 else 0 end + 
                                case true when "Q1_6" then 1 else 0 end + 
                                case true when "Q1_5" then 1 else 0 end >= 2
                                  -- note: common cold after all allergy-related branches
                            ) and (
                                case true when "Q1_17" then 1 else 0 end + 
                                case true when "Q1_15" then 1 else 0 end + 
                                case true when "Q1_16" then 1 else 0 end + 
                                case true when "Q1_18" then 1 else 0 end >= 2
                            ) then 'COMMON-COLD-and-GASTROINTESTINAL'

                          when 
                            case true when "Q1_3" then 1 else 0 end + 
                            case true when "Q1_4" then 1 else 0 end + 
                            case true when "Q1_6" then 1 else 0 end + 
                            case true when "Q1_5" then 1 else 0 end >= 2
                              -- note: common cold after all allergy-related branches
                              then 'COMMON-COLD'

                          when 
                            case true when "Q1_17" then 1 else 0 end + 
                            case true when "Q1_15" then 1 else 0 end + 
                            case true when "Q1_16" then 1 else 0 end + 
                            case true when "Q1_18" then 1 else 0 end >= 2
                              then 'GASTROINTESTINAL'

                          else 'NON-SPECIFIC-SYMPTOMS'
                      end as status
                 FROM pollster_results_weekly W;
                 
                 
DROP VIEW IF EXISTS pollster_dashboard_history;
CREATE VIEW pollster_dashboard_history AS
        SELECT  H.user_id AS "user", 
                H.global_id, 
                U.name, 
                H.status, 
                H.timestamp 
           FROM pollster_dashboard_healt_status H, 
                survey_surveyuser U 
          WHERE U.global_id = H.global_id 
            AND U.user_id = H.user_id
       ORDER BY timestamp DESC;


DROP VIEW IF EXISTS pollster_dashboard_last_intake;
CREATE VIEW pollster_dashboard_last_intake AS
    SELECT DISTINCT first_value("Q3") OVER (partition by global_id order by timestamp desc) AS "Q3",
                    first_value(timestamp) over (partition by global_id order by timestamp desc) AS "timestamp",
                    "user", 
                    global_id
    FROM pollster_results_intake;

CREATE OR REPLACE FUNCTION pollster_dashboard_neighborhood_users(
        text -- $1 zip_code_key
) RETURNS TABLE (
  user_id       integer,
  global_id     text,
  zip_code_key  text,
  "timestamp"     timestamptz
)
AS  $$
        SELECT I."user" as user_id, 
               global_id, 
               zip_code_key, 
               I.timestamp 
        FROM (SELECT country, zip_code_key 
                FROM POLLSTER_ZIP_CODES 
               WHERE ST_Touches(geometry, (SELECT geometry FROM POLLSTER_ZIP_CODES WHERE ZIP_CODE_KEY = $1))
              ) A 
	INNER JOIN pollster_dashboard_last_intake I ON (A.zip_code_key = I."Q3");
	
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION pollster_dashboard_neighborhood_users_count(
        text -- $1 zip_code_key
) RETURNS integer
AS  $$
        SELECT count(DISTINCT global_id)::integer 
          FROM pollster_dashboard_neighborhood_users($1);	
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION pollster_dashboard_neighborhood_users_avg(
        text -- $1 zip_code_key
) RETURNS decimal
AS  $$
        SELECT  avg(n) FROM (
                SELECT count(DISTINCT global_id) n, zip_code_key 
                FROM pollster_dashboard_neighborhood_users('10123') 
            GROUP BY 2) A;	
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION pollster_dashboard_users_by_zip_code(
        text -- $1 zip_code_key
) RETURNS TABLE (
  "user"       integer,
  global_id     text,
  zip_code_key  text,
  "timestamp"     timestamptz
)
AS  $$
        SELECT I."user", 
               I.global_id, 
               I."Q3" AS zip_code_key,
               I.timestamp 
        FROM pollster_results_intake I 
       WHERE (I."Q3" = $1);
	
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION pollster_dashboard_users_by_zip_code_count(
        text -- $1 zip_code_key
) RETURNS integer
AS  $$
        SELECT count(DISTINCT global_id)::integer 
          FROM pollster_dashboard_users_by_zip_code($1);	
$$ LANGUAGE SQL;

DROP VIEW IF EXISTS pollster_dashboard_neighbors;
CREATE VIEW pollster_dashboard_neighbors AS
        SELECT DISTINCT O.global_id, O."user",
	        pollster_dashboard_users_by_zip_code_count(O."Q3") AS same_zip_count,
		pollster_dashboard_neighborhood_users_count(O."Q3") AS neighbors_count, 
		pollster_dashboard_neighborhood_users_avg(O."Q3") AS neighbors_avg
           FROM pollster_dashboard_last_intake O;

