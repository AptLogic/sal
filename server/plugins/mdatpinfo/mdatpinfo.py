import json

import sal.plugin
from server.models import Fact


class MDATPInfo(sal.plugin.DetailPlugin):

    description = "Microsoft Defender telemetry"

    supported_os_families = [sal.plugin.OSFamilies.darwin, sal.plugin.OSFamilies.windows]

    def _latest_value(self, machine, name):
        """Return the latest fact_data for the given fact name from salmdatp management source."""
        try:
            fact = (
                Fact.objects
                .filter(machine=machine,
                        management_source__name="salmdatp",
                        fact_name=name)
                .order_by("-id")
                .first()
            )
            if fact and fact.fact_data is not None:
                return fact.fact_data
        except Exception:
            pass
        return None

    def _has_any_data(self):
        """Return True if any machine has reported facts from the salmdatp management source."""
        try:
            return Fact.objects.filter(management_source__name="salmdatp").exists()
        except Exception:
            return False

    def get_context(self, machine, **kwargs):
        # If no device in the database has reported MDATP facts, don't render this plugin
        if not self._has_any_data():
            return None

        context = self.super_get_context(machine, **kwargs)

        # Basic health and version info
        context["healthy"] = self._latest_value(machine, "mdatp_health_healthy")
        context["app_version"] = self._latest_value(machine, "mdatp_health_app_version")
        context["engine_version"] = self._latest_value(machine, "mdatp_health_engine_version")
        context["definitions_version"] = self._latest_value(machine, "mdatp_health_definitions_version")
        context["definitions_status"] = self._latest_value(machine, "mdatp_health_definitions_status")
        context["definitions_updated"] = self._latest_value(machine, "mdatp_health_definitions_updated")
        context["managed_by"] = self._latest_value(machine, "mdatp_health_managed_by")
        context["real_time_protection_enabled"] = self._latest_value(machine, "mdatp_health_real_time_protection_enabled")

        # Connectivity summary (individual fields and JSON)
        connectivity_ok = self._latest_value(machine, "mdatp_connectivity_summary_ok")
        connectivity_failed = self._latest_value(machine, "mdatp_connectivity_summary_failed")
        connectivity_total = self._latest_value(machine, "mdatp_connectivity_summary_total")
        context["connectivity_ok"] = connectivity_ok
        context["connectivity_failed"] = connectivity_failed
        context["connectivity_total"] = connectivity_total

        connectivity_json = self._latest_value(machine, "mdatp_connectivity_json")
        context["connectivity_raw"] = self._latest_value(machine, "mdatp_connectivity_raw") or ""

        # Parse endpoints and categorize by status
        endpoints_ok = []
        endpoints_failed = []
        connectivity_json = self._latest_value(machine, "mdatp_connectivity_json")
        
        if connectivity_json:
            try:
                parsed = json.loads(connectivity_json)
                # parsed may have keys: summary, endpoints, raw
                all_endpoints = parsed.get("endpoints", [])
            except Exception:
                # Some submissions store JSON-like string with single quotes; try to replace
                try:
                    parsed = json.loads(connectivity_json.replace("'", '"'))
                    all_endpoints = parsed.get("endpoints", [])
                except Exception:
                    all_endpoints = []
            
            # Categorize endpoints by status
            for ep in all_endpoints:
                ep_status = str(ep.get("status", "unknown")).lower()
                if ep_status in ("ok", "success", "connected", "true", "1"):
                    endpoints_ok.append(ep)
                else:
                    endpoints_failed.append(ep)
        
        context["endpoints_ok"] = endpoints_ok
        context["endpoints_failed"] = endpoints_failed

        # Health JSON for additional details
        health_json = self._latest_value(machine, "mdatp_health_json")
        health = {}
        if health_json:
            try:
                health = json.loads(health_json)
            except Exception:
                try:
                    health = json.loads(health_json.replace("'", '"'))
                except Exception:
                    health = {}
        context["health"] = health

        # Friendly fallback values for template
        context.setdefault("healthy", context.get("healthy", "Unknown"))
        context.setdefault("app_version", context.get("app_version", "Unknown"))
        context.setdefault("engine_version", context.get("engine_version", "Unknown"))
        context.setdefault("definitions_version", context.get("definitions_version", "Unknown"))
        context.setdefault("managed_by", context.get("managed_by", "Unknown"))

        # Indicate to the template that MDATP data exists somewhere in the DB
        context["mdatp_available"] = True

        return context

    def filter(self, machines, data):
        # Allow filtering by managed_by or health status if used in a link
        machines = machines.filter(machine_group__business_unit__name__icontains=data)
        return machines, 'Machines matching "' + data + '"'
