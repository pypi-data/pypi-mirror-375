/*
Description: This script reports on progress notes using encounter
			 CSN to pull provider progress notes
Authors: Temi Nanna
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
--INSERT INTO @CSN (CSN) VALUES('1056986421');

SELECT * 
INTO #CSN
FROM @CSN;


with cte as (
    SELECT CSNS.CSN                                           AS CSN
          , hno.NOTE_ID                                       AS NOTE_ID                            -- HNO.1
          , HNO.CRT_INST_LOCAL_DTTM                           AS note_creation_datetime
          , HNO.LST_FILED_INST_DTTM                           AS note_last_updated_datetime
          , FORMAT(NET.IP_ACTION_DTTM, 'yyyy-MM-dd hh:mm tt') AS provider_note_signed_dttm -- HNO.34052
          , DATEDIFF(DAY,PE.APPT_TIME, NET.IP_ACTION_DTTM)    AS days_from_visit_to_note_signed
          , DPROV.PROV_ID                                     AS author_prov_id
          , DPROV.PROV_NAME                                   AS author_name
          , DPROV.PROVIDER_TYPE                               AS author_type
          , DPROV.SPECIALTY_NAME                              AS author_primary_specialty
          , DPROV.DEPARTMENT_NAME                             AS author_primary_department
          , ZNT.Name
          , RN = ROW_NUMBER()                                    OVER (PARTITION BY csns.csn ORDER BY CASE WHEN znt.NAME = 'Progress Notes' THEN 10 ELSE 5 END DESC, NET.IP_ACTION_DTTM DESC)
    FROM #CSN as CSNS
          INNER JOIN Clarity.dbo.PAT_ENC AS PE
                     ON CSNS.CSN
                      = PE.PAT_ENC_CSN_ID
          INNER JOIN Clarity.dbo.HNO_INFO AS hno
                     ON PE.PAT_ENC_CSN_ID
                      = HNO.PAT_ENC_CSN_ID
          INNER JOIN Clarity.dbo.CLARITY_SER AS SER
                     ON SER.PROV_ID
                      = PE.VISIT_PROV_ID
                        AND SER.USER_ID = HNO.CURRENT_AUTHOR_ID
          INNER JOIN Clarity.dbo.D_PROV_PRIMARY_HIERARCHY as DPROV
                     ON DPROV.PROV_ID
                      = SER.PROV_ID
          INNER JOIN Clarity.dbo.ZC_NOTE_TYPE AS ZNT
                     ON ZNT.NOTE_TYPE_C
                      = HNO.IP_NOTE_TYPE_C
          LEFT JOIN Clarity.dbo.NOTE_EDIT_TRAIL AS net
                    ON net.NOTE_ID
                      = hno.NOTE_ID
                        AND net.IP_ACTION_ON_NOTE_C = 2
                        AND net.IP_ACTION_USER_ID = SER.USER_ID
    )

SELECT
    CSN
    ,NOTE_ID
    ,note_creation_datetime
    ,note_last_updated_datetime
    ,provider_note_signed_dttm
    ,days_from_visit_to_note_signed
    ,author_prov_id
    ,author_name
    ,author_type
    ,author_primary_specialty
    ,author_primary_department
FROM cte
WHERE RN = 1

OPTION(RECOMPILE);

IF OBJECT_ID('tempdb.dbo.#CSN', 'U') IS NOT NULL
  DROP TABLE #CSN;