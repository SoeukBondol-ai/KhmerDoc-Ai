"use client";

import { useState } from "react";
import type { LayoutRegion } from "@/lib/types";

const LABEL_DOT_COLORS: Record<string, string> = {
  header: "#F97316",
  form_field: "#22C55E",
  footer: "#6B7280",
  table: "#3B82F6",
  total_section: "#EC4899",
  seller_info: "#8B5CF6",
  buyer_info: "#06B6D4",
  stamp: "#F43F5E",
  signature: "#6366F1",
  unknown: "#64748B",
};

const DEFAULT_DOT_COLOR = "#64748B";

function confidenceStyle(confidence: number) {
  if (confidence >= 0.8) return "bg-success-bg text-success-text";
  if (confidence >= 0.5) return "bg-warning-bg text-warning-text";
  return "bg-error-bg text-error-text";
}

function formatLabel(label: string): string {
  return label.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function LayoutRegionList({
  regions,
}: {
  regions: LayoutRegion[];
}) {
  const isMock = regions.length > 0 && regions[0].source === "mock";

  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-card">
      <div className="flex items-center gap-2 border-b border-border px-5 py-3">
        <svg
          className="h-4 w-4 text-muted-foreground"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z"
          />
        </svg>
        <span className="text-[13px] font-semibold text-foreground">
          Layout Regions
        </span>
        <span className="ml-auto rounded-md bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
          {regions.length} region{regions.length !== 1 ? "s" : ""}
        </span>
      </div>

      {isMock && (
        <div className="border-b border-border bg-amber-50/60 px-5 py-2.5 text-[12px] leading-snug text-amber-800">
          Demo mode &mdash; layout regions are simulated placeholders. A trained
          YOLO model will replace this later.
        </div>
      )}

      <div className="px-5 py-1">
        {regions.map((region) => (
          <RegionRow key={region.id} region={region} />
        ))}
      </div>
    </div>
  );
}

function RegionRow({ region }: { region: LayoutRegion }) {
  const [expanded, setExpanded] = useState(false);
  const dotColor = LABEL_DOT_COLORS[region.label] ?? DEFAULT_DOT_COLOR;

  return (
    <div className="border-b border-border/50 py-2.5 last:border-b-0">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className="inline-block h-2.5 w-2.5 shrink-0 rounded-full"
            style={{ backgroundColor: dotColor }}
          />
          <span className="text-[13px] font-medium text-foreground">
            {formatLabel(region.label)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`rounded-md px-1.5 py-0.5 text-[11px] font-medium ${confidenceStyle(region.confidence)}`}
          >
            {(region.confidence * 100).toFixed(0)}%
          </span>
          {region.source && (
            <span className="rounded-md bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground">
              {region.source}
            </span>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="rounded-md bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground hover:text-foreground"
          >
            {expanded ? "hide" : "bbox"}
          </button>
        </div>
      </div>
      {expanded && (
        <div className="mt-1 text-[11px] font-mono text-muted-foreground">
          [{region.bbox.map((v) => Math.round(v)).join(", ")}]
        </div>
      )}
    </div>
  );
}