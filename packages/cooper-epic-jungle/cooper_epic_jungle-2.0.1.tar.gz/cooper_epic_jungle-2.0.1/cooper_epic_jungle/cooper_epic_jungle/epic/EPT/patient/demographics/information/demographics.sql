 SET NOCOUNT ON;

IF OBJECT_ID('tempdb.dbo.#MRN', 'U') IS NOT NULL
  DROP TABLE #MRN;

DECLARE @MRN TABLE
(
	MRN NVARCHAR(50)
)

-- INSERTION CLAUSES
{{ MRN }};
--INSERT INTO @CSN (CSN) VALUES('1020254742')

SELECT * 
INTO #MRN
FROM @MRN;

SELECT 
	  [MRN]
	  ,CONVERT(DATE,PAT.BIRTH_DATE) as DOB
	  ,ZSX.NAME as gender
	  ,zpr.NAME as race
	  ,ZEG.NAME as ethnicity

FROM 
		#MRN as MRNS
		INNER JOIN Clarity.dbo.PATIENT AS PAT ON PAT.PAT_MRN_ID = MRNS.MRN
		LEFT JOIN (clarity.dbo.patient_race pr join clarity.dbo.zc_patient_race zpr on pr.patient_race_c = zpr.patient_race_c)
					on pat.pat_id = pr.pat_id and pr.line = 1
		LEFT JOIN Clarity.dbo.ZC_SEX as ZSX ON ZSX.RCPT_MEM_SEX_C = PAT.SEX_C
		LEFT JOIN Clarity.dbo.ZC_ETHNIC_GROUP as ZEG ON ZEG.ETHNIC_GROUP_C = PAT.ETHNIC_GROUP_C

