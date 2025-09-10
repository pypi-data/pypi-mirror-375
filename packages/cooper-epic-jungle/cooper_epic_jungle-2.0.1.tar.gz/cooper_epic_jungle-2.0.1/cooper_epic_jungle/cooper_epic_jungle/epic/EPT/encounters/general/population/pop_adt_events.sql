/*
pop_adt_events: Given an optional number of parameters, get adt events.
author: Alex Moore, Justin Frisby
date: 2024-11-12 
jinja parameters: {'date_start': date str
					,'date_end': date str
					,'filt_depts': list of department names for transfer in
					,'filt_pat_class': list of patient classes for transfer in
                                        ,'filt_event_type': list of event types; only "Admission," "Transfer In," 
                                                            and "Patient Update" are available
                                        ,'filt_service': list of adt pat service names for tranfer in

					}
*/

DECLARE @date_start DATE, @date_end DATE

SET @date_start = '{{ date_start }}'
SET @date_end = '{{ date_end }}';

SELECT 
		 ADT_IN.EVENT_ID
		,HSP.PAT_ENC_CSN_ID AS CSN
		,PAT.PAT_MRN_ID AS MRN
		,PAT.PAT_NAME AS patient_name
		,HSP.ADT_ARRIVAL_TIME AS hospital_arrival_datetime
		,HSP.ED_DISP_TIME AS ed_disposition_datetime
		--,MIN(ORDP.ORDER_INST) OVER (PARTITION BY HSP.PAT_ENC_CSN_ID) as admission_order_datetime
		,HSP.ED_DEPARTURE_TIME AS ed_departure_datetime
		,HSP.HOSP_ADMSN_TIME AS admission_datetime
		,HSP.HOSP_DISCH_TIME AS discharge_datetime
		,ZC_EVENT_TYPE.NAME AS event_type
		,ADT_IN.EFFECTIVE_TIME AS event_effective_dttm
		,CASE WHEN ZC_EVENT_TYPE.NAME IN ('Transfer In','Admission') THEN  ADT_IN.EFFECTIVE_TIME END AS transfer_in_dttm
		,CASE WHEN ZC_EVENT_TYPE.NAME IN ('Transfer In','Admission') THEN  ADT_OUT.EFFECTIVE_TIME END AS transfer_out_dttm
		,CASE WHEN ZC_EVENT_TYPE.NAME IN ('Transfer In','Admission') THEN 
		    DATEDIFF(Minute,
			ADT_IN.EFFECTIVE_TIME,
			COALESCE(ADT_OUT.EFFECTIVE_TIME, GETDATE())
			)
			END AS event_duration_in_minutes
		,ROOM.ROOM_CSN_ID AS transfer_in_room_csn
		,BED.BED_CSN_ID AS transfer_in_bed_csn
		,DEP_IN.DEPARTMENT_NAME AS transfer_in_unit
		,ROOM.ROOM_NAME AS transfer_in_room_label
		,BED.BED_LABEL AS transfer_in_bed_label
		,ZC_PAT_CLASS.NAME AS transfer_in_class
		,ZPS.NAME AS transfer_in_service
		,DEP_PRIOR.DEPARTMENT_NAME AS prior_department
		,ROOM_PRIOR.ROOM_NAME AS prior_room_name
		,BED_PRIOR.BED_LABEL AS prior_bed_label
		,ZPS_PRIOR.NAME AS prior_service
		,ZPC_PRIOR.NAME AS prior_patient_class
		,DEP_NEXT.DEPARTMENT_NAME next_department
		,ROOM_NEXT.ROOM_NAME AS next_room_name
		,BED_NEXT.BED_LABEL AS next_bed_label
		,ZPS_NEXT.NAME AS next_service
		,ZPC_NEXT.NAME AS next_patient_class
FROM  --encounters
PAT_ENC_HSP AS HSP 
JOIN PATIENT AS PAT 
ON PAT.PAT_ID 
 = HSP.PAT_ID
JOIN Clarity.dbo.PATIENT_3 AS PAT3
ON PAT.PAT_ID
 = PAT3.PAT_ID
AND (PAT3.IS_TEST_PAT_YN IS NULL OR PAT3.IS_TEST_PAT_YN = 'N')
LEFT JOIN ZC_ED_DISPOSITION AS zEdDisp 
on zEdDisp.ED_DISPOSITION_C 
 = HSP.ED_DISPOSITION_C
-- transfer in
JOIN CLARITY_ADT AS ADT_IN 
ON HSP.PAT_ENC_CSN_ID 
 = ADT_IN.PAT_ENC_CSN_ID
