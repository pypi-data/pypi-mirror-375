SET NOCOUNT ON;

DECLARE @start_date AS DATE
DECLARE @end_date AS DATE

SET @start_date = '{{date_start}}'
SET @end_date = '{{date_end}}';

--SET @end_date = '04/05/2024'
--SET @start_date = '04/01/2024';

SELECT 
			  pat.[primarymrn] as MRN
			  ,pat.PatientEpicId as PAT_ID
			  ,enc.[EncounterEpicCsn] as CSN
			  ,dos.DateValue AS service_date

    {% if include_department %}
		-- FLAG: Department/Place of service info
			  ,Dep.DepartmentName as encounter_department
			  ,dep.DepartmentEpicId as encounter_department_id
			  ,dep.ParentLocationName as encounter_department_parent_location
			  ,dep.DepartmentSpecialty as encounter_department_specialty
			  ,pos.name as place_of_service
			  ,dep.LocationName department_location
			  ,dep.departmentspecialtyinstitutename_x as institute_name
	{% endif %}

    {% if include_provider_details %}
		-- FLAG: Provider Details
			  ,prov.name as encounter_provider
			  ,prov.ProviderEpicId as encounter_provider_id
			  ,prov.Npi as encounter_provider_npi
			  ,prov.PrimaryDepartment as encounter_provider_primary_department
			  ,prov.PrimarySpecialty as encounter_provider_primary_speciality
			  ,prov.PrimaryLocation as encounter_provider_primary_location
			  ,refprov.name as referring_provider_name
    {% endif %}

    {% if include_encounter_details %}
		-- FLAG: Encounter Details
			  ,VF.AppointmentStatus  as encounter_status
			  ,enc.[Type] as encounter_type
			  ,enc.VisitType as visit_type
			  ,[IsOutpatientFaceToFaceVisit] as outpatient_face_to_face_flag
			  ,dx.name as primary_diagnosis
			  ,primproc.Name as primary_procedure
			  ,VF.AppointmentConfirmationStatus as confirmation_status
			  ,VF.AppointmentSerialNumber as appointment_serial_number
    {% endif %}

    {% if include_service_date_grouping %}
     		-- FLAG: Ancillary service dates and times
			  ,dos.[dayofweek] as service_day_of_week
			  ,dos.[formattedQuarterNumber] as service_date_quarter
			  ,dos.[formattedquarteryear] as service_date_quarter_year
			  ,dos.[monthname] as service_month_name
			  ,dos.[monthnumber] as service_month_num
			  ,dos.[year] as service_year
    {% endif %}
FROM 
		  CDW.FullAccess.EncounterFact as ENC
		  left join CDW.FullAccess.patientdim as pat 
		  on pat.DurableKey 
		   = ENC.PatientDurableKey and pat.IsCurrent ='1'
		  left join CDW.FullAccess.datedim as dos 
		  on dos.datekey 
		   = ENC.datekey
		  left join CDW.FullAccess.DiagnosisDim as dx
		  on dx.DiagnosisKey
		   = ENC.PrimaryDiagnosisKey
		  left join CDW.FullAccess.ProcedureTerminologyDim as primproc
		  on primproc.ProcedureTerminologyKey
		   = ENC.PrimaryProcedureKey
		  left join CDW.FullAccess.DepartmentDim as Dep
		  on dep.DepartmentKey
		   = enc.[DepartmentKey]
		  left join CDW.FullAccess.PlaceOfServiceDim as pos
		  on pos.PlaceOfServiceKey
		   = enc.PlaceOfServiceKey
		  left join CDW.FullAccess.providerdim as prov
		  on prov.DurableKey
		   = enc.ProviderDurableKey and prov.IsCurrent ='1'
		  left join CDW.FullAccess.providerdim as refprov
		  on refprov.DurableKey
		   = enc.ReferringProviderDurableKey  and refprov.IsCurrent ='1'
		  LEFT JOIN CDW.FullAccess.VisitFact as VF
		  on VF.EncounterKey = ENC.EncounterKey

WHERE
    DOS.DATEVALUE BETWEEN @START_DATE AND @END_DATE

    {% if filt_encounter_status %}
    AND VF.AppointmentStatus IN {{ filt_encounter_status|inclause_str }}
    {% endif %}

    {% if filt_encounter_type %}
    AND enc.Type IN {{ filt_encounter_type|inclause_str }}
    {% else %}
    AND [IsOutpatientFaceToFaceVisit] = 1
    {% endif %}

    {% if filt_encounter_department %}
    AND Dep.DepartmentName IN {{ filt_encounter_department|inclause_str}}
    {% endif %}

    {% if filt_encounter_department_specialty %}
    AND Dep.DepartmentSpecialty IN {{ filt_encounter_department_specialty|inclause_str }}
    {% endif %}

    {% if filt_encounter_provider_id %}
    AND prov.ProviderEpicId IN {{ filt_encounter_provider_id|inclause }}
    {% endif %}

    AND pat.[primarymrn] NOT LIKE  '%%[A-Z]%%'  {# '% must be escaped in jinja, it is a reserved key' #}


ORDER BY enc.[Type]
OPTION(RECOMPILE) 
