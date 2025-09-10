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


WITH csn_tx AS (SELECT c.CSN
						,srvc.PAT_ENC_CSN_ID AS srvc_csn
						,srvc.TX_ID AS srvc_tx_id
				FROM #CSN c
				LEFT JOIN ARPB_TRANSACTIONS AS srvc
				ON srvc.PAT_ENC_CSN_ID = c.CSN 
				),
	 csn_hsp AS (SELECT c.CSN
						 ,ha.PRIM_ENC_CSN_ID AS prim_csn
						 ,prim.TX_ID AS prim_tx_id
				 FROM #CSN c
				 LEFT JOIN PAT_ENC e
				 ON c.CSN = e.PAT_ENC_CSN_ID
				 LEFT JOIN HSP_ACCOUNT ha
				 ON ha.HSP_ACCOUNT_ID = e.HSP_ACCOUNT_ID
				 LEFT JOIN ARPB_TRANSACTIONS AS prim
				 ON prim.VISIT_NUMBER = ha.HSP_ACCOUNT_ID
				),
	 csns AS (SELECT c.CSN
					 ,hsp.prim_csn
					 ,tx.srvc_csn
					 ,COALESCE(hsp.prim_csn,tx.srvc_csn) AS pb_csn
					 ,COALESCE(hsp.prim_tx_id,tx.srvc_tx_id) AS pb_tx_id
					 ,hsp.prim_tx_id
					 ,tx.srvc_tx_id
			  FROM #CSN c
			  LEFT JOIN csn_tx tx
			  ON tx.CSN = c.CSN
			  LEFT JOIN csn_hsp hsp
			  ON hsp.CSN = c.CSN
			 )
--select * from csns
SELECT   
		COALESCE(PRIMARY_CSN,finalqry.CSN) AS CSN
        --,finalqry.account_id AS HAR
		,CASE WHEN PRIMARY_CSN IS NOT NULL THEN 'Encounter CSN' ELSE 'Service CSN' END AS csn_type
        ,finalqry.visit_number
        ,CASE WHEN finalqry.original_payor_id = '99999'
                             THEN 'SELF PAY'
                             ELSE finalqry.original_plan_name
                             END insurance_plan_name
        ,finalqry.original_financial_class
        ,finalqry.current_plan_name "Current Plan Name"
        ,finalqry.current_financial_class
		,finalqry.service_date
		,PROV_NAME AS service_provider
		,prov_type AS service_provider_type
        ,finalqry.cpt_code AS cpt_code
        ,finalqry.cpt_code_name AS cpt_code_name
        ,MAX(finalqry.MODIFIER_ONE) AS cpt_modifier1
        ,MAX(finalqry.MODIFIER_TWO) AS cpt_modifier2
        ,MAX(finalqry.MODIFIER_THREE) AS cpt_modifier3
        ,MAX(finalqry.MODIFIER_FOUR) AS cpt_modifier4
        ,finalqry.visit_account_billed_status AS billed_status
	,finalqry.Status AS account_status
        ,RN_RANK = ROW_NUMBER() OVER (PARTITION BY 
												finalqry.pat_mrn_id, 
												finalqry.cpt_code,
												finalqry.account_id
									  ORDER BY	
												 CASE WHEN prov_type = 'Physician' THEN 10 ELSE 5 END DESC
												,finalqry.service_date
												,finalqry.charge_amount DESC
												,finalqry.visit_number)
																			
                                
