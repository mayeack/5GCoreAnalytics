#!/usr/bin/env python3
"""
Generate synthetic 5G SA Core sample data for Splunk demo.

Produces 7 days of telemetry across 4 sourcetypes with realistic
diurnal patterns and injected incidents for demo storytelling.

Usage:
    python3 generate_sample_data.py [--output-dir ../samples]
"""

import json
import os
import sys
import random
import math
import argparse
from datetime import datetime, timedelta, timezone

random.seed(2026)

INTERVAL_MINUTES = 5
DAYS = 7

REGIONS = ["US-East", "US-West", "EU-Central"]

REGION_SITES = {
    "US-East": ["east-dc1", "east-dc2"],
    "US-West": ["west-dc1", "west-dc2"],
    "EU-Central": ["eu-dc1", "eu-dc2"],
}

SLICES = ["eMBB", "URLLC", "mMTC"]
SEGMENTS = ["consumer", "enterprise"]

NF_INSTANCES = [
    {"nf_instance": "amf-east-01", "nf_type": "AMF", "region": "US-East", "site": "east-dc1"},
    {"nf_instance": "amf-east-02", "nf_type": "AMF", "region": "US-East", "site": "east-dc2"},
    {"nf_instance": "amf-west-01", "nf_type": "AMF", "region": "US-West", "site": "west-dc1"},
    {"nf_instance": "amf-west-02", "nf_type": "AMF", "region": "US-West", "site": "west-dc2"},
    {"nf_instance": "amf-eu-01",   "nf_type": "AMF", "region": "EU-Central", "site": "eu-dc1"},
    {"nf_instance": "amf-eu-02",   "nf_type": "AMF", "region": "EU-Central", "site": "eu-dc2"},
    {"nf_instance": "smf-east-01", "nf_type": "SMF", "region": "US-East", "site": "east-dc1"},
    {"nf_instance": "smf-east-02", "nf_type": "SMF", "region": "US-East", "site": "east-dc2"},
    {"nf_instance": "smf-west-01", "nf_type": "SMF", "region": "US-West", "site": "west-dc1"},
    {"nf_instance": "smf-west-02", "nf_type": "SMF", "region": "US-West", "site": "west-dc2"},
    {"nf_instance": "smf-eu-01",   "nf_type": "SMF", "region": "EU-Central", "site": "eu-dc1"},
    {"nf_instance": "smf-eu-02",   "nf_type": "SMF", "region": "EU-Central", "site": "eu-dc2"},
    {"nf_instance": "upf-east-01", "nf_type": "UPF", "region": "US-East", "site": "east-dc1"},
    {"nf_instance": "upf-east-02", "nf_type": "UPF", "region": "US-East", "site": "east-dc2"},
    {"nf_instance": "upf-west-01", "nf_type": "UPF", "region": "US-West", "site": "west-dc1"},
    {"nf_instance": "upf-west-02", "nf_type": "UPF", "region": "US-West", "site": "west-dc2"},
    {"nf_instance": "upf-eu-01",   "nf_type": "UPF", "region": "EU-Central", "site": "eu-dc1"},
    {"nf_instance": "upf-eu-02",   "nf_type": "UPF", "region": "EU-Central", "site": "eu-dc2"},
    {"nf_instance": "ausf-east-01","nf_type": "AUSF","region": "US-East", "site": "east-dc1"},
    {"nf_instance": "ausf-west-01","nf_type": "AUSF","region": "US-West", "site": "west-dc1"},
    {"nf_instance": "ausf-eu-01",  "nf_type": "AUSF","region": "EU-Central", "site": "eu-dc1"},
    {"nf_instance": "pcf-east-01", "nf_type": "PCF", "region": "US-East", "site": "east-dc1"},
    {"nf_instance": "pcf-west-01", "nf_type": "PCF", "region": "US-West", "site": "west-dc1"},
    {"nf_instance": "pcf-eu-01",   "nf_type": "PCF", "region": "EU-Central", "site": "eu-dc1"},
    {"nf_instance": "udm-east-01", "nf_type": "UDM", "region": "US-East", "site": "east-dc1"},
    {"nf_instance": "udm-west-01", "nf_type": "UDM", "region": "US-West", "site": "west-dc1"},
    {"nf_instance": "udm-eu-01",   "nf_type": "UDM", "region": "EU-Central", "site": "eu-dc1"},
    {"nf_instance": "nrf-east-01", "nf_type": "NRF", "region": "US-East", "site": "east-dc1"},
    {"nf_instance": "nrf-west-01", "nf_type": "NRF", "region": "US-West", "site": "west-dc1"},
    {"nf_instance": "nrf-eu-01",   "nf_type": "NRF", "region": "EU-Central", "site": "eu-dc1"},
    {"nf_instance": "nssf-east-01","nf_type": "NSSF","region": "US-East", "site": "east-dc1"},
    {"nf_instance": "nssf-west-01","nf_type": "NSSF","region": "US-West", "site": "west-dc1"},
    {"nf_instance": "nssf-eu-01",  "nf_type": "NSSF","region": "EU-Central", "site": "eu-dc1"},
]

