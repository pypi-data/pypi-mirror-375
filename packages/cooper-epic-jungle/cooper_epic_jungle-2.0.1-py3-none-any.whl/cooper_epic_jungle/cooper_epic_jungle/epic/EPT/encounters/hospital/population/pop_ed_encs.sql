/*
Description: Get ED encounters by date range using HSP.EMER_ADM_DATE
Author: Alex Moore
Jungle Location: epic/EPT/encounters/hosptial/pop/
Parameters: date_start = date str; date_end = date str; toggle_use_admit_date = T/F - use ED admit or ED departure ; 
			filt_ed_disposition = str list for ED dispotition;
			filt_admit_dept = str list for Next dept after ED;
*/

DECLARE @date_start DATE, @date_end DATE

SET @date_start = '{{ date_start }}'
SET @date_end = '{{ date_end }}';


WITH non_ed AS (	SELECT adt.PAT_ENC_CSN_ID AS  CSN 
                               ,dep.DEPARTMENT_NAME dept_name 
                               ,adt.EFFECTIVE_TIME arrival
                               ,ROW_NUMBER() OVER(PARTITION BY adt.PAT_ENC_CSN_ID ORDER BY adt.EFFECTIVE_TIME, adt.EVENT_ID) rown
                      FROM CLARITY_ADT adt
                      LEFT OUTER JOIN CLARITY_DEP dep
                      ON adt.DEPARTMENT_ID = dep.DEPARTMENT_ID
                      WHERE adt.EVENT_TYPE_C = 3
                      AND NULLIF(1, dep.ADT_UNIT_TYPE_C) IS NOT NULL
                      AND dep.DEPARTMENT_NAME NOT IN ('CUH EMRG','CRMC EMERGENCY')
                      AND adt.EVENT_SUBTYPE_C <> 2
		)

SELECT hsp.PAT_ID 
		,hsp.PAT_ENC_CSN_ID AS CSN
		,hsp.ED_EPISODE_ID AS EPISODE_ID
                ,hsp.HSP_ACCOUNT_ID AS HAR
                {% if include_details %}
		,hsp.EMER_ADM_DATE AS ed_admission_dttm 
		,hsp.ED_DEPARTURE_TIME AS ed_departure_dttm
		,ZED.NAME as ed_disposition
		,hsp.HOSP_ADMSN_TIME AS hosp_admission_dttm
		,hsp.HOSP_DISCH_TIME AS hosp_discharge_dttm
                ,DATEDIFF(HOUR,p1.birth_date,hsp.HOSP_ADMSN_TIME)/8766 AS age_at_encounter
		,DATEDIFF(minute,hsp.ED_DISP_TIME, non_ed.arrival) AS boarding_duration_minutes
		,DATEDIFF(hour,hsp.HOSP_ADMSN_TIME, hsp.HOSP_DISCH_TIME) AS hospital_los_hours 
                ,DATEDIFF(hour,non_ed.arrival,hsp.HOSP_DISCH_TIME) AS ip_obs_los_hours
                ,DATEDIFF(hour,COALESCE(HSP.ADT_ARRIVAL_TIME,HSP.HOSP_ADMSN_TIME),hsp.ED_DEPARTURE_TIME) AS ed_los_hours
		,dep.DEPARTMENT_NAME AS discharge_dept
		,zpc.NAME as discharge_class
		,ZDDSP.NAME as discharge_disposition
		--,ZPSH.NAME as "Encounter Service"
		,zddh.NAME AS discharge_destination
                ,non_ed.dept_name AS first_non_ed_dept_name
                ,non_ed.arrival AS first_non_ed_transfer_dttm
                {% endif %}
FROM PAT_ENC_HSP AS hsp
JOIN PATIENT_3 p3
ON p3.PAT_ID = hsp.PAT_ID
AND (p3.IS_TEST_PAT_YN IS NULL OR p3.IS_TEST_PAT_YN = 'N')
JOIN PATIENT p1
ON p1.PAT_ID = hsp.PAT_ID 
LEFT JOIN ZC_PAT_CLASS AS ZPC 
ON ZPC.ADT_PAT_CLASS_C = HSP.ADT_PAT_CLASS_C
--LEFT JOIN ZC_PRIM_SVC_HA AS ZPSH 
--ON ZPSH.PRIM_SVC_HA_C = HSP.HOSP_SERV_C
LEFT JOIN CLARITY_DEP AS DEP 
ON DEP.DEPARTMENT_ID = HSP.DEPARTMENT_ID
LEFT JOIN ZC_DISCH_DISP AS ZDDSP 
ON ZDDSP.DISCH_DISP_C = HSP.DISCH_DISP_C
LEFT JOIN ZC_ED_DISPOSITION AS ZED 
ON ZED.ED_DISPOSITION_C = HSP.ED_DISPOSITION_C
LEFT JOIN ZC_DISCH_DEST AS ZDDH 
ON ZDDH.DISCH_DEST_C = hsp.DISCH_DEST_C
LEFT JOIN non_ed 
ON hsp.PAT_ENC_CSN_ID = non_ed.CSN
AND non_ed.rown = 1
WHERE	{% if toggle_use_admit_date %}
 CONVERT(DATE,HSP.EMER_ADM_DATE) BETWEEN @date_start AND @date_end 
		{% else %}
 CONVERT(DATE,HSP.ED_DEPARTURE_TIME) BETWEEN @date_start AND @date_end 
		{% endif %}
--and
--HSP.ADT_PAT_CLASS_C IN ('101','1007' --IP
--						,'1029' --OBS
--						,'1005','106' --ED
--						,'1017' --Single Visit Outpatient
--						,'1016','102') --Same Day Surgery
 {% if filt_ed_disposition %}
 AND ZED.NAME IN {{ filt_ed_disposition|inclause_str }}
 {% endif %}
 {% if filt_admit_dept %}
 AND non_ed.dept_name IN {{ filt_admit_dept|inclause_str }}
 {% endif %}
AND
HSP.ADT_PATIENT_STAT_C != 6
AND
HSP.EMER_ADM_DATE IS NOT NULL
AND
DEP.DEPARTMENT_NAME != 'External Images'
--AND hsp.pat_id = 'Z507098'

OPTION (RECOMPILE)