/*
Encounter Specific Diagnosis(Encounter Based)
Description: The config file will return the encounter specific diagnosis of a patient encounter and allows the option
to only evaluate the presence of a specific diagnosis, or multiple diagnosis, across multiple groups of diagnosis,
across: Admission Order Diagnosis, ED/Ambulatory Diagnosis, Hospital Diagnosis, and/or Billing Diagnosis.
Author: Justin Frisby, Sean Murphy, Kevin Lam
~~~~~~~~~~~~~~~~ note that everything after this divider is for Sean and will be deleted after adding to the jungle
Jungle Location: epic/EPT/encounters/general/information/encounter_related_diagnosis.sql
Parameters: {'filts_dx': None,
              'toggle_use_ed_dxs': True,
              'toggle_use_admit_order_dx': False,
              'toggle_use_hsp_prob_list_dxs': False,
              'toggle_use_hsp_billing_dxs': True,
              'dx_line_limit': 10}
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
    {% if filts_dx|length == 1 and filts_dx.values()|first|length == 1 %}
					EDG.CURRENT_ICD10_LIST like '%%{{filts_dx.values()|first|first}}%%'
				{% else%}

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
		{% endif %}
)
{% if toggle_use_admit_order_dx %}
    ,
    ADMISSION_ORDER_DXS as --------------------------------------------------------------------------------------------------------
    (
    SELECT
    PAT_MRN_ID as MRN,
    HSP.PAT_ENC_CSN_ID AS CSN,
    'Admission Order' as "Dx Type",
    1 as LINE,
    EDG_ADM.DX_ID,
    EDG_ADM.DX_NAME,
    EDG_ADM.CURRENT_ICD10_LIST,
    CASE WHEN EDG_ADM.DX_ID IN (SELECT DX_ID FROM dx) THEN 1 ELSE 0 END AS "Dx in Specified Dxs",
    RN_AOD = ROW_NUMBER() OVER (PARTITION BY HSP.PAT_ENC_CSN_ID, DX_NAME ORDER BY DX_ID)
    FROM
    Clarity.dbo.PAT_ENC_HSP							as HSP
    INNER JOIN #CSN									as CSNS			ON CSNS.CSN = HSP.PAT_ENC_CSN_ID
    INNER JOIN Clarity.dbo.patient					as PAT			ON pat.pat_id = HSP.PAT_ID
    INNER JOIN [Clarity].[dbo].[ORDER_PROC]			as OP			ON OP.PAT_ENC_CSN_ID = HSP.PAT_ENC_CSN_ID
    AND OP.PROC_ID = 263 AND FUTURE_OR_STAND = 'S'
    LEFT JOIN  [Clarity].[dbo].[ORD_SPEC_QUEST]		as OSQ			ON OSQ.ORDER_ID = OP.ORDER_PROC_ID
    AND OSQ.ord_quest_id = '100042'
    LEFT JOIN  Clarity.dbo.CL_QQUEST				as QUEST_DESC	ON QUEST_DESC.QUEST_ID = OSQ.ORD_QUEST_ID
    {% if filts_dx %}
    INNER JOIN DX									as EDG_ADM	    ON EDG_ADM.DX_ID = CONVERT(NUMERIC,OSQ.ORD_QUEST_RESP)
    {% else %}
    LEFT JOIN  Clarity.dbo.CLARITY_EDG				as EDG_ADM		ON EDG_ADM.DX_ID = CONVERT(NUMERIC,OSQ.ORD_QUEST_RESP)
    {% endif %}
    )
    {% endif %}
    {% if toggle_use_hsp_prob_list_dxs %}
    ,
    HSP_PROBLEM_LIST as --------------------------------------------------------------------------------------------------------
    (
    SELECT
    PAT_MRN_ID as MRN,
    HSP.PAT_ENC_CSN_ID AS CSN,
    'Hospital Problem List' as "Dx Type",
    HSP_PBL.LINE,
    EDG_PBL.DX_ID,
    EDG_PBL.DX_NAME,
    EDG_PBL.CURRENT_ICD10_LIST,
    CASE WHEN EDG_PBL.DX_ID IN (SELECT DX_ID FROM dx) THEN 1 ELSE 0 END AS "Dx in Specified Dxs",
    RN_HPL = ROW_NUMBER() OVER (PARTITION BY HSP.PAT_ENC_CSN_ID, DX_NAME ORDER BY EDG_PBL.DX_ID)
    FROM
    Clarity.dbo.PAT_ENC_HSP							as HSP
    INNER JOIN #CSN									as CSNS		ON CSNS.CSN = HSP.PAT_ENC_CSN_ID
    LEFT JOIN  Clarity.dbo.patient					as PAT		ON PAT.pat_id = HSP.PAT_ID
    INNER JOIN  [Clarity].[dbo].[PAT_ENC_HOSP_PROB]	as HSP_PBL	ON HSP_PBL.PAT_ENC_CSN_ID = HSP.PAT_ENC_CSN_ID
    {% if filts_dx == False and toggle_use_hsp_prob_list_dxs == True %}
    AND HSP_PBL.LINE <= {{ dx_line_limit }}
    {% endif %}
    INNER JOIN  [Clarity].[dbo].PROBLEM_LIST		as PBL		ON HSP_PBL.PROBLEM_LIST_ID = PBL.PROBLEM_LIST_ID
    {% if filts_dx %}
    INNER JOIN DX									as EDG_PBL	    ON EDG_PBL.DX_ID = PBL.DX_ID
    {% else %}
    LEFT JOIN  Clarity.dbo.CLARITY_EDG				as EDG_PBL		ON EDG_PBL.DX_ID = PBL.DX_ID
    {% endif %}
    )
    {% endif %}
    {% if toggle_use_ed_dxs %}
    ,
    ED_DXS as --------------------------------------------------------------------------------------------------------
    (
    SELECT
    PAT_MRN_ID as MRN,
    HSP.PAT_ENC_CSN_ID AS CSN,
    'ED Diagnoses' as "Dx Type",
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
    {% if filts_dx == False and toggle_use_ed_dxs == True %}
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
    PAT_MRN_ID as MRN,
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
		MAX(CASE WHEN [Dx Type] = 'Admission Order' THEN DX_NAME END) AS "Admission Order Diagnosis",
		MAX(CASE WHEN [Dx Type] = 'Admission Order' THEN CURRENT_ICD10_LIST END) AS "Admission Order ICD Code",
		MAX(CASE WHEN [Dx Type] = 'Hospital Problem List' AND LINE = 1 THEN DX_NAME END) AS "Primary Hospital Problem List Diagnosis",
		STRING_AGG((CASE WHEN [Dx Type] = 'Hospital Problem List' THEN DX_NAME END), '; ') AS "Hospital Problem List Diagnoses",
		STRING_AGG((CASE WHEN [Dx Type] = 'Hospital Problem List' THEN CURRENT_ICD10_LIST END), '; ') AS "Hospital Problem List ICD Codes",
		STRING_AGG((CASE WHEN [Dx Type] = 'ED Diagnoses' THEN DX_NAME END), '; ') AS "ED Diagnoses",
		STRING_AGG((CASE WHEN [Dx Type] = 'ED Diagnoses' THEN CURRENT_ICD10_LIST END), '; ') AS "ED Diagnoses ICD Codes",
		STRING_AGG((CASE WHEN [Dx Type] = 'HAR Diagnosis' THEN DX_NAME END), '; ') AS "Billing Diagnoses",
		STRING_AGG((CASE WHEN [Dx Type] = 'HAR Diagnosis' THEN CURRENT_ICD10_LIST END), '; ') AS "Billing Diagnoses ICD Codes"

		{% endif %}



{# define parms which need to be unioned if included #}
{% set union_dict_all = {'toggle_use_admit_order_dx': toggle_use_admit_order_dx,
                        'toggle_use_ed_dxs': toggle_use_ed_dxs,
                        'toggle_use_hsp_prob_list_dxs': toggle_use_hsp_prob_list_dxs,
                        'toggle_use_hsp_billing_dxs': toggle_use_hsp_billing_dxs}
%}

{# create new dictionary only containin True values  #}
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

    {%- if key == 'toggle_use_admit_order_dx' %}
    SELECT * FROM admission_order_dxs	as AOD	WHERE RN_AOD = 1
    {% endif -%}

    {%- if key == 'toggle_use_ed_dxs' %}
    SELECT * FROM ED_DXS				as EDX	WHERE RN_EDX = 1
    {% endif -%}

    {%- if key == 'toggle_use_hsp_prob_list_dxs' %}
    SELECT * FROM HSP_PROBLEM_LIST		as HPL	WHERE RN_HPL = 1
    {% endif -%}

    {%- if key == 'toggle_use_hsp_billing_dxs' %}
    SELECT * FROM HAR_DXS				as HAR	WHERE RN_HAR = 1
    {% endif -%}

    {%- if key != union_dict.keys()|last %}
    Union ALl
    {% endif -%}

    {% endfor %}) as union_dxs on CSNS.CSN = union_dxs.CSN




    GROUP BY MRN, CSNS.CSN

    OPTION(RECOMPILE)