NF_BASE_CPU = {"AMF": 40, "SMF": 35, "UPF": 50, "AUSF": 25, "PCF": 30, "UDM": 28, "NRF": 20, "NSSF": 22}
NF_BASE_MEM = {"AMF": 55, "SMF": 50, "UPF": 60, "AUSF": 40, "PCF": 45, "UDM": 42, "NRF": 35, "NSSF": 38}
NF_BASE_CONN = {"AMF": 15000, "SMF": 12000, "UPF": 8000, "AUSF": 5000, "PCF": 6000, "UDM": 4000, "NRF": 3000, "NSSF": 2000}
NF_BASE_RPS = {"AMF": 1200, "SMF": 900, "UPF": 600, "AUSF": 400, "PCF": 500, "UDM": 350, "NRF": 200, "NSSF": 150}

SLICE_BASE_SUBS = {"eMBB": 45000, "URLLC": 8000, "mMTC": 120000}
SLICE_BASE_THROUGHPUT = {"eMBB": 285.0, "URLLC": 12.0, "mMTC": 0.8}
SLICE_BASE_LATENCY = {"eMBB": 18.0, "URLLC": 3.0, "mMTC": 45.0}
SLICE_BASE_SETUP_TIME = {"eMBB": 120, "URLLC": 25, "mMTC": 200}

REGION_SCALE = {"US-East": 1.0, "US-West": 0.85, "EU-Central": 0.75}
SEGMENT_SCALE = {"consumer": 0.7, "enterprise": 0.3}


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def jitter(base, pct=0.05):
    return base * (1.0 + random.gauss(0, pct))


def diurnal_factor(dt):
    """0.5 at 4am, 1.0 at peak (2pm UTC)."""
    hour = dt.hour + dt.minute / 60.0
    return 0.65 + 0.35 * math.sin(math.pi * (hour - 4) / 12)


def incident_severity(dt, start, peak, end):
    """Ramp 0->1 from start to peak, then 1->0 from peak to end."""
    if dt < start or dt > end:
        return 0.0
    if dt <= peak:
        total = (peak - start).total_seconds()
        elapsed = (dt - start).total_seconds()
        return elapsed / total if total > 0 else 1.0
    total = (end - peak).total_seconds()
    elapsed = (dt - peak).total_seconds()
    return 1.0 - elapsed / total if total > 0 else 0.0


class IncidentManager:
    def __init__(self, end_time):
        d = end_time.replace(hour=0, minute=0, second=0, microsecond=0)
        self.incidents = {
            "amf_latency": {
                "start": d.replace(hour=7, minute=30),
                "peak":  d.replace(hour=8, minute=0),
                "end":   d.replace(hour=8, minute=15),
                "nf_instance": "amf-east-01",
                "region": "US-East",
            },
            "upf_drops": {
                "start": d.replace(hour=8, minute=0),
                "peak":  d.replace(hour=8, minute=30),
                "end":   d.replace(hour=9, minute=0),
                "nf_instance": "upf-east-01",
                "region": "US-East",
                "slice": "URLLC",
            },
            "smf_sessions": {
                "start": d.replace(hour=7, minute=45),
                "peak":  d.replace(hour=8, minute=0),
                "end":   d.replace(hour=8, minute=30),
                "nf_instance": "smf-east-02",
                "region": "US-East",
            },
            "pcf_eu_minor": {
                "start": (d - timedelta(days=3)).replace(hour=14, minute=0),
                "peak":  (d - timedelta(days=3)).replace(hour=14, minute=15),
                "end":   (d - timedelta(days=3)).replace(hour=14, minute=45),
                "nf_instance": "pcf-eu-01",
                "region": "EU-Central",
            },
        }

    def sev(self, key, dt):
        inc = self.incidents[key]
        return incident_severity(dt, inc["start"], inc["peak"], inc["end"])

    def region_affected(self, key, region, dt):
        inc = self.incidents[key]
        return inc["region"] == region and self.sev(key, dt) > 0