FROM (
			SELECT       
								 clarity_tdl_tran.account_id as account_id
                                ,clarity_tdl_tran.visit_number as visit_number
                                ,v_arpb_tx_activity.PAT_NAME as patient_name
                                ,convert(varchar, patient.BIRTH_DATE,101) as patient_dob
                                ,patient.PAT_MRN_ID as pat_mrn_id
                                ------------------Coverages------------------------
								,v_coverage_payor_plan_orig.PAYOR_ID as original_payor_id
                                ,v_coverage_payor_plan_orig.FIN_CLASS_NAME as original_financial_class
                                ,v_coverage_payor_plan_orig.BENEFIT_PLAN_NAME as original_plan_name
                                ,isnull(v_coverage_payor_plan_current.benefit_plan_name,'SELF PAY') as current_plan_name
                                ,isnull(v_coverage_payor_plan_current.FIN_CLASS_NAME, 'SELF PAY') as current_financial_class
                                ,clarity_tdl_tran.cpt_code
                                ,clarity_tdl_tran.MODIFIER_ONE
                                ,clarity_tdl_tran.MODIFIER_TWO
                                ,clarity_tdl_tran.MODIFIER_THREE
                                ,clarity_tdl_tran.MODIFIER_FOUR
								,arpb_transactions_chrg.PAT_ENC_CSN_ID CSN
								,hsp_account.PRIM_ENC_CSN_ID as PRIMARY_CSN
								,arpb_transactions_chrg.service_date
								,arpb_transactions_chrg.AMOUNT as charge_amount
								,clarity_ser.PROV_NAME
								,clarity_ser.PROV_TYPE
                                ,clarity_eapc.PROC_NAME as cpt_code_name
                                ,convert(varchar,hsp_account.ACCT_BILLSTS_HA_C)+' - '+zc_acct_billsts_ha.name as visit_account_billed_status
                                ,CASE WHEN arpb_tx_moderate.AR_CLASS_C  = 2 THEN 'Ext BD' ELSE NULL END AS "Status"
                                

	FROM csns c
	LEFT JOIN clarity.dbo.clarity_tdl_tran AS clarity_tdl_tran
	ON clarity_tdl_tran.TX_ID = c.pb_tx_id
	LEFT JOIN clarity.dbo.ARPB_TRANSACTIONS AS arpb_transactions_pmnt on 
                                    (clarity_tdl_tran.MATCH_TRX_ID = arpb_transactions_pmnt.tx_id 
									 AND arpb_transactions_pmnt.tx_type_c = 2) --Payments
	LEFT OUTER JOIN clarity.dbo.ARPB_TRANSACTIONS AS arpb_transactions_chrg on (clarity_tdl_tran.TX_ID = arpb_transactions_chrg.tx_id
																				AND arpb_transactions_chrg.tx_type_c = 1) --Charges    
    LEFT OUTER JOIN clarity.dbo.v_arpb_tx_activity AS v_arpb_tx_activity on (clarity_tdl_tran.tdl_id = v_arpb_tx_activity.tdl_id) --View to bring attributes   
    LEFT OUTER JOIN clarity.dbo.patient AS patient on (v_arpb_tx_activity.pat_id = patient.pat_id)  --Patient    
    LEFT OUTER JOIN clarity.dbo.V_COVERAGE_PAYOR_PLAN AS v_coverage_payor_plan_current on (arpb_transactions_chrg.coverage_id = v_coverage_payor_plan_current.coverage_id)
    LEFT OUTER JOIN clarity.dbo.V_COVERAGE_PAYOR_PLAN AS v_coverage_payor_plan_orig on (arpb_transactions_chrg.ORIGINAL_CVG_ID = v_coverage_payor_plan_orig.coverage_id)   
    LEFT OUTER JOIN clarity.dbo.ARPB_TX_MATCH_HX AS arpb_tx_match_hx on 
                                    (arpb_transactions_chrg.TX_ID = arpb_tx_match_hx.MTCH_TX_HX_ID 
                                        AND arpb_transactions_pmnt.tx_id = arpb_tx_match_hx.tx_id) --Payment  
    LEFT OUTER JOIN clarity.dbo.clarity_eap AS clarity_eapc on (arpb_transactions_chrg.PROC_ID = clarity_eapc.PROC_ID) 
    LEFT OUTER JOIN clarity.dbo.hsp_account AS hsp_account on (arpb_transactions_chrg.visit_number = hsp_account.hsp_account_id)
    LEFT OUTER JOIN clarity.dbo.zc_acct_billsts_ha AS zc_acct_billsts_ha on (hsp_account.acct_billsts_ha_c = zc_acct_billsts_ha.acct_billsts_ha_c)
    LEFT OUTER JOIN clarity.dbo.ARPB_TX_MODERATE AS arpb_tx_moderate on (arpb_transactions_chrg.tx_id = arpb_tx_moderate.tx_id)
    LEFT OUTER JOIN clarity.dbo.CLARITY_SER AS clarity_ser on (clarity_ser.PROV_ID = v_arpb_tx_activity.SERVICE_PROV_ID) 

	WHERE 
	1=1
	AND arpb_transactions_chrg.void_date IS NULL    --Excludes charges which are voided
	AND arpb_transactions_pmnt.VOID_DATE IS NULL      --Excludes payment 
	AND arpb_tx_match_hx.MTCH_TX_HX_UN_DT IS NULL  --Excludes unmatched adjustments and payments
	AND clarity_tdl_tran.detail_type IN (1,20,21)
	--AND COALESCE(hsp_account.PRIM_ENC_CSN_ID,arpb_transactions_chrg.PAT_ENC_CSN_ID) IN (SELECT CSN FROM #CSN)

	) finalqry
WHERE 1=1
GROUP BY --finalqry.ACCOUNT_ID
                                finalqry.VISIT_NUMBER
                                ,finalqry.patient_name
                                ,finalqry.patient_dob 
                                ,finalqry.pat_mrn_id
								 ,finalqry.PROV_NAME
                                ,finalqry.original_payor_id
								,finalqry.original_financial_class
								,finalqry.current_financial_class
                                ,finalqry.original_plan_name
								,finalqry.PROV_TYPE
                                ,finalqry.current_plan_name
                                ,finalqry.cpt_code
								,finalqry.service_date
                                ,finalqry.cpt_code_name
                                ,finalqry.visit_account_billed_status
                                ,finalqry.Status 
                                ,finalqry.CSN
								,finalqry.PRIMARY_CSN
								,finalqry.charge_amount

ORDER BY finalqry.pat_mrn_id, finalqry.VISIT_NUMBER, finalqry.charge_amount DESC
OPTION(RECOMPILE)
