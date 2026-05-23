"use client";

import { useCallback, useState } from "react";
import type { DocumentExtraction } from "@/lib/types";

function confidenceStyle(confidence: number) {
  if (confidence >= 0.8)
    return "bg-success-bg text-success-text";
  if (confidence >= 0.5)
    return "bg-warning-bg text-warning-text";
  return "bg-error-bg text-error-text";
}

function FieldRow({
  label,
  field,
}: {
  label: string;
  field: { value: string | null; confidence: number; source: string };
}) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-border/50 py-3 last:border-b-0">
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span className="text-[12px] font-medium text-muted-foreground">
          {label}
        </span>
        <span className="truncate text-sm text-foreground">
          {field.value ?? "—"}
        </span>
      </div>
      <div className="flex shrink-0 items-center gap-2 pt-1">
        <span
          className={`rounded-md px-1.5 py-0.5 text-[11px] font-medium ${confidenceStyle(field.confidence)}`}
        >
          {(field.confidence * 100).toFixed(0)}%
        </span>
        {field.source && (
          <span className="rounded-md bg-muted px-1.5 py-0.5 text-[11px] text-muted-foreground">
            {field.source}
          </span>
        )}
      </div>
    </div>
  );
}

export default function ExtractionJsonPanel({
  extraction,
}: {
  extraction: DocumentExtraction;
}) {
  const [copied, setCopied] = useState(false);

  const json = JSON.stringify(
    {
      document_id: extraction.document_id,
      extraction: {
        document_id: extraction.document_id,
        document_type: extraction.document_type,
        company_name: extraction.company_name,
        phone: extraction.phone,
        date: extraction.date,
        invoice_number: extraction.invoice_number,
        total_amount: extraction.total_amount,
        currency: extraction.currency,
        raw_text_preview: extraction.raw_text_preview ?? undefined,
      },
    },
    null,
    2,
  );

  const copy = useCallback(async () => {
    await navigator.clipboard.writeText(json);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [json]);

  const download = useCallback(() => {
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `extraction_${extraction.document_id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [json, extraction.document_id]);

  return (
    <div className="flex flex-col gap-6">
      {/* Extracted Fields */}
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
              d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25H12"
            />
          </svg>
          <span className="text-[13px] font-semibold text-foreground">
            Extracted Fields
          </span>
          <span className="ml-auto rounded-md bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
            {extraction.document_id}
          </span>
        </div>
        <div className="px-5 py-1">
          <FieldRow label="Document Type" field={extraction.document_type} />
          <FieldRow label="Company Name" field={extraction.company_name} />
          <FieldRow label="Phone" field={extraction.phone} />
          <FieldRow label="Date" field={extraction.date} />
          <FieldRow label="Invoice Number" field={extraction.invoice_number} />
          <FieldRow label="Total Amount" field={extraction.total_amount} />
          <FieldRow label="Currency" field={extraction.currency} />
        </div>
      </div>

      {/* Raw JSON */}
      <div className="overflow-hidden rounded-2xl border border-border bg-card">
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <div className="flex items-center gap-2">
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
                d="M17.25 6.75 22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3-4.5 16.5"
              />
            </svg>
            <span className="text-[13px] font-semibold text-foreground">
              Raw JSON
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={copy}
              className="rounded-md bg-muted px-2.5 py-1 text-[12px] font-medium text-muted-foreground hover:bg-border hover:text-foreground"
            >
              {copied ? "Copied" : "Copy"}
            </button>
            <button
              onClick={download}
              className="rounded-md bg-primary px-2.5 py-1 text-[12px] font-medium text-white hover:bg-primary-hover"
            >
              Download
            </button>
          </div>
        </div>
        <pre className="max-h-72 overflow-auto bg-gray-900 p-5 font-mono text-[12px] leading-relaxed text-gray-300">
          {json}
        </pre>
      </div>
    </div>
  );
}