# 5G SA Core Analytics - Executive Demo Guide

## Overview

This demo showcases Splunk's ability to provide end-to-end visibility across a 5G Standalone Core network. The audience will see how Splunk enables a telecom operator to monitor service health, detect degradations before they become outages, and rapidly isolate root cause -- all from a single platform.

**Target audience:** C-level executives, VP of Network Operations, VP of Engineering, CTO

**Demo duration:** 5-7 minutes

---

## The Scenario

You are the VP of Network Operations at a major telecom operator running a 5G SA Core across three regions:

| Region | Sites | Role |
|---|---|---|
| US-East | east-dc1, east-dc2 | Primary US market |
| US-West | west-dc1, west-dc2 | Secondary US market |
| EU-Central | eu-dc1, eu-dc2 | European market |

The network supports three 5G network slices:

- **eMBB** (Enhanced Mobile Broadband) -- Consumer and enterprise broadband
- **URLLC** (Ultra-Reliable Low-Latency Communication) -- Premium, mission-critical services
- **mMTC** (Massive Machine-Type Communication) -- IoT and sensor networks

Eight core network functions are monitored: AMF, SMF, UPF, AUSF, PCF, UDM, NRF, and NSSF.

## What Happened (Injected Incidents)

### Minor Incident (3 days ago)
A brief PCF policy latency spike in EU-Central. It self-resolved within 45 minutes with no subscriber impact. This appears as a small blip in the weekly trend view.

### Major Incident (Today, 07:30-09:00 UTC)
A correlated, multi-NF service degradation in US-East:

1. **07:30** -- AMF registration latency begins rising on `amf-east-01` in US-East
2. **07:45** -- SMF session establishment success rate starts dropping on `smf-east-02`
3. **08:00** -- UPF packet drops spike on `upf-east-01`, specifically hitting the premium URLLC slice
4. **08:00** -- Critical alert fires: registration success rate below 92%
5. **08:15** -- Critical alert: URLLC packet loss exceeds SLA at 8.5%
6. **08:30** -- AMF and SMF begin recovering
7. **09:00** -- UPF packet drops return to normal, all services restored

The combined effect: subscriber experience degraded in US-East, with the premium URLLC slice most severely impacted.

---

## Demo Flow (5-7 minutes)

### Opening (30 seconds)

> "Let me show you how Splunk gives us real-time visibility into our entire 5G SA Core -- across all regions, all network functions, and all service slices -- from a single pane of glass."

Open the **5G SA Core Analytics** app. You land on the **Service Health Overview** dashboard.

### Dashboard 1: Service Health Overview (2-3 minutes)

**Step 1: Set the stage**

Set the time range to **Last 7 days**. Leave Region set to **All Regions**.

> "Here's our 5G SA Core environment. We're monitoring 33 network function instances across three regions, serving hundreds of thousands of subscribers across three network slices."

Point to the top KPI row:

> "At a glance, I can see our overall registration success rate, session establishment rate, total active subscribers, and any critical alerts. These are the numbers that tell me whether the network is healthy."

**Step 2: Spot the anomaly**

Point to the **Service Success Rates Over Time** timechart:

> "Looking at the weekly trend, you can see the network has been stable for the past week. But look at today -- there's a clear dip in both registration and session success rates. Something happened."

Point to the **Control Plane Latency** timechart:

> "And here we can see a corresponding latency spike. These are correlated -- when latency goes up, success rates go down."

**Step 3: Isolate the region**

Point to the **Service Health by Region** column chart:

> "Now look at the regional breakdown. US-West and EU-Central are healthy. US-East is the outlier -- its success rates are noticeably lower. The problem is concentrated in one region."

Change the Region dropdown to **US-East**:

> "Let me filter down to US-East. Now the KPI singles and trend lines show just this region, and the degradation is much more pronounced."

**Step 4: Identify the slice impact**

Point to the **Impact by Network Slice** chart:

> "Look at the slice breakdown. The URLLC slice -- our premium, mission-critical service tier -- has significantly higher packet drops than eMBB or mMTC. This is the slice where SLA violations have the most business impact."

**Step 5: Review alerts**

Point to the **Current Issues and Alerts** table:

> "And at the bottom, we can see the alerts that fired. Critical alerts on the AMF for registration failures, and on the UPF for URLLC packet loss exceeding our SLA threshold. Multiple NFs were affected, all tied to the same incident correlation ID."

> "So within 30 seconds of looking at this dashboard, I know: something went wrong today in US-East, it impacted our premium URLLC slice, and multiple network functions were involved. Now let me drill into the operations view to understand what happened."

### Transition (15 seconds)

Click on **Operations Drilldown** in the navigation.

> "This second dashboard is where our operations team investigates. Let me show you how we go from 'something is wrong' to 'here's what caused it.'"

### Dashboard 2: Operations Drilldown (2-3 minutes)

**Step 1: Set filters**

Set time range to **Last 24 hours**. Set Region to **US-East**. Leave NF Type and Slice at **All**.

> "I'm focused on US-East over the last 24 hours."

**Step 2: Alert timeline**

Point to the **Alert Timeline by Severity** chart:

