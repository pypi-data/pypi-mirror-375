/*
pop_scheduled_surgeries_by_date: Given an optional number of parameters, get completed surgical encounters based on surgery date, or surgery date and additional parameters.
								 
author: Alex Moore, Tem Nanna
date: 2024-11-12 
jinja parameters: {'date_start': date str
					,'date_end': date str
					,'filt_surg_serv': list of surgical services
					,'filt_location': list of location os surgeries
					,'filt_prim_surg': list of primary surgeons by PROV_ID
					,'include_details': bool to show more than basic columns
					,'include_cancelled': bool to show cancelled surgeries
					}
*/

DECLARE @start_date DATE
DECLARE @end_date DATE

SET @start_date = '{{ date_start }}'
SET @end_date = '{{ date_end }}';

SELECT DISTINCT
				ORCA.OR_CASE_ID AS CASE_ID
				,pat.PAT_ID
				,ORCA.SURGERY_DATE surgery_date
                                {% if include_cancelled %}
                                ,ZOSS.NAME AS or_scheduled_status
                                ,zocr.NAME AS cancelled_reason
                                {% endif %}
				{% if include_details %}
				,ORCA.RECORD_CREATE_DATE AS case_created_dttm
				,ZOS.NAME AS surgical_service
				,OPROC.PROC_DISPLAY_NAME AS or_procedure_name
				,LOC.LOC_NAME AS or_location
				,ZPC.NAME AS scheduled_patient_class
				,ZOCC.NAME AS case_class
				,SRG_SER.PROV_NAME AS primary_surgeon
				,DATEDIFF(HOUR, pat.birth_date, ORCA.SURGERY_DATE)/8766 AS age_at_surgery
				{% endif %}
FROM OR_CASE AS ORCA
JOIN PATIENT AS PAT 
ON PAT.PAT_ID = ORCA.PAT_ID
LEFT JOIN OR_CASE_ALL_PROC AS OPROC 
ON OPROC.OR_CASE_ID = ORCA.OR_CASE_ID 
AND OPROC.LINE = 1
LEFT JOIN OR_PROC AS ORP 
ON ORP.OR_PROC_ID = OPROC.OR_PROC_ID 
LEFT JOIN CLARITY_LOC AS LOC 
ON LOC.LOC_ID = ORCA.LOC_ID
LEFT JOIN CLARITY_SER AS SRG_SER 
ON SRG_SER.PROV_ID = ORCA.PRIMARY_PHYSICIAN_ID
LEFT JOIN ZC_OR_SCHED_STATUS AS ZOSS 
ON ZOSS.SCHED_STATUS_C = ORCA.SCHED_STATUS_C
LEFT JOIN ZC_OR_CASE_CLASS AS ZOCC 
ON ZOCC.CASE_CLASS_C = ORCA.CASE_CLASS_C
LEFT JOIN ZC_OR_SERVICE AS ZOS 
ON ZOS.SERVICE_C = ORCA.SERVICE_C
LEFT JOIN CLARITY_SER AS room 
ON room.PROV_ID = ORCA.OR_ID
LEFT JOIN ZC_PAT_CLASS AS ZPC 
ON ZPC.ADT_PAT_CLASS_C = ORCA.PAT_CLASS_C
LEFT JOIN ZC_OR_CANCEL_RSN zocr
ON zocr.CANCEL_REASON_C = ORCA.CANCEL_REASON_C
WHERE CONVERT(DATE,ORCA.SURGERY_DATE) BETWEEN @start_date AND @end_date
{% if filt_surg_serv %}
AND ZOS.NAME IN {{ filt_surg_serv|inclause_str }}
{% endif %}
{% if filt_location %}
AND LOC.LOC_NAME IN {{ filt_location|inclause_str }}
{% endif %}
{% if filt_prim_surg %}
AND SRG_SER.PROV_ID IN {{ filt_prim_surg|inclause_str }}
{% endif %}
{% if include_cancelled %}
{% else %}
AND ZOSS.NAME = 'Scheduled'
AND ORCA.CANCEL_DATE IS NULL
{% endif %}
ORDER BY orca.SURGERY_DATE
OPTION(RECOMPILE)
