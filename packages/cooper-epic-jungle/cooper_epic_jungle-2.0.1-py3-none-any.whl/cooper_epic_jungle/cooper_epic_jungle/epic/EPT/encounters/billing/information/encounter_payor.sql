SET NOCOUNT ON;

IF OBJECT_ID('tempdb.dbo.#CSN', 'U') IS NOT NULL
  DROP TABLE #CSN; 

DECLARE @CSN TABLE
(
	CSN NVARCHAR(50)
)

--------INSERTION CLAUSES
--INSERT INTO @CSN (CSN) VALUES('1052366722');
{{ CSN }};

SELECT * 
INTO #CSN
FROM @CSN;

with Coverage AS (
    Select Encounter.EncounterEpicCsn AS CSN
          ,PrimaryCoverage.BenefitPlanName AS primary_plan
          ,PrimaryCoverage.PayorName AS  primary_payor
          ,PrimaryCoverage.Payorfinancialclass AS primary_financial_class
          ,SecondCoverage.BenefitPlanName AS secondary_plan
          ,SecondCoverage.PayorName AS secondary_payor
          ,SecondCoverage.Payorfinancialclass AS secondary_financial_class
          ,RN = ROW_NUMBER() OVER (PARTITION BY Encounter.EncounterEpicCsn ORDER BY PrimaryCoverage.BenefitPlanName ASC)

    From #CSN Discharges
    INNER JOIN CDW.FullAccess.EncounterFact Encounter
    ON Discharges.CSN
     = Encounter.EncounterEpicCsn
    INNER JOIN CDW.FullAccess.BillingAccountFact BillingAccount
    ON Encounter.EncounterKey
     = BillingAccount.PrimaryEncounterKey
    INNER JOIN CDW.FullAccess.CoverageDim PrimaryCoverage
    ON (BillingAccount.PrimaryCoverageKey
     = PrimaryCoverage.CoverageKey)
    INNER JOIN CDW.FullAccess.CoverageDim SecondCoverage
    ON (BillingAccount.SecondCoverageKey
     = SecondCoverage.CoverageKey)
    )
Select
           CSN
          ,primary_plan
          ,primary_payor
          ,primary_financial_class
          ,secondary_plan
          ,secondary_payor
          ,secondary_financial_class
from coverage cov
where RN ='1'
OPTION(RECOMPILE)