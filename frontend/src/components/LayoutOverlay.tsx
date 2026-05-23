"use client";

import { useCallback, useState } from "react";
import type { LayoutRegion } from "@/lib/types";

const LABEL_COLORS: Record<string, { border: string; bg: string; text: string }> = {
  header: { border: "border-blue-300", bg: "bg-blue-50/70", text: "text-blue-700" },
  seller_info: { border: "border-teal-300", bg: "bg-teal-50/70", text: "text-teal-700" },
  buyer_info: { border: "border-violet-300", bg: "bg-violet-50/70", text: "text-violet-700" },
  table: { border: "border-amber-300", bg: "bg-amber-50/70", text: "text-amber-700" },
  total_section: { border: "border-rose-300", bg: "bg-rose-50/70", text: "text-rose-700" },
  footer: { border: "border-gray-300", bg: "bg-gray-50/70", text: "text-gray-700" },
  stamp: { border: "border-pink-300", bg: "bg-pink-50/70", text: "text-pink-700" },
  signature: { border: "border-indigo-300", bg: "bg-indigo-50/70", text: "text-indigo-700" },
  unknown: { border: "border-slate-300", bg: "bg-slate-50/70", text: "text-slate-700" },
};

const DEFAULT_COLOR = LABEL_COLORS.unknown;

function formatLabel(label: string): string {
  return label.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function LayoutOverlay({
  regions,
  imageWidth,
  imageHeight,
  imageUrl,
  alt = "Uploaded document",
}: {
  regions: LayoutRegion[];
  imageWidth?: number | null;
  imageHeight?: number | null;
  imageUrl: string;
  alt?: string;
}) {
  const [naturalSize, setNaturalSize] = useState<{ w: number; h: number } | null>(null);

  const handleLoad = useCallback((e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setNaturalSize({ w: img.naturalWidth, h: img.naturalHeight });
  }, []);

  const baseW = imageWidth ?? naturalSize?.w;
  const baseH = imageHeight ?? naturalSize?.h;
  const hasDimensions = baseW != null && baseH != null;

  return (
    <div className="relative inline-block">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={imageUrl}
        alt={alt}
        className="max-h-125 rounded-lg object-contain"
        onLoad={handleLoad}
      />
      {hasDimensions &&
        regions.map((region) => {
          const [xMin, yMin, xMax, yMax] = region.bbox;
          const left = (xMin / baseW!) * 100;
          const top = (yMin / baseH!) * 100;
          const width = ((xMax - xMin) / baseW!) * 100;
          const height = ((yMax - yMin) / baseH!) * 100;
          const colors = LABEL_COLORS[region.label] ?? DEFAULT_COLOR;

          return (
            <div
              key={region.id}
              className={`pointer-events-none absolute ${colors.border} ${colors.bg} ${colors.text}`}
              style={{
                left: `${left}%`,
                top: `${top}%`,
                width: `${width}%`,
                height: `${height}%`,
                borderWidth: 1.5,
              }}
            >
              <span
                className={`absolute -top-4 left-0.5 truncate rounded px-1 text-[10px] font-semibold leading-tight ${colors.bg} ${colors.text}`}
              >
                {formatLabel(region.label)}
              </span>
            </div>
          );
        })}
    </div>
  );
}