> "Here's the alert sequence. We can see warnings starting around 07:30, escalating to high and then critical alerts by 08:00. The timeline tells the story of the incident progression."

**Step 3: KPI correlation**

Point to the **KPI Degradation Timeline** chart:

> "And here's the KPI view -- latency and packet drops over time. You can see them spike in the same window as the alerts. This is Splunk correlating infrastructure metrics with service KPIs in real time."

**Step 4: NF instance isolation**

Change NF Type to **AMF**:

> "Now let me isolate by network function. Starting with the AMF -- our registration handler."

Point to the **NF Instance Health** table:

> "Look at the instance table. `amf-east-01` had elevated CPU, high error rate, and was in 'degraded' status. `amf-east-02` was healthy. One specific instance was the problem."

Point to the **NF Error Rate Over Time** chart:

> "And the error rate timeline confirms it -- `amf-east-01` spiked while the other AMF instances stayed flat. Splunk is showing us exactly which instance was affected."

**Step 5: See the CPU correlation**

Point to the **NF CPU Utilization Over Time** chart:

> "CPU utilization tells the same story. `amf-east-01` hit near 80% while others stayed at baseline. High CPU drove the latency, which drove the registration failures."

**Step 6: Multi-NF correlation**

Change NF Type to **UPF**:

> "Now let me check the User Plane Function. Same story -- `upf-east-01` shows elevated errors and CPU, while `upf-east-02` is clean."

Change Slice to **URLLC**:

> "And when I filter to the URLLC slice, the subscriber experience impact is obvious -- quality scores dropped and latency spiked."

**Step 7: Full incident picture**

Change NF Type and Slice back to **All**. Point to the **Incident Detail** table:

> "The full incident table ties it all together. We can see the progression from warning to critical, across AMF, SMF, and UPF, all sharing the same incident correlation ID. The operations team can see exactly what changed, which NF instances were involved, and which subscribers were impacted."

### Closing (30 seconds)

> "In about 5 minutes, we went from an executive health overview to root-cause direction. We identified the region, the network functions, the specific instances, and the subscriber impact -- all from Splunk."
>
> "This is the power of having your 5G SA Core telemetry in Splunk: end-to-end visibility, real-time correlation, and fast triage. The same platform that monitors your network also powers your incident response."

---

## Key Value Messages

1. **End-to-end visibility** -- One platform spanning all 8 core NFs, all regions, all slices
2. **Proactive detection** -- Splunk surfaces degradations before they become customer-impacting outages
3. **Rapid triage** -- Go from "something is wrong" to "here's which instance caused it" in minutes, not hours
4. **Cross-domain correlation** -- Link infrastructure health (CPU, memory) to control-plane KPIs (latency, success rate) to subscriber experience (quality score, complaints) in a single view
5. **Operational resilience** -- Incident correlation IDs, alert timelines, and drilldown capabilities accelerate MTTR

---

## Setup Instructions

### Prerequisites
- Splunk Enterprise (local instance)
- Both apps installed:
  - `TA_5g_sa_core` (Technology Add-on)
  - `app_5g_sa_core_demo` (Demo app)

### Loading Data

1. Generate fresh sample data (recommended before each demo):
   ```bash
   cd $SPLUNK_HOME/etc/apps/TA_5g_sa_core/bin
   python3 generate_sample_data.py
   ```

2. Restart Splunk to pick up the new data:
   ```bash
   $SPLUNK_HOME/bin/splunk restart
   ```

3. If re-running, clean old data first:
   ```bash
   $SPLUNK_HOME/bin/splunk stop
   $SPLUNK_HOME/bin/splunk clean eventdata -index fiveg_sa_core -f
   $SPLUNK_HOME/bin/splunk start
   ```

4. Navigate to **5G SA Core Analytics** in the app menu.

### Verifying Data Loaded

Run this search to confirm:
```
index=fiveg_sa_core | stats count by sourcetype
```

Expected: ~66k `5g:nf:metrics`, ~18k `5g:service:kpi`, ~36k `5g:subscriber:experience`, ~18 `5g:core:alerts`.

---

## Optional Enhancements

If extending this demo beyond the initial scope:

- **Real-time alerting** -- Add saved searches with alert actions to demonstrate proactive notification
- **ITSI integration** -- Show KPI-based service monitoring with glass tables
- **ML-powered anomaly detection** -- Use MLTK to detect abnormal patterns without static thresholds
- **Incident response automation** -- Integrate with SOAR for automated runbooks
- **Capacity planning** -- Add dashboards showing NF resource utilization trends for planning
- **SLA reporting** -- Build scheduled reports tracking SLA compliance by slice and region
- **Dashboard Studio** -- Rebuild dashboards in Dashboard Studio for more polished visual design

---

## Design Simplifications

This demo intentionally trades telecom completeness for clarity:

- Uses readable field names instead of 3GPP TS 28.552 counter names
- Slices are plain strings (eMBB/URLLC/mMTC) instead of S-NSSAI encoding
- No SBI HTTP/2 signaling trace data -- focuses on aggregated KPIs
- No SUPI/SUCI subscriber identifiers -- uses segment-level aggregation
- Single index instead of production multi-tier retention
- Static sample data instead of live streaming ingestion
