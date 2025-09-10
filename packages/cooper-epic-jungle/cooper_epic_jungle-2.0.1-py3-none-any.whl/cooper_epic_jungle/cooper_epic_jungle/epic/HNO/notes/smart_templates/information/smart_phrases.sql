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

{% if toggle_all_smartphrases %}
SELECT DISTINCT
			InsertNotes.NOTE_ID	as [NOTE_ID]
			,MAX(NEI.CONTACT_SERIAL_NUM)	as [note_csn_id]
			,STRING_AGG(SPHR.SMARTPHRASE_NAME, ': ') as [smartphrases_used]
FROM
        #NOTE_ID AS InsertNotes
        INNER JOIN [Clarity].[dbo].[NOTE_SMARTPHRASE_IDS] as SMID
        ON InsertNotes.NOTE_ID
         = SMID.NOTE_ID
        INNER JOIN [Clarity].[dbo].NOTE_ENC_INFO AS NEI
        ON SMID.NOTE_CSN_ID
         = NEI.CONTACT_SERIAL_NUM
         AND NEI.MOST_RECENT_CNCT_YN = 'Y'
        INNER JOIN [Clarity].[dbo].[CL_SPHR] as SPHR
        ON SPHR.SMARTPHRASE_ID
         = SMID.SMARTPHRASES_ID
GROUP BY InsertNotes.NOTE_ID

{% else %}
SELECT DISTINCT
        InsertNotes.NOTE_ID	as [NOTE_ID],
        SPHR.SMARTPHRASE_NAME as [smartphrase_name],
        CASE WHEN SPHR.SMARTPHRASE_NAME IS NOT NULL THEN 'yes' ELSE 'no' END as had_smartphrase_documented
FROM
    #NOTE_ID AS InsertNotes
    INNER JOIN [Clarity].[dbo].[NOTE_SMARTPHRASE_IDS] as SMID
    ON InsertNotes.NOTE_ID
     = SMID.NOTE_ID
    INNER JOIN [Clarity].[dbo].NOTE_ENC_INFO AS NEI
    ON SMID.NOTE_CSN_ID
     = NEI.CONTACT_SERIAL_NUM
     AND NEI.MOST_RECENT_CNCT_YN = 'Y'
    INNER JOIN [Clarity].[dbo].[CL_SPHR] as SPHR
    ON SPHR.SMARTPHRASE_ID
     = SMID.SMARTPHRASES_ID
WHERE
    SPHR.SMARTPHRASE_NAME = '{{ target_smartphrase }}'

{% endif %}

OPTION(RECOMPILE)

