/*
Description: This script generates observation and/or inpatient admissions/discharges from cooper hospital.
Authors: Temi Nanna
*/

SET NOCOUNT ON

DECLARE @date_start AS DATE
DECLARE @date_end AS DATE

SET @date_start = '{{date_start}}'
SET @date_end = '{{date_end}}'

SELECT
    
	  peh.PAT_ID -- [EPT .1]
	 ,peh.PAT_ENC_CSN_ID AS CSN -- [EPT 8]
	 ,peh.HSP_ACCOUNT_ID AS HAR -- [EPT 2500]
	 ,peh.IP_EPISODE_ID AS EPISODE_ID -- [EPT 1950]
	 ,peh.HOSP_ADMSN_TIME AS hospital_admission_dttm -- [EPT 18850/18851]
	 ,peh.HOSP_DISCH_TIME AS hospital_discharge_dttm -- [EPT 18855/18856]
	 ,DATEDIFF(DAY, peh.HOSP_ADMSN_TIME, peh.HOSP_DISCH_TIME) AS hospital_length_of_stay -- [CALC]
         ,DATEDIFF(HOUR,p1.birth_date,peh.HOSP_ADMSN_TIME)/8766 AS age_at_encounter
         ,UPPER(zpc.[NAME]) AS adt_patient_class_description -- [EPT 10110]
	 ,UPPER(zps.[NAME]) AS adt_patient_status_description -- [EPT 10115]
         ,UPPER(zdd.[NAME]) AS discharge_disposition_description -- [EPT 18888]
	 ,UPPER(zas.[NAME]) AS admission_source_description -- [EPT 10310]
	 ,UPPER(zhat.[NAME]) AS hospital_admission_type_description -- [EPT 18875]
	 ,UPPER(zpse.[NAME]) AS hospital_service_description -- [EPT 18886]
          {% if include_detail_columns -%}
	 ,UPPER(aasc.[NAME]) AS auth_cert_status_description -- [EPT 10250]
	 ,UPPER(zcs.[NAME]) AS admission_confirmation_description -- [EPT 18852]
	 ,UPPER(zddt.[NAME]) AS discharge_destination_description -- [EPT 11140]
	 ,UPPER(ztsh.[NAME]) AS transfer_from_description -- [EPT 18891]
	 ,UPPER(zam.[NAME]) AS means_of_arrival_description -- [EPT 490]
	 ,UPPER(zal.[NAME]) AS acuity_level_description -- [EPT 410]
         ,peh.ADT_ARRIVAL_TIME AS arrival_dttm -- [EPT 10820/10815]
	 ,peh.INP_ADM_DATE AS inpatient_admission_dttm -- [EPT 10290/10291]
	 ,CONVERT(DATE, peh.ADT_ARRIVAL_TIME) AS arrival_date -- [EPT 10820/10815]
	 ,CONVERT(DATE, peh.HOSP_ADMSN_TIME) AS hospital_admission_date -- [EPT 18850/18851]
	 ,CONVERT(DATE, peh.INP_ADM_DATE) AS inpatient_admission_date -- [EPT 10290/10291]
	 ,CONVERT(DATE, peh.HOSP_DISCH_TIME) AS hospital_discharge_date -- [EPT 18855/18856]
	 ,FORMAT(peh.ADT_ARRIVAL_TIME, 'hh:mm tt') AS arrival_time -- [EPT 10820/10815]
	 ,FORMAT(peh.HOSP_ADMSN_TIME, 'hh:mm tt') AS hospital_admission_time -- [EPT 18850/18851]
	 ,FORMAT(peh.INP_ADM_DATE, 'hh:mm tt') AS inpatient_admission_time -- [EPT 10290/10291]
	 ,FORMAT(peh.HOSP_DISCH_TIME, 'hh:mm tt') AS hospital_discharge_time -- [EPT 18855/18856]
	 ,DATEDIFF(DAY, peh.HOSP_ADMSN_TIME, peh.HOSP_DISCH_TIME) AS hospital_length_of_stay -- [CALC]
	 ,peh.ADMISSION_PROV_ID AS admission_provider_id -- [EPT 18867]
	 ,peh.DISCHARGE_PROV_ID AS discharge_provider_id -- [EPT 18858]
	 ,peh.DEPARTMENT_ID AS department_discharge_id -- [EPT 18880]
	 ,peh.INPATIENT_DATA_ID AS inpatient_data_id -- [EPT 87400]
	 ,peh.ADM_EVENT_ID AS admission_event_id -- [Numeric]
	 ,peh.INP_ADM_EVENT_ID AS inpatient_admission_event_id -- [EPT 10292]
         ,cd.DEPARTMENT_NAME AS discharge_department_name -- [DEP .2]
         ,cd.SPECIALTY AS discharge_department_specialty -- [DEP 110]
         {% endif %}