def generate_timestamps(end_time):
    start = end_time - timedelta(days=DAYS)
    ts = start
    timestamps = []
    while ts <= end_time:
        timestamps.append(ts)
        ts += timedelta(minutes=INTERVAL_MINUTES)
    return timestamps


def generate_nf_metrics(timestamps, im):
    events = []
    for ts in timestamps:
        load = diurnal_factor(ts)
        for nf in NF_INSTANCES:
            nft = nf["nf_type"]
            cpu = jitter(NF_BASE_CPU[nft] * load, 0.08)
            mem = jitter(NF_BASE_MEM[nft], 0.05)
            conn = int(jitter(NF_BASE_CONN[nft] * load, 0.1))
            rps = round(jitter(NF_BASE_RPS[nft] * load, 0.08), 1)
            error_rate = round(max(0, random.gauss(0.02, 0.008)), 3)
            status = "healthy"

            nfi = nf["nf_instance"]

            s = im.sev("amf_latency", ts) if nfi == "amf-east-01" else 0
            if s > 0:
                cpu += 35 * s
                error_rate += 5.0 * s
                status = "degraded" if s > 0.3 else "warning"

            s = im.sev("upf_drops", ts) if nfi == "upf-east-01" else 0
            if s > 0:
                cpu += 25 * s
                error_rate += 3.0 * s
                status = "degraded" if s > 0.3 else "warning"

            s = im.sev("smf_sessions", ts) if nfi == "smf-east-02" else 0
            if s > 0:
                cpu += 30 * s
                error_rate += 4.5 * s
                status = "degraded" if s > 0.3 else "warning"

            s = im.sev("pcf_eu_minor", ts) if nfi == "pcf-eu-01" else 0
            if s > 0:
                cpu += 15 * s
                error_rate += 1.0 * s
                status = "warning" if s > 0.3 else status

            events.append({
                "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "nf_type": nft,
                "nf_instance": nfi,
                "region": nf["region"],
                "site": nf["site"],
                "nf_cpu_pct": round(clamp(cpu, 2, 99), 1),
                "nf_memory_pct": round(clamp(mem, 15, 95), 1),
                "nf_status": status,
                "active_connections": max(10, conn),
                "request_rate_per_sec": max(0, rps),
                "error_rate_pct": round(clamp(error_rate, 0, 100), 3),
            })
    return events


def generate_service_kpi(timestamps, im):
    events = []
    for ts in timestamps:
        load = diurnal_factor(ts)
        for region in REGIONS:
            scale = REGION_SCALE[region]
            for s in SLICES:
                reg_rate = jitter(99.85, 0.002)
                pdu_rate = jitter(99.7, 0.002)
                drop_rate = jitter(0.08, 0.15)
                cp_latency = jitter(15.0, 0.08)
                up_throughput = jitter(SLICE_BASE_THROUGHPUT[s] * load * scale, 0.06)
                subs = int(jitter(SLICE_BASE_SUBS[s] * load * scale, 0.05))
                pkt_drop = jitter(0.05, 0.2)
                sig_fail = max(0, int(random.gauss(3, 2)))

                if im.region_affected("amf_latency", region, ts):
                    sev = im.sev("amf_latency", ts)
                    reg_rate -= 8.5 * sev
                    cp_latency += 165 * sev
                    sig_fail += int(45 * sev)

                if im.region_affected("smf_sessions", region, ts):
                    sev = im.sev("smf_sessions", ts)
                    pdu_rate -= 11.5 * sev
                    drop_rate += 4.0 * sev

                if im.region_affected("upf_drops", region, ts) and s == "URLLC":
                    sev = im.sev("upf_drops", ts)
                    pkt_drop += 8.4 * sev
                    up_throughput *= (1 - 0.6 * sev)

                if im.region_affected("pcf_eu_minor", region, ts):
                    sev = im.sev("pcf_eu_minor", ts)
                    cp_latency += 25 * sev
                    sig_fail += int(8 * sev)

                events.append({
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "region": region,
                    "slice": s,
                    "registration_success_rate": round(clamp(reg_rate, 80, 100), 2),
                    "pdu_session_success_rate": round(clamp(pdu_rate, 75, 100), 2),
                    "session_drop_rate": round(clamp(drop_rate, 0, 25), 3),
                    "control_plane_latency_ms": round(clamp(cp_latency, 3, 500), 1),
                    "user_plane_throughput_gbps": round(clamp(up_throughput, 0.01, 500), 2),
                    "active_subscribers": max(100, subs),
                    "packet_drop_pct": round(clamp(pkt_drop, 0, 50), 3),
                    "signaling_failure_count": sig_fail,
                })
    return events


