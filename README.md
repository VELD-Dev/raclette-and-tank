# Raclette & Tank Importer
Raclette And Tank Importer (RATI lol) is a Blender plugin that exports a map of Ratchet &amp; Clank from .dat files to Blender.

## How to use ?
### Step 1
Go to `USRDIR > packed > levels > LEVEL_NAME`, use PSArcTool or PS3GameExtractor and extract:
1. `global_cached.psarc` for the models and everything
2. `global_uncached.psarc` for the scripts *(not necessary but can help fangame developers)*

### Step 2
Open Blender.  
Click `Edit` in the topbar, then `⚙ Preferences`.  
Go to `Add-ons` category, and search for `Raclette and Tank Importer` (it is in `Reverse-Engineering` category)  
Click the check mark to enable the plugin.

### Step 3
Click `File` in the topbar, then `📥 Import`.  
Press `Extract & Import RAC Assets (.dat) (experimental)`.

### Step 4
In the browser, search for `main.dat` or `assetlookup.dat` (depending on which game you want to export models)  
Check or uncheck options depending what you want to export and have on Blender. You can always import previously non-imported elements to the scene by redoing the [Step 3](#Step_3). Do not forget to uncheck what you already imported to avoid duplicates.

### Additional info
Each category of model (mobys, ties, shrubs, etc...) are splitted to different Collections.
