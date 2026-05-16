"""One-shot bulk export of parsed vmstat data to Elasticsearch.

Requires: pip install elasticsearch
(or: pip install vmstat-visualizer[elasticsearch])

Uses ECS-compatible field names so data works with standard Kibana
dashboards and can be correlated with other observability data.
"""

import json
import sys


ECS_FIELD_MAP = {
    'time': '@timestamp',
    'run_queue': 'system.load.1',
    'blocked_processes': 'system.process.blocked',
    'swapped_memory_kb': 'system.memory.swap.used.bytes',
    'free_memory_kb': 'system.memory.free.bytes',
    'inactive_memory_kb': 'system.memory.inactive.bytes',
    'active_memory_kb': 'system.memory.active.bytes',
    'swap_in_kb': 'system.memory.swap.in.bytes',
    'swap_out_kb': 'system.memory.swap.out.bytes',
    'blocks_in': 'system.diskio.read.bytes',
    'blocks_out': 'system.diskio.write.bytes',
    'interrupts': 'system.cpu.interrupts',
    'context_switches': 'system.cpu.context_switches',
    'user_cpu_percent': 'system.cpu.user.pct',
    'system_cpu_percent': 'system.cpu.system.pct',
    'idle_cpu_percent': 'system.cpu.idle.pct',
    'wait_cpu_percent': 'system.cpu.iowait.pct',
    'steal_cpu_percent': 'system.cpu.steal.pct',
    'guest_cpu_percent': 'system.cpu.guest.pct',
}

KB_FIELDS = {
    'swapped_memory_kb', 'free_memory_kb', 'inactive_memory_kb',
    'active_memory_kb', 'swap_in_kb', 'swap_out_kb',
    'blocks_in', 'blocks_out',
}

PCT_FIELDS = {
    'user_cpu_percent', 'system_cpu_percent', 'idle_cpu_percent',
    'wait_cpu_percent', 'steal_cpu_percent', 'guest_cpu_percent',
}


def _to_ecs_doc(ts_entry, source_file=None):
    """Convert a Timeseries entry to an ECS-compatible dict."""
    doc = {}
    for attr, ecs_field in ECS_FIELD_MAP.items():
        val = getattr(ts_entry, attr, None)
        if val is None:
            continue

        if attr == 'time':
            doc[ecs_field] = val.replace(' ', 'T')
        elif attr in KB_FIELDS:
            doc[ecs_field] = int(val) * 1024
        elif attr in PCT_FIELDS:
            doc[ecs_field] = int(val) / 100.0
        else:
            doc[ecs_field] = int(val)

    doc['event.module'] = 'vmstat'
    doc['event.dataset'] = 'system.vmstat'
    if source_file:
        doc['file.path'] = source_file

    return doc


def build_bulk_body(timeseries, index, source_file=None):
    """Build an Elasticsearch bulk request body (NDJSON)."""
    lines = []
    for entry in timeseries:
        action = json.dumps({"index": {"_index": index}})
        doc = json.dumps(_to_ecs_doc(entry, source_file=source_file))
        lines.append(action)
        lines.append(doc)
    return "\n".join(lines) + "\n"


def export_to_elasticsearch(timeseries, es_url, api_key=None,
                             cloud_id=None, index='vmstat',
                             source_file=None, verify_certs=True):
    """Bulk-index vmstat data into Elasticsearch.

    Args:
        timeseries: list of Timeseries entries
        es_url: Elasticsearch URL (ignored if cloud_id is set)
        api_key: API key string
        cloud_id: Elastic Cloud ID
        index: target index name
        source_file: original vmstat log filename
        verify_certs: whether to verify TLS certificates

    Returns:
        dict with 'indexed' count and 'errors' list
    """
    try:
        from elasticsearch import Elasticsearch, helpers
    except ImportError:
        print(
            "ERROR: elasticsearch-py is required. "
            "Install with: pip install elasticsearch",
            file=sys.stderr,
        )
        raise SystemExit(1)

    kwargs = {}
    if cloud_id:
        kwargs['cloud_id'] = cloud_id
    else:
        kwargs['hosts'] = [es_url]

    if api_key:
        kwargs['api_key'] = api_key

    kwargs['verify_certs'] = verify_certs

    es = Elasticsearch(**kwargs)

    actions = []
    for entry in timeseries:
        doc = _to_ecs_doc(entry, source_file=source_file)
        actions.append({
            "_index": index,
            "_source": doc,
        })

    success, errors = helpers.bulk(es, actions, raise_on_error=False)

    return {
        'indexed': success,
        'errors': errors if errors else [],
    }