def generate_subscriber_experience(timestamps, im):
    events = []
    for ts in timestamps:
        load = diurnal_factor(ts)
        for region in REGIONS:
            scale = REGION_SCALE[region]
            for s in SLICES:
                for seg in SEGMENTS:
                    seg_scale = SEGMENT_SCALE[seg]
                    subs = int(jitter(SLICE_BASE_SUBS[s] * load * scale * seg_scale, 0.05))
                    throughput = jitter(SLICE_BASE_THROUGHPUT[s] * scale, 0.06)
                    latency = jitter(SLICE_BASE_LATENCY[s], 0.08)
                    setup = jitter(SLICE_BASE_SETUP_TIME[s], 0.06)
                    quality = jitter(95.0, 0.01)
                    complaints = max(0, int(random.gauss(1, 1)))

                    if im.region_affected("amf_latency", region, ts):
                        sev = im.sev("amf_latency", ts)
                        latency += 40 * sev
                        setup += 200 * sev
                        quality -= 12 * sev
                        complaints += int(15 * sev)

                    if im.region_affected("smf_sessions", region, ts):
                        sev = im.sev("smf_sessions", ts)
                        setup += 300 * sev
                        quality -= 8 * sev
                        complaints += int(10 * sev)

                    if im.region_affected("upf_drops", region, ts) and s == "URLLC":
                        sev = im.sev("upf_drops", ts)
                        throughput *= (1 - 0.5 * sev)
                        quality -= 15 * sev
                        complaints += int(20 * sev)

                    if im.region_affected("pcf_eu_minor", region, ts):
                        sev = im.sev("pcf_eu_minor", ts)
                        latency += 8 * sev
                        quality -= 3 * sev

                    events.append({
                        "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "region": region,
                        "slice": s,
                        "subscriber_segment": seg,
                        "active_subscribers": max(10, subs),
                        "avg_throughput_mbps": round(clamp(throughput, 0.01, 1000), 1),
                        "avg_latency_ms": round(clamp(latency, 1, 500), 1),
                        "session_setup_time_ms": round(clamp(setup, 5, 2000), 0),
                        "service_quality_score": round(clamp(quality, 30, 100), 1),
                        "complaint_count": complaints,
                    })
    return events


