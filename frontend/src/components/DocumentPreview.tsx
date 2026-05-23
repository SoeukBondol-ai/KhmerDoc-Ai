"use client";

import type { LayoutRegion } from "@/lib/types";
import LayoutOverlay from "./LayoutOverlay";

export default function DocumentPreview({
  file,
  documentId,
  layoutRegions,
  imageWidth,
  imageHeight,
}: {
  file: File;
  documentId: string;
  layoutRegions?: LayoutRegion[];
  imageWidth?: number | null;
  imageHeight?: number | null;
}) {
  const isImage = file.type.startsWith("image/");
  const imageUrl = isImage ? URL.createObjectURL(file) : null;

  if (!isImage) {
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
              d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0 0 22.5 18.75V5.25A2.25 2.25 0 0 0 20.25 3H3.75A2.25 2.25 0 0 0 1.5 5.25v13.5A2.25 2.25 0 0 0 3.75 21Z"
            />
          </svg>
          <span className="text-[13px] font-semibold text-foreground">
            Original Document
          </span>
        </div>
        <div className="flex min-h-64 flex-col items-center justify-center px-6 py-10">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-muted">
            <svg
              className="h-6 w-6 text-muted-foreground"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
              />
            </svg>
          </div>
          <p className="text-sm font-medium text-foreground">{file.name}</p>
          <p className="mt-1 text-[13px] text-muted-foreground">
            PDF preview not yet supported
          </p>
          <p className="mt-1 text-[12px] text-muted-foreground/50">
            ID: {documentId}
          </p>
        </div>
      </div>
    );
  }

  const showOverlay = layoutRegions && layoutRegions.length > 0;

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
            d="m2.25 15.75 5.159-5.159a2.25 2.25 0 0 1 3.182 0l5.159 5.159m-1.5-1.5 1.409-1.409a2.25 2.25 0 0 1 3.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0 0 22.5 18.75V5.25A2.25 2.25 0 0 0 20.25 3H3.75A2.25 2.25 0 0 0 1.5 5.25v13.5A2.25 2.25 0 0 0 3.75 21Z"
          />
        </svg>
        <span className="text-[13px] font-semibold text-foreground">
          Original Document
        </span>
        {showOverlay && (
          <span className="ml-auto rounded-md bg-primary-bg px-2 py-0.5 text-[11px] font-medium text-primary">
            Layout overlay
          </span>
        )}
      </div>
      <div className="flex items-center justify-center bg-muted/50 p-4">
        {showOverlay ? (
          <LayoutOverlay
            regions={layoutRegions}
            imageWidth={imageWidth}
            imageHeight={imageHeight}
            imageUrl={imageUrl!}
            alt="Uploaded document"
          />
        ) : (
          imageUrl && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={imageUrl}
              alt="Uploaded document"
              className="max-h-125 rounded-lg object-contain"
            />
          )
        )}
      </div>
    </div>
  );
}