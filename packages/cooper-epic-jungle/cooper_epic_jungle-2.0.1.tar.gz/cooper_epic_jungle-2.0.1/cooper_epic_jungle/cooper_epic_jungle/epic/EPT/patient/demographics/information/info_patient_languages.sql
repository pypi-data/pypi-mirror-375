SET NOCOUNT ON;

IF OBJECT_ID('tempdb.dbo.#PAT_ID', 'U') IS NOT NULL
  DROP TABLE #PAT_ID;

DECLARE @PAT_ID TABLE
(
  PAT_ID VARCHAR(20)
)
--INSERT STATEMENTS
{{ PAT_ID }};

SELECT * 
INTO #PAT_ID
FROM @PAT_ID;

Select 
patients.PAT_ID														as PAT_ID
	  ,UPPER(EthnicGroup.NAME)												as patient_ethnicity
	  ,UPPER(PatientLanguage.NAME)											as patient_primary_spoken_language
	  ,UPPER(SpokenLanguageNames.NAME)										as patient_secondary_spoken_language
	  ,PAT4.LANGUAGE_C_CMT													as patient_language_comment
	  ,UPPER(WrittenLanguage.NAME)											as patient_written_language
	  ,UPPER(PrefCareLanguage.NAME)											as patient_preferred_care_language
	  ,UPPER(PrefPcpLanguage.NAME)											as patient_pcp_preferred_language
	  ,CASE 
			WHEN UPPER(PatientLanguage.NAME) = 'SPANISH' 
				 OR UPPER(WrittenLanguage.NAME) = 'SPANISH' 
				 OR UPPER(SpokenLanguageNames.NAME) = 'SPANISH' 
				 OR UPPER(PrefCareLanguage.NAME) = 'SPANISH' 
				 OR PAT4.LANGUAGE_C_CMT LIKE '%%spanish%%'
			THEN 1
			ELSE 0
	 END																	as is_spanish_speaking

From Clarity.dbo.PATIENT Patients
inner join #PAT_ID as PAT_ID 
	on PAT_ID.PAT_ID 
	 = patients.PAT_ID
inner join Clarity.dbo.PATIENT_4 as PAT4
	on PAT4.PAT_ID
	 = Patients.PAT_ID
left outer join Clarity.dbo.ZC_ETHNIC_GROUP as EthnicGroup 
	on Patients.ETHNIC_GROUP_C 
	 = EthnicGroup.ETHNIC_GROUP_C
left outer join Clarity.dbo.ZC_LANGUAGE as PatientLanguage 
	on Patients.LANGUAGE_C 
	 = PatientLanguage.LANGUAGE_C
left outer join Clarity.dbo.ZC_LANGUAGE as WrittenLanguage 
	on Patients.LANG_WRIT_C 
	 = WrittenLanguage.LANGUAGE_C
left outer join Clarity.dbo.ZC_LANGUAGE as PrefCareLanguage 
	on Patients.LANG_CARE_C 
	 = PrefCareLanguage.LANGUAGE_C
left outer join Clarity.dbo.ZC_LANGUAGE as PrefPcpLanguage 
	on Patients.PREF_PCP_LANG_C 
	 = PrefPcpLanguage.LANGUAGE_C
left outer join Clarity.dbo.PAT_SPOKEN_LANG as SpokenLanguages 
	on SpokenLanguages.PAT_ID 
	 = Patients.PAT_ID
	 AND SpokenLanguages.PAT_SPOKEN_LANG_C = '96'
left outer join Clarity.dbo.ZC_LANGUAGE as  SpokenLanguageNames
	on SpokenLanguages.PAT_SPOKEN_LANG_C 
	 = SpokenLanguageNames.LANGUAGE_C

OPTION(RECOMPILE)