AND ADT_IN.EVENT_TYPE_C IN (1,3,5) -- admission, transfer_id
AND ADT_IN.EVENT_SUBTYPE_C != 2
JOIN ZC_PAT_CLASS 
ON ADT_IN.PAT_CLASS_C 
 = ZC_PAT_CLASS.ADT_PAT_CLASS_C
JOIN ZC_EVENT_TYPE 
ON ZC_EVENT_TYPE.EVENT_TYPE_C 
 = ADT_IN.EVENT_TYPE_C
JOIN CLARITY_DEP AS DEP_IN 
ON ADT_IN.DEPARTMENT_ID 
 = DEP_IN.DEPARTMENT_ID
--LEFT JOIN SERVICE_PROV AS sp
--ON sp.FACILITY_ID = DEP_IN.SERV_AREA_ID
JOIN ZC_PAT_SERVICE AS ZPS 
ON ADT_IN.PAT_SERVICE_C
 = ZPS.HOSP_SERV_C
JOIN CLARITY_BED AS BED 
ON ADT_IN.BED_CSN_ID 
 = BED.BED_CSN_ID
JOIN CLARITY_ROM AS ROOM 
ON ADT_IN.ROOM_CSN_ID 
 = ROOM.ROOM_CSN_ID
-- last transfer out
LEFT JOIN CLARITY_ADT AS ADT_PRIOR 
ON ADT_IN.XFER_EVENT_ID 
 = ADT_PRIOR.EVENT_ID
AND ADT_PRIOR.EVENT_SUBTYPE_C != 2
LEFT JOIN CLARITY_BED AS BED_PRIOR
ON ADT_PRIOR.BED_CSN_ID 
 = BED_PRIOR.BED_CSN_ID
LEFT JOIN CLARITY_ROM AS ROOM_PRIOR
ON ADT_PRIOR.ROOM_CSN_ID 
 = ROOM_PRIOR.ROOM_CSN_ID
LEFT JOIN CLARITY_DEP AS DEP_PRIOR 
ON ADT_PRIOR.DEPARTMENT_ID 
 = DEP_PRIOR.DEPARTMENT_ID
LEFT JOIN ZC_PAT_CLASS AS ZPC_PRIOR
ON ADT_PRIOR.PAT_CLASS_C 
 = ZPC_PRIOR.ADT_PAT_CLASS_C
LEFT JOIN ZC_PAT_SERVICE AS ZPS_PRIOR
ON ADT_PRIOR.PAT_SERVICE_C
 = ZPS_PRIOR.HOSP_SERV_C
-- next transfer out
LEFT JOIN CLARITY_ADT AS ADT_NEXT_OUT 
ON ADT_IN.NEXT_OUT_EVENT_ID 
 = ADT_NEXT_OUT.EVENT_ID
AND ADT_NEXT_OUT.EVENT_SUBTYPE_C != 2
LEFT JOIN CLARITY_ADT AS ADT_OUT 
on ADT_NEXT_OUT.XFER_IN_EVENT_ID
 = ADT_OUT.EVENT_ID
LEFT JOIN CLARITY_DEP AS DEP_NEXT
ON ADT_OUT.DEPARTMENT_ID 
 = DEP_NEXT.DEPARTMENT_ID
LEFT JOIN ZC_PAT_SERVICE AS ZPS_NEXT
ON ADT_OUT.PAT_SERVICE_C
 = ZPS_NEXT.HOSP_SERV_C
LEFT JOIN ZC_PAT_CLASS  AS ZPC_NEXT
ON ADT_OUT.PAT_CLASS_C 
 = ZPC_NEXT.ADT_PAT_CLASS_C
LEFT JOIN CLARITY_BED AS BED_NEXT
ON ADT_OUT.BED_CSN_ID 
 = BED_NEXT.BED_CSN_ID
LEFT JOIN CLARITY_ROM AS ROOM_NEXT
ON ADT_OUT.ROOM_CSN_ID 
 = ROOM_NEXT.ROOM_CSN_ID
WHERE 1=1
AND CONVERT(DATE,ADT_IN.EFFECTIVE_TIME) BETWEEN @date_start AND @date_end
{% if filt_depts %}
AND DEP_IN.DEPARTMENT_NAME IN {{ filt_depts|inclause_str }}
{% endif %}
{% if filt_pat_class %}
AND ZC_PAT_CLASS.NAME IN {{ filt_pat_class|inclause_str }}
{% endif %}
{% if filt_event_type %}
AND ZC_EVENT_TYPE.NAME IN {{ filt_event_type|inclause_str }}
{% endif %}
{% if filt_service %}
AND ZPS.NAME IN {{ filt_service|inclause_str}}
{% endif %}

ORDER BY HSP.PAT_ENC_CSN_ID,ADT_IN.EFFECTIVE_TIME

OPTION(RECOMPILE)

