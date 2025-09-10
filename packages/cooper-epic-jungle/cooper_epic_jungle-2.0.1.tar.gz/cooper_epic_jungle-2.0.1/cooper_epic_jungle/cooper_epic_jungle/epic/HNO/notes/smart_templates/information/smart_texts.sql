SET NOCOUNT ON;

IF OBJECT_ID('tempdb.dbo.#NOTE_ID', 'U') IS NOT NULL
  DROP TABLE #NOTE_ID; 

DECLARE @NOTE_ID TABLE
(
	NOTE_ID NVARCHAR(50)
)

-- INSERTION CLAUSES
{{ NOTE_ID }};
--INSERT INTO @NOTE_ID (NOTE_ID) VALUES('955069643')

SELECT * 
INTO #NOTE_ID
FROM @NOTE_ID;
{% if toggle_all_smarttexts %}
SELECT DISTINCT
        InsertNotes.NOTE_ID	as [NOTE_ID]
        ,MAX(NEI.CONTACT_SERIAL_NUM)	as [note_csn_id]
        ,STRING_AGG(SMTX.SMARTTEXT_NAME, '; ') as [smarttexts_used]
  FROM 
        #NOTE_ID AS InsertNotes
        INNER JOIN [Clarity].[dbo].[NOTE_SMARTTEXT_IDS] as SMTXIDS
        ON InsertNotes.NOTE_ID
         = SMTXIDS.NOTE_ID
        INNER JOIN [Clarity].[dbo].NOTE_ENC_INFO AS NEI
        ON SMTXIDS.NOTE_CSN_ID
         = NEI.CONTACT_SERIAL_NUM
         AND NEI.MOST_RECENT_CNCT_YN = 'Y'
        INNER JOIN [Clarity].[dbo].SMARTTEXT as SMTX
        ON SMTXIDS.SMARTTEXTS_ID
         = SMTX.SMARTTEXT_ID
GROUP BY InsertNotes.NOTE_ID

{% else %}
SELECT DISTINCT
        InsertNotes.NOTE_ID	as [NOTE_ID]
        ,SMTX.SMARTTEXT_NAME as [smarttexts_name]
        ,CASE WHEN SMTX.SMARTTEXT_NAME IS NOT NULL THEN 'yes' ELSE 'no' END as had_smarttext_documented
  FROM
        #NOTE_ID AS InsertNotes
        INNER JOIN [Clarity].[dbo].[NOTE_SMARTTEXT_IDS] as SMTXIDS
        ON InsertNotes.NOTE_ID
         = SMTXIDS.NOTE_ID
        INNER JOIN [Clarity].[dbo].NOTE_ENC_INFO AS NEI
        ON SMTXIDS.NOTE_CSN_ID
         = NEI.CONTACT_SERIAL_NUM
         AND NEI.MOST_RECENT_CNCT_YN = 'Y'
        INNER JOIN [Clarity].[dbo].SMARTTEXT as SMTX
        ON SMTXIDS.SMARTTEXTS_ID
         = SMTX.SMARTTEXT_ID
  WHERE
		SMTX.SMARTTEXT_NAME = '{{ target_smarttext }}'
{% endif %}

OPTION(RECOMPILE)
