/*
Description: This script generates patient demographic information.
Authors: Temi Nanna
*/

SET NOCOUNT ON;

IF OBJECT_ID('tempdb.dbo.#PAT_ID', 'U') IS NOT NULL
  DROP TABLE #PAT_ID;

DECLARE @PAT_ID TABLE
(
  PAT_ID VARCHAR(20)
)

--INSERT STATEMENTS
{{ PAT_ID }}

SELECT *
INTO #PAT_ID
FROM @PAT_ID;

WITH demographics AS
(
SELECT 
       patients.PAT_ID
      ,patients.PAT_MRN_ID AS MRN
      ,UPPER(patients.PAT_LAST_NAME) + ', ' + UPPER(patients.PAT_FIRST_NAME) AS patient_name
      ,UPPER(patients.PAT_FIRST_NAME) AS patient_first_name
      ,UPPER(patients.PAT_MIDDLE_NAME) AS patient_middle_name
      ,UPPER(patients.PAT_LAST_NAME) AS patient_last_name
      ,CAST(patients.BIRTH_DATE	AS DATE) AS patient_birth_date
      ,FLOOR((CAST (GetDate() AS INTEGER) - CAST(patients.BIRTH_DATE AS INTEGER)) / 365.25) AS patient_age
      ,UPPER(sex_description.NAME) AS patient_sex
      ,UPPER(sex_description.ABBR) AS patient_sex_abr
      ,UPPER(patients.EMAIL_ADDRESS) AS patient_email
      ,patients.HOME_PHONE AS patient_home_number
      ,patients.WORK_PHONE AS patient_work_number
      ,patient_status_description.NAME AS patient_status
      ,patients.DEATH_DATE AS epic_death_date
      ,UPPER(patient_race_description.NAME) AS patient_race
      ,UPPER(ethnic_group_description.NAME) AS patient_ethnicity
      ,UPPER(martial_description.NAME) AS patient_martial_status
      ,UPPER(language_description.NAME) AS patient_lanuage
      ,CASE WHEN patients.SSN = '000-00-0000' then ''
	    WHEN patients.SSN = '999-99-9999' then ''
	    WHEN patients.SSN is null then ''
       ELSE patients.SSN
       END AS ssn
      ,CASE WHEN patients.HOME_PHONE is null then ''
	    WHEN patients.HOME_PHONE = '000-000-0000' then ''
	    WHEN patients.HOME_PHONE = '999-999-9999' then ''
       ELSE patients.HOME_PHONE
       END AS patient_home_number_calc
      ,CASE WHEN patients.WORK_PHONE is null then ''
            WHEN patients.WORK_PHONE = '000-000-0000' then ''
	    WHEN patients.WORK_PHONE = '999-999-9999' then ''
       ELSE patients.WORK_PHONE
       END AS patient_work_number_calc
      ,provider_information.PROV_ID AS pcp_of_record_prov_id
      ,provider_information.PROV_NAME AS pcp_of_record_name
      ,CONCAT(provider_address.ADDR_LINE_1,' ',provider_address.ADDR_LINE_2) AS pcp_of_record_address
      ,patients.MEDICARE_NUM AS medicare_number
      ,patients.MEDICAID_NUM AS medicaid_number

FROM 
	Clarity.dbo.PATIENT AS patients
	INNER JOIN #pat_id AS insert_pat_ids 
        ON insert_pat_ids.PAT_ID 
         = patients.PAT_ID

	LEFT OUTER JOIN Clarity.dbo.PATIENT_RACE AS patient_race
	ON patients.PAT_ID 
	 = patient_race.PAT_ID 
	 AND patient_race.LINE = '1'

	LEFT OUTER JOIN Clarity.dbo.ZC_PATIENT_RACE AS patient_race_description
	ON patient_race.PATIENT_RACE_C 
	 = patient_race_description.PATIENT_RACE_C

	LEFT OUTER JOIN Clarity.dbo.ZC_MARITAL_STATUS AS martial_description
	ON patients.MARITAL_STATUS_C 
	 = martial_description.MARITAL_STATUS_C

	LEFT OUTER JOIN Clarity.dbo.ZC_LANGUAGE AS language_description 
	ON patients.LANGUAGE_C 
	 = language_description.LANGUAGE_C

	LEFT OUTER JOIN Clarity.dbo.ZC_SEX AS sex_description
	ON patients.SEX_C 
	 = sex_description.RCPT_MEM_SEX_C

	LEFT OUTER JOIN Clarity.dbo.CLARITY_SER AS provider_information
	ON patients.CUR_PCP_PROV_ID 
	 = provider_information.PROV_ID

	LEFT OUTER JOIN Clarity.dbo.Clarity_SER_ADDR AS provider_address
	ON provider_information.PROV_ID 
	 = provider_address.PROV_ID 
	 AND provider_address.PRIMARY_ADDR_YN = 'Y' 
	 AND provider_address.LINE = 1

	LEFT OUTER JOIN Clarity.dbo.ZC_ETHNIC_GROUP AS ethnic_group_description 
	ON patients.ETHNIC_GROUP_C 
	 = ethnic_group_description.ETHNIC_GROUP_C

	LEFT OUTER JOIN Clarity.dbo.PATIENT_4 AS patient_4 
	ON patient_4.PAT_ID 
	 = patients.PAT_ID

	LEFT OUTER JOIN Clarity.dbo.ZC_PAT_LIVING_STAT AS patient_status_description
	ON patient_4.PAT_LIVING_STAT_C 
	 = patient_status_description.PAT_LIVING_STAT_C
)

