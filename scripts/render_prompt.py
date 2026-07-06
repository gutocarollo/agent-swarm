#!/usr/bin/env python3
"""Render a LearnHouse Delivery Council prompt with validated ARGS."""

from __future__ import annotations

import argparse
import sys


START_AT = ("AUTO", "EXECUTION", "PLANNING", "PLAN_REVIEW")


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-at", default="AUTO", choices=START_AT)
    parser.add_argument("--task", required=True)
    parser.add_argument("--plan-source")
    parser.add_argument("--auto-decide", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--plan-review-max", type=int, default=2)
    parser.add_argument("--execution-review-max", type=int, default=3)
    parser.add_argument("--auto-execute-after-plan", action=argparse.BooleanOptionalAction, default=None)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.plan_review_max > 2:
        raise SystemExit("PLAN_REVIEW_MAX cannot exceed 2")
    if args.execution_review_max > 3:
        raise SystemExit("EXECUTION_REVIEW_MAX cannot exceed 3")
    if args.start_at == "PLAN_REVIEW" and not args.plan_source:
        raise SystemExit("--plan-source is required when --start-at PLAN_REVIEW")

    auto_execute = args.auto_execute_after_plan
    if auto_execute is None:
        auto_execute = args.start_at == "PLAN_REVIEW"

    lines = [
        "Use $learnhouse-delivery-council.",
        "",
        "ARGS:",
        f"START_AT={args.start_at}",
        f"AUTO_DECIDE={bool_text(args.auto_decide)}",
        f"PLAN_REVIEW_MAX={args.plan_review_max}",
        f"EXECUTION_REVIEW_MAX={args.execution_review_max}",
        f"AUTO_EXECUTE_AFTER_PLAN={bool_text(auto_execute)}",
    ]
    if args.plan_source:
        lines.append(f"PLAN_SOURCE={args.plan_source}")
    lines.extend(["", "TASK:", args.task])
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
