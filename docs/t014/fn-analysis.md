# T014 False Negative (FN) Root Cause Analysis Report

Total False Negatives Analyzed: **32 items**

## 1. FN Classification Breakdown

- **FN-01 obvious_event_missed**: 19 items (59.4%)
- **FN-08 location_missing**: 10 items (31.2%)
- **FN-02 followup_event_missed**: 3 items (9.4%)

## 2. Pipeline Root Cause Stage

- **LLM_CLASSIFICATION**: 32 items (100% at LLM Event Classification stage)

## 3. Detailed FN Item List

### [FN-01] Article #10: Russian attack hits rail workers in new deadly strikes on Kyiv
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-02] Article #11: The final minutes before floodwater crashed through Nepal-China border
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-03] Article #12: Israeli fire kills three in Gaza City during reported raid, medics say
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-04] Article #13: Ex-gang boss guilty of orchestrating 1996 murder of rapper Tupac Shakur
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-05] Article #14: Teen girl charged with murder over recording of San Diego mosque attack
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-06] Article #24: Man arrested after Swiss rave shooting that killed woman
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-07] Article #25: US and Iran trade strikes for first time in weeks
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-08] Article #30: Two dead and more than a dozen missing after 'terrifying' flash flood hits Grand Canyon
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-09] Article #40: Orangutans in danger as wildfires blaze through Borneo
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-10] Article #42: 'I haven't lost my hope' - the search for missing loved ones
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-11] Article #43: Nepal flood relief vehicles trapped as heavy rain turns roads to mud
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-12] Article #45: 97-year-old woman rescued after Nepali floods looked like 'a warrior'
- **Source**: Source_GB (GB)
- **Classification**: `FN-02 followup_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-02 followup_event_missed.

### [FN-13] Article #47: Strong M6.8 Earthquake hits Ishikawa Prefecture
- **Source**: Source_JP (JP)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-14] Article #48: Fire breaks out at London historical building
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-15] Article #57: Iran retaliates after US strikes kill four at wedding party, state media reports
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-16] Article #63: As Michigan Senate race heats up, Vance calls El-Sayed 'evil'
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.9
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-17] Article #65: 'I have fired 40 of my agents for being corrupt', says Nigeria's anti-corruption chief
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-18] Article #75: Tiger Woods to change plea after crash arrest
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-19] Article #76: Zelensky says airlines should avoid Russian airspace as Ukraine escalates drone operations
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-20] Article #89: Bus crash on Egypt's Red Sea coast kills 16
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-21] Article #105: Thousands still missing as Nepal-Tibet flood relief and recovery intensifies
- **Source**: Source_GB (GB)
- **Classification**: `FN-02 followup_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-02 followup_event_missed.

### [FN-22] Article #109: More than 900 killed in Gaza this year despite ceasefire, Hamas-run health ministry says
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-23] Article #112: EU and Nato vow to step up pressure on Russia after 'new escalation' in Germany
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-24] Article #116: 'Nothing but mud and silt' - the village swept away by deadly floods in Nepal
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-25] Article #119: Iranian attack on Saudi tanker killed two Filipino sailors, Saudi Arabia says
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-26] Article #148: Why Nepal floods should worry India
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-27] Article #165: Sydney police investigate second possible mistaken identity killing in two days
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-28] Article #182: Toxic wildfire haze spreads across South East Asia as 'super' El Niño intensifies
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-29] Article #187: Palestinian teens killed during settler attack on West Bank village, officials say
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-30] Article #188: Anthony Joshua's driver attempted overtake before fatal crash, trial hears
- **Source**: Source_GB (GB)
- **Classification**: `FN-01 obvious_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-01 obvious_event_missed.

### [FN-31] Article #200: ICE agent charged with lying about shooting Venezuelan man during crackdown
- **Source**: Source_GB (GB)
- **Classification**: `FN-08 location_missing`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-08 location_missing.

### [FN-32] Article #201: Nepal tunnel rescuers hunt for survivors with rafts and drone
- **Source**: Source_GB (GB)
- **Classification**: `FN-02 followup_event_missed`
- **Root Cause Stage**: `LLM_CLASSIFICATION`
- **AI Confidence**: 0.0
- **Notes**: LLM Prompt v1 classified this real news event as is_event=false. Root cause: conservative trigger threshold for FN-02 followup_event_missed.

