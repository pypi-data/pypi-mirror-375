/*
Encounter Specific Diagnosis(Encounter Based)
Description: The config file will return the encounter specific diagnosis of a patient encounter and allows the option
to only evaluate the presence of a specific diagnosis, or multiple diagnosis, across multiple groups of diagnosis,
across: Admission Order Diagnosis, ED/Ambulatory Diagnosis, Hospital Diagnosis, and/or Billing Diagnosis.
Author: Justin Frisby, Sean Murphy, Kevin Lam
~~~~~~~~~~~~~~~~ note that everything after this divider is for Sean and will be deleted after adding to the jungle
Jungle Location: epic/EPT/encounters/general/information/encounter_related_diagnosis.sql

*/

SET NOCOUNT ON;

IF OBJECT_ID('tempdb.dbo.#CSN', 'U') IS NOT NULL
    DROP TABLE #CSN;

DECLARE @CSN TABLE
             (
                 CSN NVARCHAR(50)
             )

-- INSERTION CLAUSES
    {{ CSN }};
;


SELECT *
INTO #CSN
FROM @CSN;

with DX as --------------------------------------------------------------------------------------------------------
         (
             SELECT
                 EDG.dx_id,
                 EDG.dx_name,
                 EDG.current_icd10_list
              FROM
                 CLARITY.DBO.CLARITY_EDG EDG
			 JOIN Clarity.dbo.EDG_CURRENT_ICD10 AS icd
			 ON edg.DX_ID = icd.DX_ID
			 AND EC_INACTIVE_YN = 'N'
                 {% if filts_dx %}
    WHERE

				{% for dx_cat, list_of_dxs in filts_dx.items() %}
					{% for dx in list_of_dxs %}
						{% if dx_cat == filts_dx.keys()|first and dx == list_of_dxs|first: %}
							EDG.CURRENT_ICD10_LIST LIKE '%%{{dx}}%%'
						{% else %}
							OR EDG.CURRENT_ICD10_LIST LIKE '%%{{dx}}%%'
						{% endif %}
					{% endfor %}
				{% endfor %}
				
		{% endif %}
)

    {% if toggle_use_pat_enc_dxs %}
    ,
    PAT_ENC_DXS as --------------------------------------------------------------------------------------------------------
    (
    SELECT
    HSP.PAT_ID,
    HSP.PAT_ENC_CSN_ID AS CSN,
    'PAT_ENC Diagnoses' as "Dx Type",
    ENC_DX.LINE,
    EDG_ENC.DX_ID,
    EDG_ENC.DX_NAME,
    EDG_ENC.CURRENT_ICD10_LIST,
    CASE WHEN EDG_ENC.DX_ID IN (SELECT DX_ID FROM dx) THEN 1 ELSE 0 END AS "Dx in Specified Dxs",
    RN_EDX = ROW_NUMBER() OVER (PARTITION BY HSP.PAT_ENC_CSN_ID, DX_NAME ORDER BY EDG_ENC.DX_ID)
    FROM
    Clarity.dbo.PAT_ENC						    as HSP
    INNER JOIN #CSN								as CSNS			ON CSNS.CSN = HSP.PAT_ENC_CSN_ID
    INNER JOIN Clarity.dbo.patient				as pat			ON pat.pat_id = HSP.PAT_ID
    INNER JOIN Clarity.dbo.PAT_ENC_DX			as ENC_DX		ON ENC_DX.PAT_ENC_CSN_ID = HSP.PAT_ENC_CSN_ID
    {% if filts_dx == False and toggle_use_pat_enc_dxs== True %}
    AND ENC_DX.LINE <= {{ dx_line_limit }}
    {% endif %}
    {% if filts_dx %}
    INNER JOIN DX								as EDG_ENC	    ON EDG_ENC.DX_ID = ENC_DX.DX_ID
    {% else %}
    LEFT JOIN  Clarity.dbo.CLARITY_EDG			as EDG_ENC		ON EDG_ENC.DX_ID = ENC_DX.DX_ID
    {% endif %}
    )
    {% endif %}
    {% if toggle_use_hsp_billing_dxs %}
    ,

    HAR_DXS as
    (
    SELECT
    HSP.PAT_ID,
    HSP.PAT_ENC_CSN_ID AS CSN,
    'HAR Diagnosis' as "Dx Type",
    ACCT_DX.LINE,
    EDG_HAR.DX_ID,
    EDG_HAR.DX_NAME,
    EDG_HAR.CURRENT_ICD10_LIST,
    CASE WHEN EDG_HAR.DX_ID IN (SELECT DX_ID FROM dx) THEN 1 ELSE 0 END AS "Dx in Specified Dxs",
    RN_HAR = ROW_NUMBER() OVER (PARTITION BY HSP.PAT_ENC_CSN_ID, DX_NAME ORDER BY EDG_HAR.DX_ID)
    FROM
    Clarity.dbo.PAT_ENC						    as HSP
    INNER JOIN #CSN								as CSNS			ON CSNS.CSN = HSP.PAT_ENC_CSN_ID
    LEFT JOIN Clarity.dbo.patient				as pat			ON pat.pat_id = HSP.PAT_ID
    INNER JOIN Clarity.dbo.HSP_ACCT_DX_LIST		as ACCT_DX		ON ACCT_DX.HSP_ACCOUNT_ID = HSP.HSP_ACCOUNT_ID
    {% if filts_dx == False and toggle_use_hsp_billing_dxs == True %}
    AND ACCT_DX.LINE <= {{ dx_line_limit }}
    {% endif %}
    {% if filts_dx %}
    INNER JOIN DX								as EDG_HAR	    ON ACCT_DX.DX_ID = EDG_HAR.DX_ID
    {% else %}
    LEFT JOIN  Clarity.dbo.CLARITY_EDG			as EDG_HAR		ON ACCT_DX.DX_ID = EDG_HAR.DX_ID
    {% endif %}
    )
    {% endif %}
