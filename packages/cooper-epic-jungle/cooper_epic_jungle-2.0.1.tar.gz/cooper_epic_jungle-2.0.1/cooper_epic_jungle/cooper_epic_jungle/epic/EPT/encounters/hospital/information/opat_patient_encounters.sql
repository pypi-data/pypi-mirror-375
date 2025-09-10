/*
Description: Script identifies outpatient parenteral antimicrobial therapy patients (OPAT) from the PAT_ENC_HSP table.
             Information script takes CSN.

Authors: Temi Nanna
*/

SET NOCOUNT ON
;

IF OBJECT_ID('tempdb..#CSN') IS NOT NULL
	DROP TABLE #CSN;

DECLARE @CSN TABLE
(
	CSN NVARCHAR(50)
)

{{CSN}}


SELECT * 
INTO #CSN
FROM @CSN
;

SELECT DISTINCT 
	hospital_encounters.PAT_ENC_CSN_ID AS CSN
       ,opat_patient = 1

FROM 
	Clarity.dbo.PAT_ENC_HSP AS hospital_encounters
	INNER JOIN Clarity.dbo.PATIENT AS patients 
	ON hospital_encounters.PAT_ID 
	 = patients.PAT_ID

	INNER JOIN #CSN AS temp_tbl_csns 
	ON temp_tbl_csns.CSN
	 = hospital_encounters.PAT_ENC_CSN_ID

	INNER JOIN clarity.dbo.smrtdta_elem_data AS data_elements 
	ON hospital_encounters.PAT_ENC_CSN_ID 
	 = data_elements.contact_serial_num
	AND data_elements.ELEMENT_ID = 'COOPER#711'

	INNER JOIN clarity.dbo.smrtdta_elem_value AS data_element_values 
	ON data_elements.HLV_ID 
	 = data_element_values.HLV_ID
	AND data_element_values.LINE = '1'

OPTION(RECOMPILE);

IF OBJECT_ID('tempdb..#CSN') IS NOT NULL
	DROP TABLE #CSN