FROM 
	Clarity.dbo.PAT_ENC_HSP AS peh
	LEFT OUTER JOIN Clarity.dbo.ZC_PAT_CLASS AS zpc
	ON peh.ADT_PAT_CLASS_C
	 = zpc.ADT_PAT_CLASS_C

	LEFT OUTER JOIN Clarity.dbo.ZC_PAT_STATUS AS zps
	ON peh.ADT_PATIENT_STAT_C
	 = zps.ADT_PATIENT_STAT_C

	LEFT OUTER JOIN Clarity.dbo.ZC_LVL_OF_CARE AS zloc
	ON peh.LEVEL_OF_CARE_C
	 = zloc.LEVEL_OF_CARE_C

	LEFT OUTER JOIN Clarity.dbo.ZC_AUTHCERT_STAT AS aasc
	ON peh.ADT_ATHCRT_STAT_C
	 = aasc.ADT_ATHCRT_STAT_C

	LEFT OUTER JOIN Clarity.dbo.ZC_ADM_SOURCE AS zas
	ON peh.ADMIT_SOURCE_C
	 = zas.ADMIT_SOURCE_C

	LEFT OUTER JOIN Clarity.dbo.ZC_CONF_STAT AS zcs
	ON peh.ADMIT_CONF_STAT_C
	 = zcs.ADMIT_CONF_STAT_C

	LEFT OUTER JOIN Clarity.dbo.ZC_HOSP_ADMSN_TYPE AS zhat
	ON peh.HOSP_ADMSN_TYPE_C
	 = zhat.HOSP_ADMSN_TYPE_C

	LEFT OUTER JOIN Clarity.dbo.ZC_PAT_SERVICE AS zpse
	ON peh.HOSP_SERV_C
	 = zpse.HOSP_SERV_C

	LEFT OUTER JOIN Clarity.dbo.ZC_DISCH_DISP AS zdd
	ON peh.DISCH_DISP_C
	 = zdd.DISCH_DISP_C

	LEFT OUTER JOIN Clarity.dbo.ZC_DISCH_DEST AS zddt
	ON peh.DISCH_DEST_C
	 = zddt.DISCH_DEST_C

	LEFT OUTER JOIN Clarity.dbo.ZC_TRANSFER_SRC_HA as ztsh
	ON peh.TRANSFER_FROM_C
	 = ztsh.TRANSFER_SRC_HA_C

	LEFT OUTER JOIN Clarity.dbo.ZC_ARRIV_MEANS AS zam
	ON peh.MEANS_OF_ARRV_C
	 = zam.MEANS_OF_ARRV_C

	LEFT OUTER JOIN Clarity.dbo.ZC_ACUITY_LEVEL AS zal
	ON peh.ACUITY_LEVEL_C
	 = zal.ACUITY_LEVEL_C

        LEFT OUTER JOIN Clarity.dbo.PATIENT AS p1
        ON peh.PAT_ID
         = p1.PAT_ID

	INNER JOIN Clarity.dbo.PATIENT_3 AS p3
	ON peh.PAT_ID
	 = p3.PAT_ID

        LEFT OUTER JOIN Clarity.dbo.Clarity_DEP AS cd
        ON peh.DEPARTMENT_ID
         = cd.DEPARTMENT_ID

WHERE  
       {% if toggle_use_discharge_date -%}
       -- Parameter: discharges date
       CONVERT(DATE, peh.HOSP_DISCH_TIME) BETWEEN @date_start AND @date_end
       {% else %}
       -- Parameter: admissions date
       CONVERT(DATE, peh.HOSP_ADMSN_TIME) BETWEEN @date_start AND @date_end
       {% endif -%}
       AND zpc.[NAME] IN {{ filt_patient_class | inclause_str}}
       {% if filt_discharge_department -%}
       AND cd.DEPARTMENT_NAME IN {{ filt_discharge_department | inclause_str}}


       {% endif -%}

        AND peh.DEPARTMENT_ID <> '310400028' -- External Imaging

       AND peh.ADMIT_SOURCE_C IS NOT NULL
       AND peh.ADM_EVENT_ID IS NOT NULL
       AND peh.ADT_PATIENT_STAT_C <> '6' -- Hospital Outpatient Visit
       AND p3.IS_TEST_PAT_YN = 'N' -- Test Patient
	
OPTION(RECOMPILE)