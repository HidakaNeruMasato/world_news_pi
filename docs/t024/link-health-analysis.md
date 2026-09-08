# T024 Production Link Health & Real Data Analysis

## 1. Real Data Verification Matrix (120 Active Events / 120 Articles)

Production DB の全 120 アクティブイベント・120 記事を対象にリンク検証を実施しました。

| Metric / Status | Count / Value | Percentage |
|---|---:|---:|
| **Total Articles Checked** | 120 | 100.0% |
| **Media Sources Represented** | 18 | - |
| **Active (`active`)** | 111 | 92.5% |
| **Redirected (`redirected`)** | 5 | 4.2% |
| **Not Found (`not_found`)** | 2 | 1.7% |
| **Gone (`gone`)** | 0 | 0.0% |
| **Blocked (`blocked`)** | 1 | 0.8% |
| **Temporary Error (`temporary_unavailable`)**| 1 | 0.8% |
| **Timeout (`timeout`)** | 0 | 0.0% |
| **Invalid (`invalid`)** | 0 | 0.0% |

---

## 2. Key Reliability Performance Indicators (KPIs)

* **Link Availability Rate**: `96.7%`
  $$\text{Link Availability Rate} = \frac{\text{Active} + \text{Redirected}}{\text{Total Checked}} = \frac{111 + 5}{120} = 96.7\%$$

* **Event Reachability Rate**: `98.3%`
  $$\text{Event Reachability Rate} = \frac{\text{Active Events with } \ge 1 \text{ usable article}}{\text{Total Active Events}} = \frac{118}{120} = 98.3\%$$

* **Canonical URLs Discovered**: `116` (96.7%)
* **URL Redirects Processed**: `5` (4.2%)
* **Alternative Articles Triggered**: `2` Events
