"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { LayoutRegion } from "@/lib/types";

type RgbaColor = {
  fill: string;
  border: string;
  text: string;
  chip: string;
};

const LABEL_COLORS: Record<string, RgbaColor> = {
  header: {
    fill: "rgba(249,115,22,0.18)",
    border: "rgba(249,115,22,0.7)",
    text: "#c2410c",
    chip: "rgba(249,115,22,0.15)",
  },
  form_field: {
    fill: "rgba(34,197,94,0.18)",
    border: "rgba(34,197,94,0.7)",
    text: "#15803d",
    chip: "rgba(34,197,94,0.15)",
  },
  footer: {
    fill: "rgba(107,114,128,0.18)",
    border: "rgba(107,114,128,0.7)",
    text: "#374151",
    chip: "rgba(107,114,128,0.15)",
  },
  table: {
    fill: "rgba(59,130,246,0.18)",
    border: "rgba(59,130,246,0.7)",
    text: "#1d4ed8",
    chip: "rgba(59,130,246,0.15)",
  },
  total_section: {
    fill: "rgba(236,72,153,0.18)",
    border: "rgba(236,72,153,0.7)",
    text: "#be185d",
    chip: "rgba(236,72,153,0.15)",
  },
  seller_info: {
    fill: "rgba(139,92,246,0.18)",
    border: "rgba(139,92,246,0.7)",
    text: "#6d28d9",
    chip: "rgba(139,92,246,0.15)",
  },
  buyer_info: {
    fill: "rgba(6,182,212,0.18)",
    border: "rgba(6,182,212,0.7)",
    text: "#0e7490",
    chip: "rgba(6,182,212,0.15)",
  },
  stamp: {
    fill: "rgba(244,63,94,0.18)",
    border: "rgba(244,63,94,0.7)",
    text: "#be123c",
    chip: "rgba(244,63,94,0.15)",
  },
  signature: {
    fill: "rgba(99,102,241,0.18)",
    border: "rgba(99,102,241,0.7)",
    text: "#4338ca",
    chip: "rgba(99,102,241,0.15)",
  },
  unknown: {
    fill: "rgba(100,116,139,0.18)",
    border: "rgba(100,116,139,0.7)",
    text: "#334155",
    chip: "rgba(100,116,139,0.15)",
  },
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
  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [renderedSize, setRenderedSize] = useState<{
    w: number;
    h: number;
  } | null>(null);

  const measure = useCallback(() => {
    if (imgRef.current) {
      setRenderedSize({ w: imgRef.current.clientWidth, h: imgRef.current.clientHeight });
    }
  }, []);

  useEffect(() => {
    const el = imgRef.current;
    if (!el) return;

    const observer = new ResizeObserver(() => measure());
    observer.observe(el);
    return () => observer.disconnect();
  }, [measure]);

  const baseW = imageWidth ?? null;
  const baseH = imageHeight ?? null;
  const canRender = baseW && baseH && renderedSize;

  return (
    <div ref={containerRef} className="relative inline-block">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        ref={imgRef}
        src={imageUrl}
        alt={alt}
        className="max-h-125 rounded-lg object-contain"
        onLoad={measure}
      />
      {canRender &&
        regions.map((region) => {
          const [xMin, yMin, xMax, yMax] = region.bbox;
          const scaleX = renderedSize.w / baseW!;
          const scaleY = renderedSize.h / baseH!;

          const left = xMin * scaleX;
          const top = yMin * scaleY;
          const width = (xMax - xMin) * scaleX;
          const height = (yMax - yMin) * scaleY;

          const colors = LABEL_COLORS[region.label] ?? DEFAULT_COLOR;

          return (
            <div
              key={region.id}
              style={{
                position: "absolute",
                left: `${left}px`,
                top: `${top}px`,
                width: `${width}px`,
                height: `${height}px`,
                backgroundColor: colors.fill,
                border: `2px solid ${colors.border}`,
                pointerEvents: "none",
                overflow: "hidden",
              }}
            >
              <span
                style={{
                  position: "absolute",
                  top: 2,
                  left: 4,
                  display: "inline-block",
                  padding: "1px 6px",
                  borderRadius: 4,
                  fontSize: 11,
                  fontWeight: 600,
                  lineHeight: "16px",
                  backgroundColor: colors.chip,
                  color: colors.text,
                  whiteSpace: "nowrap",
                }}
              >
                {formatLabel(region.label)}
              </span>
            </div>
          );
        })}
    </div>
  );
}