, sogi AS
(
SELECT
        patients.PAT_ID
       ,gender_identity_description.NAME AS gender_identity
       ,patient_sexual_orientation_description.NAME AS sexual_orientation
       ,sex_assigned_birth_description.NAME AS sex_assigned_at_birth
       ,RN_SO = ROW_NUMBER() OVER (PARTITION BY patients.PAT_ID ORDER BY patient_sexual_orientation.LINE DESC)

FROM 
	Clarity.dbo.PATIENT AS patients
	INNER JOIN #pat_id AS insert_pat_ids
	ON insert_pat_ids.PAT_ID
	 = patients.PAT_ID

	INNER JOIN Clarity.dbo.PATIENT_4 AS patient_4
	ON patient_4.PAT_ID
	 = patients.PAT_ID

	LEFT JOIN Clarity.dbo.PAT_SEXUAL_ORIENTATION AS patient_sexual_orientation
	ON patient_sexual_orientation.PAT_ID
	 = patients.PAT_ID

	LEFT JOIN Clarity.dbo.ZC_SEXUAL_ORIENTATION AS patient_sexual_orientation_description
	ON patient_sexual_orientation_description.SEXUAL_ORIENTATION_C
	 = patient_sexual_orientation.SEXUAL_ORIENTATN_C

	LEFT JOIN Clarity.dbo.ZC_GENDER_IDENTITY AS gender_identity_description
	 ON gender_identity_description.GENDER_IDENTITY_C
	  = patient_4.GENDER_IDENTITY_C

	LEFT JOIN Clarity.dbo.ZC_SEX_ASGN_AT_BIRTH AS sex_assigned_birth_description
	ON sex_assigned_birth_description.SEX_ASGN_AT_BIRTH_C
	 = patient_4.SEX_ASGN_AT_BIRTH_C
)

