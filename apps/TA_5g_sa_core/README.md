# TA_5g_sa_core - 5G SA Core Technology Add-on

Technology Add-on for ingesting and normalizing 5G Standalone Core telemetry data in Splunk.

## Sourcetypes

| Sourcetype | Description |
|---|---|
| `5g:nf:metrics` | Network function health metrics (CPU, memory, status, connections) per NF instance |
| `5g:service:kpi` | Service-level KPIs (registration rate, session rate, latency, throughput) per region/slice |
| `5g:core:alerts` | Alert and incident events with severity, correlation IDs |
| `5g:subscriber:experience` | Subscriber experience metrics per region, slice, and segment |

## Setup

1. Install this add-on to `$SPLUNK_HOME/etc/apps/TA_5g_sa_core`
2. Generate sample data (or use the pre-generated files in `samples/`):
   ```bash
   cd bin
   python3 generate_sample_data.py
   ```
3. Restart Splunk. The `inputs.conf` will automatically monitor the sample files.
4. Data is indexed to the `fiveg_sa_core` index.

## Regenerating Sample Data

The generator script creates 7 days of data ending at the current time.
To refresh the data (e.g., for a new demo date):

```bash
cd $SPLUNK_HOME/etc/apps/TA_5g_sa_core/bin
python3 generate_sample_data.py
```

Then clean and re-index:

```bash
$SPLUNK_HOME/bin/splunk stop
$SPLUNK_HOME/bin/splunk clean eventdata -index fiveg_sa_core -f
$SPLUNK_HOME/bin/splunk start
```

## Index

- `fiveg_sa_core` - All 5G SA Core telemetry data

## Lookup

- `nf_instance_info` - Maps NF instance IDs to metadata (role, vendor, description)

## Data Format

All data is JSON-line format with an ISO 8601 `timestamp` field.
