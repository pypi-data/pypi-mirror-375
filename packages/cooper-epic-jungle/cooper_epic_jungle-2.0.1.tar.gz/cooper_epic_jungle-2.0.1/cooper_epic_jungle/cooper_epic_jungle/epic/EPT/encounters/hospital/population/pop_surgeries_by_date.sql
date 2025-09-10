/*
pop_surgeries_by_date: Given an optional number of parameters, get completed surgical encounters based on surgery date, or surgery date and additional parameters.
					   Returns both encounter and surgery CSNs, be sure to rename the correct one if sending CSNs through more info scripts.
author: Alex Moore
date: 2024-11-12 
jinja parameters: {'date_start': date str
					,'date_end': date str
					,'filt_surg_serv': list of surgical services
					,'filt_location': list of location os surgeries
					,'filt_prim_surg': list of primary surgeons by PROV_ID
					,'filt_resp_anes': list of responsible anesthesiologists by PROV_ID
					,'filt_cpt_codes': list of cpt codes
					,'include_details': bool to show more than basic columns
					}
*/

DECLARE @start_date DATE, @end_date DATE

SET @start_date = '{{ date_start }}'  
SET @end_date = '{{ date_end }}';


SELECT DISTINCT
		ORL.LOG_ID AS LOG_ID
		,ORCA.OR_CASE_ID AS CASE_ID
		,PAT.PAT_ID
		,POAL.OR_LINK_CSN AS encounter_CSN
		,POAL.PAT_ENC_CSN_ID AS surgery_CSN
		,HSP.HSP_ACCOUNT_ID AS HAR
		,hsp.HOSP_ADMSN_TIME AS admission_dttm
		,hsp.HOSP_DISCH_TIME AS discharge_dttm
		,ORCA.SURGERY_DATE AS surgery_date
		{% if include_details %}
		,ZOS.NAME AS surgical_service
		,LOC.LOC_NAME AS or_location
		,SRG_SER.PROV_NAME AS primary_surgeon
		,ANS_SER.PROV_NAME AS responsible_anes
		,OPROC.OR_PROC_ID AS cpt_code -- NEED TO REVISIT LATER FOR SURGERIES BEFORE 2021
		,OPROC.PROC_NAME AS or_procedure_name
		,room.PROV_NAME AS or_room
		,FLB.IN_OR_DTTM AS wheels_in_dttm
		,FLB.PROCEDURE_START_DTTM AS proc_start_dttm
		,FLB.PROCEDURE_COMP_DTTM AS proc_end_dttm
		,FLB.OUT_OR_DTTM as wheels_out_dttm
		,FLB.NUMBER_OF_PROCEDURES AS num_of_procs
		,ZOAT.NAME AS primary_anes_type
		,ZOL.NAME AS laterality
		,ZOCC.NAME AS case_class
		,ZOAR.NAME AS asa_rating
		,DATEDIFF(HOUR, pat.birth_date, ORCA.SURGERY_DATE)/8766 AS age_at_surgery
		,CASE WHEN pat.DEATH_DATE > hsp.HOSP_DISCH_TIME THEN hsp.HOSP_DISCH_TIME ELSE pat.DEATH_DATE END AS death_date
		,DATEDIFF(HOUR, ORCA.SURGERY_DATE, CASE WHEN pat.DEATH_DATE > hsp.HOSP_DISCH_TIME THEN hsp.HOSP_DISCH_TIME ELSE pat.DEATH_DATE END )/8766 AS days_from_surg_to_death
		{% endif %}
FROM 
[Clarity].[dbo].OR_LOG AS ORL
INNER JOIN [Clarity].[dbo].F_LOG_BASED AS FLB 
ON FLB.LOG_ID = ORL.LOG_ID
INNER JOIN [Clarity].[dbo].patient AS PAT 
ON PAT.PAT_ID = ORL.PAT_ID
INNER JOIN [Clarity].[dbo].OR_LOG_VIRTUAL AS OLV 
ON OLV.LOG_ID = ORL.LOG_ID
INNER JOIN [Clarity].[dbo].OR_PROC AS OPROC 
ON OPROC.OR_PROC_ID = OLV.PRIMARY_PROC_ID
INNER JOIN [Clarity].[dbo].OR_CASE AS ORCA 
ON ORL.case_id = ORCA.OR_CASE_ID 
LEFT JOIN [Clarity].[dbo].PAT_OR_ADM_LINK AS POAL 
ON POAL.CASE_ID = ORL.CASE_ID
LEFT JOIN [Clarity].[dbo].PAT_ENC_HSP AS HSP 
ON POAL.OR_LINK_INP_ID = HSP.INPATIENT_DATA_ID
LEFT JOIN [Clarity].[dbo].CLARITY_LOC AS LOC 
ON LOC.LOC_ID = ORL.LOC_ID
LEFT JOIN [Clarity].[dbo].CLARITY_SER AS SRG_SER 
ON SRG_SER.PROV_ID = ORL.PRIMARY_PHYS_ID
LEFT JOIN [Clarity].[dbo].CLARITY_SER AS ANS_SER 
ON ANS_SER.PROV_ID = FLB.RESP_ANES_ID
LEFT JOIN [Clarity].[dbo].ZC_OR_LRB AS ZOL 
ON ZOL.LRB_C = OPROC.LRB_C 
LEFT JOIN [Clarity].[dbo].ZC_PROC_NOT_PERF AS ZPNP 
ON ZPNP.PROC_NOT_PERF_C = ORL.PROC_NOT_PERF_C
LEFT JOIN [Clarity].[dbo].ZC_OR_SCHED_STATUS AS ZOSS 
ON ZOSS.SCHED_STATUS_C = ORCA.SCHED_STATUS_C
LEFT JOIN [Clarity].[dbo].ZC_OR_CASE_CLASS AS ZOCC 
ON ZOCC.CASE_CLASS_C = ORL.CASE_CLASS_C
LEFT JOIN [Clarity].[dbo].ZC_OR_ASA_RATING as ZOAR 
ON ZOAR.ASA_RATING_C = ORL.ASA_RATING_C
LEFT JOIN [Clarity].[dbo].ZC_OR_SERVICE AS ZOS 
ON ZOS.SERVICE_C = ORL.SERVICE_C
LEFT JOIN [Clarity].[dbo].ZC_OR_ANESTH_TYPE AS ZOAT 
ON ZOAT.ANESTHESIA_TYPE_C = FLB.PRIMARY_ANES_TYPE_C
LEFT JOIN [Clarity].[dbo].CLARITY_SER AS room 
ON room.PROV_ID = ORL.ROOM_ID

WHERE  
ZOSS.NAME = 'Completed' 
AND CONVERT(DATE,ORL.SURGERY_DATE) BETWEEN @start_date AND @end_date
{% if filt_surg_serv %}
AND ZOS.NAME IN {{ filt_surg_serv|inclause_str }}
{% endif %}
{% if filt_location %}
AND LOC.LOC_NAME IN {{ filt_location|inclause_str }}
{% endif %}
{% if filt_prim_surg %}
AND SRG_SER.PROV_ID IN {{ filt_prim_surg|inclause_str }}
{% endif %}
{% if filt_resp_anes %}
AND ANS_SER.PROV_ID IN {{ filt_resp_anes|inclause_str }} 
{% endif %}
{% if filt_cpt_codes %}
AND OPROC.OR_PROC_ID IN {{ filt_cpt_codes|inclause_str }}
{% endif %}

OPTION (RECOMPILE)