---------------------------------------  FINAL CTE  ---------------------------------------------------------
    SELECT

        {% if filts_dx %}
    csns.CSN

    {% for dx_cat, list_of_dxs in filts_dx.items(): %}
                {% if list_of_dxs|length == 1: %}
                    ,MAX(CASE WHEN CURRENT_ICD10_LIST LIKE '%%{{list_of_dxs[0]}}%%' THEN 1 ELSE 0 END) AS [Has_{{dx_cat|title()}}_In_Dx]
                {% else: %}
                   {%  for dx in range(0,list_of_dxs|length): %}
                        {% if dx == 0: %}
                            ,MAX(CASE WHEN CURRENT_ICD10_LIST LIKE '%%{{list_of_dxs[dx]}}%%'
                        {% else: %}
                             OR CURRENT_ICD10_LIST LIKE '%%{{list_of_dxs[dx]}}%%'
                        {% endif %}
                   {% endfor %}
                    THEN 1 ELSE 0 END) AS  [Has_{{dx_cat|title()}}_In_Dx]
                {% endif %}
            {% endfor %}
        {% else %}

        -- select only if dx type is true
		CSNS.CSN,
		STRING_AGG((CASE WHEN [Dx Type] = 'PAT_ENC Diagnoses' THEN DX_NAME END), '; ') AS "Enc Diagnoses",
		STRING_AGG((CASE WHEN [Dx Type] = 'PAT_ENC Diagnoses' THEN CURRENT_ICD10_LIST END), '; ') AS "Enc Diagnoses ICD Codes",
		STRING_AGG((CASE WHEN [Dx Type] = 'HAR Diagnosis' THEN DX_NAME END), '; ') AS "Billing Diagnoses",
		STRING_AGG((CASE WHEN [Dx Type] = 'HAR Diagnosis' THEN CURRENT_ICD10_LIST END), '; ') AS "Billing Diagnoses ICD Codes"

		{% endif %}



{# define parms which need to be unioned if included #}
{% set union_dict_all = {'toggle_use_pat_enc_dxs': toggle_use_pat_enc_dxs,
                        'toggle_use_hsp_billing_dxs': toggle_use_hsp_billing_dxs
                        }
%}

{# create new dictionary only containing True values  #}
{% set union_dict = {} %}

    {% for key,value in union_dict_all.items() %}
    {% if value %}
    {% set _ = union_dict.update({key:value}) %}
    {% endif %}
    {% endfor %}

    from #csn as CSNS
    left join (
    {# Loop through included variables. add union for all except last iteration #}
    {% for key,val in union_dict.items() %}

    {%- if key == 'toggle_use_pat_enc_dxs' %}
    SELECT * FROM PAT_ENC_DXS		as HPL	WHERE RN_EDX = 1
    {% endif -%}

    {%- if key == 'toggle_use_hsp_billing_dxs' %}
    SELECT * FROM HAR_DXS				as HAR	WHERE RN_HAR = 1
    {% endif -%}

    {%- if key != union_dict.keys()|last %}
    Union All
    {% endif -%}

    {% endfor %}) as union_dxs on CSNS.CSN = union_dxs.CSN




    GROUP BY CSNS.CSN

    OPTION(RECOMPILE)