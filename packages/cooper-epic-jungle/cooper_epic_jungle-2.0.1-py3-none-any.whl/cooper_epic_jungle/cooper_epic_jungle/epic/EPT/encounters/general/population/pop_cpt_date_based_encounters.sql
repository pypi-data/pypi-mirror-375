/*
Description: Get encounters by CPT code list
             ONLY WORKS WHEN GIVEN CPTs
Author: Alex Moore, Justin Frisby, Arnold McGee
Jungle Location: epic/EPT/encounters/hosptial/pop/
Parameters: date_start = date str
			; date_end = date str
			; filt_cpt_codes = list of CPT codes
*/

SET NOCOUNT ON;

DECLARE @start_date DATE
SET @start_date = '{{ date_start }}'  
DECLARE @end_date DATE
SET @end_date = '{{ date_end }}' ; 


SELECT patient.PAT_ID
		,hsp_account.PRIM_ENC_CSN_ID AS encounter_CSN
		,arpb_transactions_chrg.PAT_ENC_CSN_ID AS service_CSN
		,COALESCE(hsp_account.PRIM_ENC_CSN_ID,arpb_transactions_chrg.PAT_ENC_CSN_ID) AS CSN
		,CASE WHEN hsp_account.PRIM_ENC_CSN_ID IS NULL THEN 'Service CSN' ELSE 'Encounter CSN' END AS csn_type
	   ,clarity_tdl_tran.account_id as HAR 
	   ,clarity_tdl_tran.visit_number as visit_number
	   ,clarity_tdl_tran.cpt_code
	   ,clarity_tdl_tran.ORIG_SERVICE_DATE AS service_date
FROM clarity_tdl_tran AS clarity_tdl_tran
LEFT JOIN ARPB_TRANSACTIONS AS arpb_transactions_chrg 
ON clarity_tdl_tran.TX_ID = arpb_transactions_chrg.tx_id
AND arpb_transactions_chrg.tx_type_c = 1 --Charges    
LEFT JOIN v_arpb_tx_activity AS v_arpb_tx_activity 
ON clarity_tdl_tran.tdl_id = v_arpb_tx_activity.tdl_id --View to bring attributes   
LEFT JOIN patient AS patient 
ON v_arpb_tx_activity.pat_id = patient.pat_id  --Patient    
LEFT JOIN clarity_eap AS clarity_eapc 
ON arpb_transactions_chrg.PROC_ID = clarity_eapc.PROC_ID
LEFT JOIN hsp_account AS hsp_account 
ON arpb_transactions_chrg.visit_number = hsp_account.hsp_account_id
LEFT JOIN zc_acct_billsts_ha AS zc_acct_billsts_ha 
ON hsp_account.acct_billsts_ha_c = zc_acct_billsts_ha.acct_billsts_ha_c
WHERE 
	1=1
	AND arpb_transactions_chrg.void_date IS NULL    --Excludes charges which are voided
	AND RIGHT(clarity_tdl_tran.cpt_code,5) IN {{ filt_cpt_codes|inclause_str }} 	
	AND clarity_tdl_tran.cpt_code NOT LIKE '[a-Z]%%'
	AND clarity_tdl_tran.detail_type IN (1)
	AND clarity_tdl_tran.ORIG_SERVICE_DATE BETWEEN @start_date and @end_date


OPTION(RECOMPILE)