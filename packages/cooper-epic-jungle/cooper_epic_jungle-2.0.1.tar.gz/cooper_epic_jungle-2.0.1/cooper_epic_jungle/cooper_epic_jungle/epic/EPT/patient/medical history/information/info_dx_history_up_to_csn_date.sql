/*
Historical DX's up to given encounter date

Description: The config file will return a list of diagnoses recorded on the problem list (PROBLEM_LIST) and/or medical history (MEDICAL_HX)
tables, given an encounter's date as an anchor and an optional list of DX ids to check for. 
Author: Justin Frisby, Alex Moore

Parameters: {'filts_icd': None
              }
*/

SET NOCOUNT ON;
IF OBJECT_ID('tempdb.dbo.#CSN', 'U') IS NOT NULL
  DROP TABLE #CSN; 

DECLARE @CSN TABLE
(
	CSN NVARCHAR(50)
)

-- INSERTION CLAUSES
{{ CSN }};
;

SELECT * 
INTO #CSN
FROM @CSN;

WITH csn AS (
				SELECT c.CSN
						,e.PAT_ID
						,CONVERT(DATE,e.CONTACT_DATE) AS contact_date
				FROM #CSN c
				JOIN PAT_ENC e
				ON c.CSN = e.PAT_ENC_CSN_ID

			)

			, dx AS (
					SELECT edg.dx_id
							, edg.dx_name
							, edg.current_icd10_list
					FROM clarity.dbo.clarity_edg edg
					JOIN Clarity.dbo.EDG_CURRENT_ICD10 AS icd
					ON edg.DX_ID = icd.DX_ID
					AND EC_INACTIVE_YN = 'N'
					
					{% if filts_icd %}
					WHERE 

					{% for dx_cat, list_of_dxs in filts_icd.items() %}
						{% for dx in list_of_dxs %}
							{% if dx_cat == filts_icd.keys()|first and dx == list_of_dxs|first: %}
					EDG.CURRENT_ICD10_LIST LIKE '%%{{dx}}%%'
							{% else %}
							OR EDG.CURRENT_ICD10_LIST LIKE '%%{{dx}}%%'
							{% endif %}
						{% endfor %}
					{% endfor %}

					{% endif %}
					
			),
			stg AS
			(
				SELECT pl.pat_id,
						d1.dx_id, 
						d1.current_icd10_list,
						COALESCE(NOTED_DATE,DATE_OF_ENTRY) AS DX_DATE, 
						1 as summing
				FROM Clarity.dbo.PROBLEM_LIST pl
				JOIN dx AS d1
				ON d1.DX_ID = pl.DX_ID
				JOIN csn c 
				ON c.PAT_ID = pl.PAT_ID
				AND CONVERT(DATE,pl.NOTED_DATE) <= c.contact_date

				UNION ALL

				SELECT	pl.pat_id,
						d1.dx_id, 
						d1.current_icd10_list,
						COALESCE(pl.MED_HX_START_DT,pl.CONTACT_DATE) MED_HX_DATE, 
						1 as summing
						
				FROM Clarity.dbo.medical_hx pl
				JOIN dx AS d1 
				ON d1.DX_ID = pl.DX_ID
				JOIN csn c
				ON c.PAT_ID = pl.PAT_ID
				AND CONVERT(DATE,COALESCE(pl.MED_HX_START_DT,pl.CONTACT_DATE)) <= c.contact_date
			)
SELECT  --c.PAT_ID
		c.CSN
		--,p.PAT_MRN_ID AS MRN
		{% if filts_icd %}

		{% for dx_cat, list_of_dxs in filts_icd.items(): %}
			{% if list_of_dxs|length == 1: %}
                    ,MAX(CASE WHEN stg.current_icd10_list LIKE '%%{{list_of_dxs[0]}}%%' THEN 1 ELSE 0 END) AS [Has_{{dx_cat|title()}}_In_Dx]
            {% else: %}
				{%  for dx in range(0,list_of_dxs|length): %}
					{% if dx == 0: %}
                            ,MAX(CASE WHEN stg.current_icd10_list LIKE '%%{{list_of_dxs[dx]}}%%'
                    {% else: %}
                             OR stg.current_icd10_list LIKE '%%{{list_of_dxs[dx]}}%%'
                    {% endif %}
                {% endfor %}
                    THEN 1 ELSE 0 END) AS  [Has_{{dx_cat|title()}}_In_Dx]
            {% endif %}
        {% endfor %}
        {% endif %}
		--,MIN(stg.DX_DATE) as "First Dx Date"
		--,stg.DX_ID
		--,CASE WHEN SUM(summing) > 0 THEN 1 else 0 END as dx_chk
FROM csn c
LEFT JOIN stg 
ON stg.pat_id = c.pat_id
LEFT JOIN PATIENT p
ON c.PAT_ID = p.PAT_ID
GROUP BY --c.PAT_ID
			c.CSN
			--,p.PAT_MRN_ID
			,stg.DX_ID

OPTION (RECOMPILE)