def generate_alerts(im):
    alerts = []
    alert_counter = [0]

    def mk_id():
        alert_counter[0] += 1
        return "ALT-{:04d}".format(alert_counter[0])

    inc = im.incidents

    major_day = inc["amf_latency"]["start"].strftime("%Y%m%d")
    minor_day = inc["pcf_eu_minor"]["start"].strftime("%Y%m%d")

    major_corr = "INC-{}-001".format(major_day)
    minor_corr = "INC-{}-002".format(minor_day)

    major_alerts = [
        {
            "timestamp": inc["amf_latency"]["start"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "warning",
            "nf_type": "AMF", "nf_instance": "amf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "eMBB",
            "alert_name": "AMF Registration Latency Elevated",
            "description": "Registration latency for amf-east-01 rising above normal baseline",
            "kpi_name": "control_plane_latency_ms", "kpi_value": 45.2, "threshold": 30,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": (inc["amf_latency"]["start"] + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "high",
            "nf_type": "AMF", "nf_instance": "amf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "eMBB",
            "alert_name": "AMF Registration Latency Threshold Exceeded",
            "description": "AMF registration latency exceeded 100ms threshold in US-East",
            "kpi_name": "control_plane_latency_ms", "kpi_value": 112.5, "threshold": 100,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": inc["smf_sessions"]["start"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "warning",
            "nf_type": "SMF", "nf_instance": "smf-east-02",
            "region": "US-East", "site": "east-dc2", "slice": "eMBB",
            "alert_name": "Session Establishment Success Rate Declining",
            "description": "PDU session success rate dropping on smf-east-02",
            "kpi_name": "pdu_session_success_rate", "kpi_value": 96.8, "threshold": 98,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": inc["amf_latency"]["peak"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "critical",
            "nf_type": "AMF", "nf_instance": "amf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "eMBB",
            "alert_name": "Critical: AMF Registration Failure Rate",
            "description": "Registration success rate dropped below 92% on amf-east-01, subscriber impact confirmed",
            "kpi_name": "registration_success_rate", "kpi_value": 91.3, "threshold": 95,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": inc["upf_drops"]["start"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "warning",
            "nf_type": "UPF", "nf_instance": "upf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "URLLC",
            "alert_name": "UPF Packet Drop Rate Elevated",
            "description": "Packet drops on upf-east-01 exceeding baseline for URLLC slice",
            "kpi_name": "packet_drop_pct", "kpi_value": 1.2, "threshold": 0.5,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": (inc["upf_drops"]["start"] + timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "high",
            "nf_type": "SMF", "nf_instance": "smf-east-02",
            "region": "US-East", "site": "east-dc2", "slice": "eMBB",
            "alert_name": "Session Establishment Degradation",
            "description": "PDU session success rate below 90% on smf-east-02",
            "kpi_name": "pdu_session_success_rate", "kpi_value": 88.2, "threshold": 95,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": (inc["upf_drops"]["start"] + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "critical",
            "nf_type": "UPF", "nf_instance": "upf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "URLLC",
            "alert_name": "Critical: URLLC Packet Loss Exceeds SLA",
            "description": "URLLC slice packet drop rate at 5.3%, breaching SLA threshold. Premium subscribers impacted.",
            "kpi_name": "packet_drop_pct", "kpi_value": 5.3, "threshold": 1.0,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": (inc["upf_drops"]["peak"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "critical",
            "nf_type": "UPF", "nf_instance": "upf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "URLLC",
            "alert_name": "Critical: Service Impact - US-East URLLC",
            "description": "Widespread service impact on URLLC slice in US-East. Throughput degraded 60%, packet loss 8.5%. Escalate immediately.",
            "kpi_name": "packet_drop_pct", "kpi_value": 8.5, "threshold": 1.0,
            "correlation_id": major_corr, "status": "open",
        },
        {
            "timestamp": inc["amf_latency"]["end"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "info",
            "nf_type": "AMF", "nf_instance": "amf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "eMBB",
            "alert_name": "AMF Latency Recovering",
            "description": "Registration latency on amf-east-01 returning to normal levels",
            "kpi_name": "control_plane_latency_ms", "kpi_value": 28.0, "threshold": 30,
            "correlation_id": major_corr, "status": "resolved",
        },
        {
            "timestamp": inc["smf_sessions"]["end"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "info",
            "nf_type": "SMF", "nf_instance": "smf-east-02",
            "region": "US-East", "site": "east-dc2", "slice": "eMBB",
            "alert_name": "Session Establishment Recovered",
            "description": "PDU session success rate on smf-east-02 returned above 99%",
            "kpi_name": "pdu_session_success_rate", "kpi_value": 99.5, "threshold": 98,
            "correlation_id": major_corr, "status": "resolved",
        },
        {
            "timestamp": inc["upf_drops"]["end"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "info",
            "nf_type": "UPF", "nf_instance": "upf-east-01",
            "region": "US-East", "site": "east-dc1", "slice": "URLLC",
            "alert_name": "UPF Packet Drops Resolved",
            "description": "Packet drop rate on upf-east-01 returned to normal. URLLC SLA restored.",
            "kpi_name": "packet_drop_pct", "kpi_value": 0.08, "threshold": 0.5,
            "correlation_id": major_corr, "status": "resolved",
        },
    ]

    minor_alerts = [
        {
            "timestamp": inc["pcf_eu_minor"]["start"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "warning",
            "nf_type": "PCF", "nf_instance": "pcf-eu-01",
            "region": "EU-Central", "site": "eu-dc1", "slice": "eMBB",
            "alert_name": "PCF Policy Latency Elevated",
            "description": "Policy decision latency on pcf-eu-01 above baseline",
            "kpi_name": "control_plane_latency_ms", "kpi_value": 35.0, "threshold": 30,
            "correlation_id": minor_corr, "status": "open",
        },
        {
            "timestamp": inc["pcf_eu_minor"]["peak"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "high",
            "nf_type": "PCF", "nf_instance": "pcf-eu-01",
            "region": "EU-Central", "site": "eu-dc1", "slice": "eMBB",
            "alert_name": "PCF Policy Latency Threshold Exceeded",
            "description": "Policy decision latency on pcf-eu-01 at 42ms, affecting session setup times",
            "kpi_name": "control_plane_latency_ms", "kpi_value": 42.0, "threshold": 30,
            "correlation_id": minor_corr, "status": "open",
        },
        {
            "timestamp": inc["pcf_eu_minor"]["end"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alert_id": mk_id(), "severity": "info",
            "nf_type": "PCF", "nf_instance": "pcf-eu-01",
            "region": "EU-Central", "site": "eu-dc1", "slice": "eMBB",
            "alert_name": "PCF Latency Resolved",
            "description": "Policy decision latency on pcf-eu-01 returned to normal. Auto-resolved.",
            "kpi_name": "control_plane_latency_ms", "kpi_value": 16.0, "threshold": 30,
            "correlation_id": minor_corr, "status": "resolved",
        },
    ]

    baseline_alerts = []
    end_time_dt = inc["amf_latency"]["start"]
    start_time_dt = end_time_dt - timedelta(days=DAYS)
    current = start_time_dt + timedelta(hours=random.randint(2, 8))
    while current < end_time_dt - timedelta(days=1):
        if random.random() < 0.3:
            nf = random.choice(NF_INSTANCES)
            region = nf["region"]
            site = nf["site"]
            baseline_alerts.append({
                "timestamp": current.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "alert_id": mk_id(), "severity": random.choice(["info", "warning"]),
                "nf_type": nf["nf_type"], "nf_instance": nf["nf_instance"],
                "region": region, "site": site,
                "slice": random.choice(SLICES),
                "alert_name": random.choice([
                    "Routine health check variance",
                    "Brief latency spike detected",
                    "Connection count above average",
                    "Memory utilization elevated",
                    "Minor signaling anomaly",
                ]),
                "description": "Transient condition detected and auto-resolved within monitoring window",
                "kpi_name": random.choice(["nf_cpu_pct", "control_plane_latency_ms", "nf_memory_pct"]),
                "kpi_value": round(random.uniform(30, 60), 1),
                "threshold": round(random.uniform(50, 80), 0),
                "correlation_id": "INC-{}-BL{:03d}".format(current.strftime("%Y%m%d"), alert_counter[0]),
                "status": "resolved",
            })
        current += timedelta(hours=random.randint(4, 12))

    alerts = baseline_alerts + minor_alerts + major_alerts
    alerts.sort(key=lambda a: a["timestamp"])
    return alerts


def write_jsonl(filepath, events):
    with open(filepath, "w") as f:
        for evt in events:
            f.write(json.dumps(evt, separators=(",", ":")) + "\n")
    print("  Wrote {} events to {}".format(len(events), filepath))


def main():
    parser = argparse.ArgumentParser(description="Generate 5G SA Core sample data")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "..", "samples"),
                        help="Output directory for sample files")
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    now = datetime.now(timezone.utc)
    end_time = now.replace(minute=(now.minute // INTERVAL_MINUTES) * INTERVAL_MINUTES,
                           second=0, microsecond=0)

    print("Generating 5G SA Core sample data")
    print("  End time: {}".format(end_time.strftime("%Y-%m-%dT%H:%M:%SZ")))
    print("  Span: {} days".format(DAYS))
    print("  Interval: {} minutes".format(INTERVAL_MINUTES))
    print("  Output: {}".format(output_dir))
    print()

    timestamps = generate_timestamps(end_time)
    im = IncidentManager(end_time)

    print("Generating NF metrics...")
    nf_events = generate_nf_metrics(timestamps, im)
    write_jsonl(os.path.join(output_dir, "5g_nf_metrics.json"), nf_events)

    print("Generating service KPIs...")
    kpi_events = generate_service_kpi(timestamps, im)
    write_jsonl(os.path.join(output_dir, "5g_service_kpi.json"), kpi_events)

    print("Generating subscriber experience...")
    sub_events = generate_subscriber_experience(timestamps, im)
    write_jsonl(os.path.join(output_dir, "5g_subscriber_experience.json"), sub_events)

    print("Generating alerts...")
    alert_events = generate_alerts(im)
    write_jsonl(os.path.join(output_dir, "5g_core_alerts.json"), alert_events)

    total = len(nf_events) + len(kpi_events) + len(sub_events) + len(alert_events)
    print("\nDone. Total events: {}".format(total))


if __name__ == "__main__":
    main()
