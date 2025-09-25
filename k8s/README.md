# PagerDuty Integration with Alertmanager

This document explains how PagerDuty was integrated with Alertmanager in
the **Prometheus monitoring stack**.

------------------------------------------------------------------------

## 🔧 Steps to Configure PagerDuty with Alertmanager

### 1. Create the Alertmanager Configuration (`alertmanager.yaml`)

Here is the configuration used to send alerts to PagerDuty:

``` yaml
global:
  resolve_timeout: 5m

inhibit_rules:
- equal:
  - namespace
  - alertname
  source_matchers:
  - severity = critical
  target_matchers:
  - severity =~ warning|info
- equal:
  - namespace
  - alertname
  source_matchers:
  - severity = warning
  target_matchers:
  - severity = info
- equal:
  - namespace
  source_matchers:
  - alertname = InfoInhibitor
  target_matchers:
  - severity = info
- target_matchers:
  - alertname = InfoInhibitor

receivers:
- name: "null"

- name: "pagerduty"
  pagerduty_configs:
  - service_key: "<PAGERDUTY_ROUTING_KEY>"   # Replace with your actual routing key
    severity: '{{ .CommonLabels.severity | default "error" }}'
    send_resolved: true

route:
  group_by: ["namespace"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 12h
  receiver: "pagerduty"

  routes:
  - matchers:
    - alertname = "Watchdog"
    receiver: "null"

templates:
- /etc/alertmanager/config/*.tmpl
```

------------------------------------------------------------------------

### 2. Create the Kubernetes Secret

To apply this configuration to your cluster, create a **Kubernetes
Secret** in the `monitoring` namespace:

``` bash
kubectl -n monitoring create secret generic alertmanager-prometheus-kube-prometheus-alertmanager   --from-file=alertmanager.yaml=alertmanager.yaml --dry-run=client -o yaml | kubectl apply -f -
```

------------------------------------------------------------------------

### 3. Restart Alertmanager Pod

After applying the new secret, restart Alertmanager to reload the
configuration:

``` bash
kubectl -n monitoring delete pod -l app.kubernetes.io/name=alertmanager
```

This will force Kubernetes to spin up a new pod with the updated
configuration.

------------------------------------------------------------------------

### 4. Test PagerDuty Integration

Send a test alert to Alertmanager and verify it reaches PagerDuty:

``` bash
kubectl -n monitoring exec -it <alertmanager-pod-name> --   curl -XPOST -H 'Content-Type: application/json'   -d '[{"labels": {"alertname": "PagerDutyTest", "severity": "critical", "namespace": "monitoring"}}]'   http://localhost:9093/api/v2/alerts
```

Check PagerDuty to confirm that the incident was created.

------------------------------------------------------------------------

## ✅ Verification

-   Run
    `kubectl -n monitoring port-forward svc/alertmanager-operated 9093`\
-   Visit <http://localhost:9093>\
-   Confirm that PagerDuty is listed as a **receiver** under the
    `/api/v2/alerts` endpoint.

------------------------------------------------------------------------

## 📌 Notes

-   Always use **Routing Key** from PagerDuty **Events API v2** service
    integration.\
-   Inhibitions are configured so that **critical alerts silence
    warning/info alerts** of the same type.\
-   The `Watchdog` alert is muted (sent to `null` receiver).

------------------------------------------------------------------------

## 📝 Authors

-   Setup by: `<Your Name>`{=html}
-   Date: September 2025
