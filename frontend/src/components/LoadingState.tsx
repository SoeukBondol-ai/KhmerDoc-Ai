"use client";

import type { ProcessingStep } from "@/lib/types";

const STEPS: { key: ProcessingStep; label: string }[] = [
  { key: "uploading", label: "Uploading document" },
  { key: "running_ocr", label: "Running OCR" },
  { key: "extracting", label: "Extracting fields" },
];

export default function LoadingState({ step }: { step: ProcessingStep }) {
  if (step === "idle" || step === "error" || step === "done") return null;

  const currentIdx = STEPS.findIndex((s) => s.key === step);

  return (
    <div className="mx-auto max-w-md pt-20 pb-16">
      <div className="overflow-hidden rounded-2xl border border-border bg-card p-6">
        <div className="mb-5 flex items-center gap-3">
          <div className="h-4 w-4 animate-spin rounded-full border-2 border-muted border-t-primary" />
          <span className="text-sm font-medium text-foreground">
            Processing document
          </span>
        </div>
        <div className="flex flex-col gap-3">
          {STEPS.map((s, idx) => {
            const isComplete = idx < currentIdx;
            const isCurrent = idx === currentIdx;

            return (
              <div key={s.key} className="flex items-center gap-3">
                <div
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold ${
                    isComplete
                      ? "bg-primary text-white"
                      : isCurrent
                        ? "border-2 border-primary text-primary"
                        : "border-2 border-border text-muted-foreground"
                  }`}
                >
                  {isComplete ? (
                    <svg
                      className="h-3 w-3"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={3}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : (
                    idx + 1
                  )}
                </div>
                <span
                  className={`text-[13px] ${
                    isComplete
                      ? "font-medium text-foreground"
                      : isCurrent
                        ? "font-medium text-foreground"
                        : "text-muted-foreground"
                  }`}
                >
                  {s.label}
                </span>
                {isCurrent && (
                  <span className="ml-auto text-[11px] text-primary">
                    in progress
                  </span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}