, patient_address AS
(
SELECT
	patient_address_history.PAT_ID
   ,UPPER(patient_address_history.ADDR_HX_LINE1) AS patient_address1
   ,UPPER(patient_address_history.ADDR_HX_LINE2) AS patient_address2
   ,CASE WHEN patient_address_history.ADDR_HX_LINE1 IS NOT NULL 
		 AND patient_address_history.ADDR_HX_LINE2 IS NOT NULL THEN UPPER(patient_address_history.ADDR_HX_LINE1) + ' ' + UPPER(patient_address_history.ADDR_HX_LINE2)
         WHEN patient_address_history.ADDR_HX_LINE1 IS NOT NULL THEN UPPER(patient_address_history.ADDR_HX_LINE1)
	     WHEN patient_address_history.ADDR_HX_LINE2 IS NOT NULL THEN UPPER(patient_address_history.ADDR_HX_LINE2)
    END AS address_combined
   ,patient_address_history.CITY_HX AS patient_city
   ,UPPER(state_description.[NAME]) AS patient_state
   ,UPPER(state_description.ABBR) AS patient_state_abr
   ,county_description.[NAME] AS patient_county
   ,LEFT(patient_address_history.ZIP_HX, 5) AS patient_postal_code
   ,patient_address_history.EFF_START_DATE AS record_start_date
   ,patient_address_history.EFF_END_DATE AS record_end_date

FROM
	Clarity.dbo.PAT_ADDR_CHNG_HX AS patient_address_history
	INNER JOIN #pat_id AS insert_pat_ids
	ON insert_pat_ids.PAT_ID 
	 = patient_address_history.PAT_ID

	LEFT OUTER JOIN Clarity.dbo.ZC_STATE AS state_description 
	ON state_description.STATE_C
	 = patient_address_history.STATE_HX_C

	LEFT OUTER JOIN Clarity.dbo.zc_county AS county_description 
	ON county_description.COUNTY_C 
	 = patient_address_history.COUNTY_HX_C

WHERE
	patient_address_history.EFF_END_DATE IS NULL
)

SELECT
     
       demographics.PAT_ID -- [EPT .1]
      ,demographics.MRN -- [EPT 2061]
	  ,patient_address.patient_address1 -- [EPT 2405]
	  ,patient_address.patient_address2 -- [EPT 2410]
	  ,patient_address.address_combined -- [EPT 2405/2410 calc]
	  ,patient_address.patient_city -- [EPT 2420]
	  ,patient_address.patient_state -- [EPT 2425]
	  ,patient_address.patient_state_abr -- [EPT 2425]
	  ,patient_address.patient_county -- [EPT 2422]
	  ,patient_address.patient_postal_code -- [EPT 2430]
	  ,patient_address.record_start_date -- [EPT 2400]
	  ,patient_address.record_end_date -- [DATETIME]
      ,demographics.patient_first_name -- [EPT 118]
      ,demographics.patient_middle_name -- [EPT 119]
      ,demographics.patient_last_name -- [EPT 117]
      ,demographics.patient_name -- [EPT .2]
      ,demographics.patient_birth_date -- [EPT 110/111]
      ,demographics.patient_age -- [EPT 110/111 calc]
      ,demographics.patient_sex -- [EPT 130]
      ,demographics.patient_sex_abr -- [EPT 130]
      ,demographics.patient_race -- [EPT 145]
      ,demographics.patient_ethnicity -- [EPT 135]
      {% if include_detail_columns -%}
      ,demographics.patient_martial_status -- [EPT 140]
      ,demographics.patient_email -- [EPT 85]
      ,demographics.patient_home_number -- [EPT 90]
      ,demographics.patient_work_number -- [EPT 91]
      ,demographics.epic_death_date -- [EPT 115/116]
      ,demographics.patient_status -- [EPT 112]
      ,demographics.patient_lanuage -- [EPT 155]
      ,demographics.ssn -- [EPT 160]
      ,demographics.patient_home_number_calc -- [CALC]
      ,demographics.patient_work_number_calc -- [CALC]
      ,demographics.pcp_of_record_prov_id -- [SER .1]
      ,demographics.pcp_of_record_name -- [SER .2]
      ,demographics.pcp_of_record_address -- [SER 21010/21020 calc]
      ,demographics.medicare_number -- [EPT 5330]
      ,demographics.medicaid_number -- [EPT 5335]
      ,sogi.gender_identity -- [EPT 131]
      ,sogi.sexual_orientation -- [EPT 132]
      ,sogi.sex_assigned_at_birth -- [EPT 133]
      {% endif %}
      
FROM 
	demographics AS demographics
	LEFT OUTER JOIN SoGi AS sogi
	ON demographics.PAT_ID 
	 = sogi.PAT_ID 
	 AND sogi.RN_SO = '1'

	LEFT OUTER JOIN patient_address AS patient_address
	ON patient_address.PAT_ID
	 = demographics.PAT_ID

OPTION(RECOMPILE);

IF OBJECT_ID('tempdb.dbo.#PAT_ID', 'U') IS NOT NULL
  DROP TABLE #PAT_ID;
