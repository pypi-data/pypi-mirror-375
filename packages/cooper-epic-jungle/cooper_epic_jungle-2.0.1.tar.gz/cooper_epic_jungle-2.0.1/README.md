# CooperEpicJungle

This is the Cooper internal Epic Jungle. It  is an extension of the MiPi package.
It contains pre-configured SQL templates

## Access the scripts using mipi

```python
# Import the data manager
from mipi_datamanager import DataManager

# Import the Epic Jungle
from cooper_epic_jungle import COOPER_EPIC_JUNGLE

# use the default jungle with all of its presets (COOPER_EPIC_JUNGLE)
mipi = DataManager.from_jinja_repo_preset("epic/EPT/encounters/ambulatory/population/generic.sql")

# override the jungle for the entire datamanager object
from cooper_epic_jungle import EPT
mipi = DataManager.from_jinja_repo_preset(override_jinja_repo_source=EPT)


```