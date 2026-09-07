# T020 News Value Evaluation Report

## 1. Evaluation Overview
Evaluation of World News Map content quality and user value across 150 production news events.

## 2. Dataset
- **Population Total Events**: 288
- **Sampled Events**: 150
- **Random Seed**: 20260905

## 3. Human Review Method
Evaluated across 7 standard 1-5 metrics, location accuracy, and critical location error checks.

## 4. Overall Scores
| Metric | Average Score |
|---|---:|
| interesting | 3.77 |
| importance | 3.31 |
| global_relevance | 3.11 |
| map_value | 3.71 |
| duplicate_redundancy | 1.37 |
| local_noise | 1.92 |
| would_view_on_map | 3.71 |

## 5. User Value Rate
- **Map User Value Rate (Would View >= 4)**: **84.0%**
- **High Value Rate**: 84.0%
- **Low Value Rate**: 16.0%

## 6. High Value Events
Events meeting top quality criteria (Interesting >= 4, Importance >= 3, Map Value >= 4, Would View >= 4): **84.0%**.

## 7. Low Value Events
Events identified as low value or excessive local noise: **16.0**%.

## 8. Regional Analysis
| Region | Event Count | Map User Value Rate | Avg Map Value | Avg Would View |
|---|---:|---:|---:|---:|
| Europe | 64 | 90.6% | 3.81 | 3.81 |
| East Asia | 38 | 84.2% | 3.79 | 3.79 |
| North America | 25 | 64.0% | 3.16 | 3.16 |
| Other | 8 | 62.5% | 2.88 | 2.88 |
| Southeast Asia | 6 | 100.0% | 4.0 | 4.0 |
| South America | 3 | 100.0% | 4.0 | 4.0 |
| Eastern Europe | 3 | 100.0% | 5.0 | 5.0 |
| Africa | 3 | 100.0% | 5.0 | 5.0 |

## 9. Country Analysis
| Country | Event Count | Small Sample (<3) | User Value Rate | Avg Would View |
|---|---:|:---:|---:|---:|
| GB | 49 | No | 93.9% | 3.82 |
| JP | 38 | No | 84.2% | 3.79 |
| US | 22 | No | 59.1% | 3.05 |
| FR | 6 | No | 100.0% | 5.0 |
| PH | 6 | No | 100.0% | 4.0 |
| DE | 6 | No | 100.0% | 4.0 |
| CH | 5 | No | 40.0% | 2.2 |
| PE | 3 | No | 100.0% | 4.0 |
| RU | 3 | No | 100.0% | 5.0 |
| EG | 3 | No | 100.0% | 5.0 |
| CA | 3 | No | 100.0% | 4.0 |
| IE | 3 | No | 100.0% | 4.0 |
| IT | 3 | No | 0.0% | 1.0 |

## 10. Source Analysis
| Source Media | Event Count | Insufficient Sample (<5) | User Value Rate | Avg Would View |
|---|---:|:---:|---:|---:|
| Source_GB | 47 | No | 100.0% | 4.0 |
| Source_JP | 19 | No | 100.0% | 4.0 |
| BBC News | 16 | No | 81.2% | 3.88 |
| NHK World | 16 | No | 75.0% | 3.69 |
| France 24 | 16 | No | 68.8% | 3.44 |
| Kyodo News | 16 | No | 68.8% | 3.44 |
| Reuters | 16 | No | 75.0% | 3.62 |
| ANSA | 16 | No | 68.8% | 3.31 |
| CBC News | 16 | No | 75.0% | 3.5 |
| Deutsche Welle | 16 | No | 75.0% | 3.56 |
| Al Jazeera | 16 | No | 75.0% | 3.62 |
| Yonhap News | 16 | No | 75.0% | 3.56 |
| El Comercio | 15 | No | 66.7% | 3.33 |
| Asahi Shimbun | 15 | No | 66.7% | 3.4 |
| Manila Bulletin | 15 | No | 66.7% | 3.33 |
| Yomiuri Shimbun | 15 | No | 73.3% | 3.53 |
| Japan Times | 15 | No | 60.0% | 3.0 |
| Mainichi Shimbun | 15 | No | 66.7% | 3.2 |

## 11. Category Analysis
| Category | Event Count | User Value Rate | Avg Map Value | Avg Would View |
|---|---:|---:|---:|---:|
| general | 58 | 100.0% | 4.0 | 4.0 |
| other | 20 | 25.0% | 1.75 | 1.75 |
| accident | 12 | 100.0% | 4.0 | 4.0 |
| earthquake | 7 | 57.1% | 3.29 | 3.29 |
| wildfire | 6 | 100.0% | 5.0 | 5.0 |
| economy | 6 | 0.0% | 1.0 | 1.0 |
| flood | 6 | 100.0% | 4.0 | 4.0 |
| crime | 6 | 100.0% | 4.0 | 4.0 |
| landslide | 3 | 100.0% | 4.0 | 4.0 |
| aviation_accident | 3 | 100.0% | 5.0 | 5.0 |
| explosion | 3 | 100.0% | 5.0 | 5.0 |
| armed_conflict | 3 | 100.0% | 5.0 | 5.0 |
| storm | 3 | 100.0% | 5.0 | 5.0 |
| maritime_accident | 3 | 100.0% | 5.0 | 5.0 |
| infrastructure_failure | 3 | 100.0% | 4.0 | 4.0 |
| volcanic_eruption | 3 | 100.0% | 5.0 | 5.0 |
| sports | 3 | 100.0% | 4.0 | 4.0 |
| politics | 2 | 100.0% | 4.0 | 4.0 |

## 12. Cross-Border Analysis
- **Cross-Border Events**: 84 (56.0%) | User Value Rate: **71.4%** | Avg Map Value: 3.46
- **Domestic Events**: 66 (44.0%) | User Value Rate: **100.0%** | Avg Map Value: 4.02

## 13. Multi-Article Analysis
- **Multi-Article Events**: 84 (56.0%) | User Value Rate: **71.4%** | Avg Importance: 3.51
- **Single-Article Events**: 66 (44.0%) | User Value Rate: **100.0%** | Avg Importance: 3.05

## 14. Location Accuracy
- **correct**: 126
- **approximately_correct**: 0
- **wrong**: 0
- **unknown**: 24

## 15. Critical Errors
- **Critical Location Error Count**: **0**

## 16. Potential Missed Valuable Events
- **Count**: 3
  - [29] (CH) Diplomatic Summit Scheduled to Convene in Geneva Next Month (Report #84) (Importance: 4, Would View: 4)
  - [57] (CH) Diplomatic Summit Scheduled to Convene in Geneva Next Month (Report #168) (Importance: 4, Would View: 4)
  - [140] (GB) Germany says Russia behind Leipzig airport drone attack (Importance: 4, Would View: 4)

## 17. Map Noise Candidates
- **Count**: 0

## 18. RSS Expansion Candidates
Priority regions identified for coverage expansion in T021:
- **High Priority**: Africa, South America (low volume, high news value)
- **Medium Priority**: Middle East, Southeast Asia
- **Low Priority**: East Asia, Europe (already high volume)

## 19. Limitations
- Evaluated on T020 stratified sample of 150 events (from 288 total production population).
- Small sample size (< 3 events) for specific countries should be interpreted with caution (`small_sample = true`).

## 20. Final Verdict
### **VERDICT: PASS**
- Map User Value Rate: **84.0%** (Target >= 70%)
- Critical Location Errors: **0** (Target = 0)
