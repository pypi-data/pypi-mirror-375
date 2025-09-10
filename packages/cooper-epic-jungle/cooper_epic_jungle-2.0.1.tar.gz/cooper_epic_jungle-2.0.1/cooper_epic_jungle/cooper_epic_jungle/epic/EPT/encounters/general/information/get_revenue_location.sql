SET NOCOUNT ON;

IF OBJECT_ID('tempdb.dbo.#CSN', 'U') IS NOT NULL
  DROP TABLE #CSN;

DECLARE @CSN TABLE
(
	CSN NVARCHAR(50)
)

-- INSERTION CLAUSES
{{ CSN }};

SELECT *
INTO #CSN
FROM @CSN;

WITH 
cape_deps as
(
SELECT 
		DEP.DEPARTMENT_ID, 
		--DEP.DEPARTMENT_NAME, 
		parent_location.LOC_NAME as DEP41000_hospital_parent_location, 
		rev_location.LOC_NAME as DEP4001_revenue_location, 
		eaf_rev_location.LOC_NAME as EAF_networked_rev_loc_parent_location
FROM 
		Clarity.dbo.CLARITY_DEP dep
		JOIN Clarity.dbo.CLARITY_DEP_4 AS dep_4
		ON dep_4.DEPARTMENT_ID
		 = dep.DEPARTMENT_ID
		JOIN Clarity.dbo.CLARITY_LOC AS parent_location
		ON parent_location.LOC_ID
		 = dep_4.HOSP_PARENT_LOC_ID
		JOIN  Clarity.dbo.CLARITY_LOC AS rev_location
		ON dep.REV_LOC_ID
		 = rev_location.LOC_ID
		JOIN Clarity.dbo.CLARITY_LOC AS eaf_rev_location
		ON eaf_rev_location.LOC_ID
		 = rev_location.HOSP_PARENT_LOC_ID
WHERE 
		parent_location.loc_id = '3101001' -- CAPE REGIONAL PARENT HOSPITAL
		OR
		rev_location.loc_id = '3101001' -- CAPE REGIONAL PARENT HOSPITAL
		OR
		eaf_rev_location.loc_id = '3101001' -- CAPE REGIONAL PARENT HOSPITAL
		OR
		dep.DEPARTMENT_ID IN ('311017902','311025104','311023801',
						   '311024601','311017201','311025401')
)
,
enc AS (
        SELECT c.CSN
                ,enc.DEPARTMENT_ID
                ,CASE WHEN enc.DEPARTMENT_ID IN (SELECT DEPARTMENT_ID FROM cape_deps) THEN 1 ELSE 0 END as CAPE_FLAG

        FROM #CSN c
        JOIN Clarity.dbo.PAT_ENC enc
        ON enc.PAT_ENC_CSN_ID
         = c.CSN
        JOIN Clarity.dbo.CLARITY_DEP dep
        ON enc.DEPARTMENT_ID = dep.DEPARTMENT_ID
        ),
     hsp AS (
        SELECT c.CSN
                ,hsp.DEPARTMENT_ID
                ,CASE WHEN hsp.DEPARTMENT_ID IN (SELECT DEPARTMENT_ID FROM cape_deps) THEN 1 ELSE 0 END as CAPE_FLAG
        FROM #CSN c
        JOIN Clarity.dbo.PAT_ENC_HSP hsp
        ON hsp.PAT_ENC_CSN_ID
         = c.CSN
        JOIN Clarity.dbo.CLARITY_DEP dep
        ON hsp.DEPARTMENT_ID = dep.DEPARTMENT_ID

        ),
     adt AS (
        SELECT c.CSN
                ,adt.DEPARTMENT_ID
                ,CASE WHEN adt.DEPARTMENT_ID IN (SELECT DEPARTMENT_ID FROM cape_deps) THEN 1 ELSE 0 END as CAPE_FLAG
        FROM #CSN c
        JOIN Clarity.dbo.CLARITY_ADT adt
        ON c.CSN = adt.PAT_ENC_CSN_ID
		AND ADT.event_type_c = 1
        JOIN Clarity.dbo.CLARITY_DEP dep
        ON dep.DEPARTMENT_ID = adt.DEPARTMENT_ID
        )
		

SELECT
CSN,
CASE WHEN SUM(CAPE_FLAG) >= 1 THEN 'CAPE' ELSE 'CAMDEN' END as revenue_location

FROM

(
SELECT * FROM enc
UNION ALL
SELECT * FROM adt
UNION ALL
SELECT * FROM hsp
) as inner_deps

GROUP BY CSN
