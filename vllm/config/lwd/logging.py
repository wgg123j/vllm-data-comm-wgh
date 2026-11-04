# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
"""Log the resolved LWD metadata without reading files or starting execution."""

import argparse
import json
import logging
from dataclasses import asdict

from .entry import LwdConfig


def log_lwd_config(logger: logging.Logger, config: LwdConfig) -> None:
    """Emit one startup record with all fields, defaults and selected connections."""
    if not logger.isEnabledFor(logging.INFO):
        return
    snapshot = {
        "metadata_only": True,
        "lwd_config": asdict(config),
        "selected_instance": asdict(config.instance),
        "connections": [
            {**asdict(link), "cloud_leader_rank": link.cloud_leader_rank}
            for link in config.connections
        ],
        "cloud_cards": {
            str(cloud.id): sum(len(dp.ranks) for dp in cloud.dp)
            for cloud in config.topology.clouds
        },
    }
    # Serialize the parsed snapshot only; tenant_key_file remains a path, not content.
    logger.info("[config] resolved=%s", json.dumps(snapshot, ensure_ascii=False))


def log_lwd_frontend_config(logger: logging.Logger, args: argparse.Namespace) -> None:
    """Log the effective frontend count before serve normalizes dispatch arguments."""
    additional = getattr(args, "additional_config", None)
    if not isinstance(additional, dict) or "lwd_config" not in additional:
        return
    entry = additional["lwd_config"]
    if not isinstance(entry, dict) or not logger.isEnabledFor(logging.INFO):
        return
    snapshot = {
        "role": entry.get("role"),
        "instance_id": entry.get("instance_id"),
        "api_server_count": args.api_server_count,
        "api_server_rpc_port": getattr(args, "api_server_rpc_port", None),
        "api_server_attach": getattr(args, "api_server_attach", None),
    }
    logger.info("[config] frontend=%s", json.dumps(snapshot, ensure_ascii=False))
