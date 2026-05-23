"use client";

import { useCallback, useState } from "react";
import Link from "next/link";
import type {
  ExtractionResponse,
  LayoutDetectionResponse,
  OcrResponse,
  ProcessingStep,
  UploadResponse,
} from "@/lib/types";
import { uploadDocument, runOcr, runExtraction, runLayout } from "@/lib/api";
import FileUpload from "@/components/FileUpload";
import DocumentPreview from "@/components/DocumentPreview";
import OcrTextPanel from "@/components/OcrTextPanel";
import ExtractionJsonPanel from "@/components/ExtractionJsonPanel";
import LayoutRegionList from "@/components/LayoutRegionList";
import LoadingState from "@/components/LoadingState";
import ErrorMessage from "@/components/ErrorMessage";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [step, setStep] = useState<ProcessingStep>("idle");
  const [error, setError] = useState<string | null>(null);

  const [ocrResult, setOcrResult] = useState<OcrResponse | null>(null);
  const [extractionResult, setExtractionResult] =
    useState<ExtractionResponse | null>(null);
  const [layoutResult, setLayoutResult] =
    useState<LayoutDetectionResponse | null>(null);

  const process = useCallback(
    async (file: File) => {
      setFile(file);
      setError(null);
      setOcrResult(null);
      setExtractionResult(null);
      setLayoutResult(null);

      try {
        setStep("uploading");
        const upload: UploadResponse = await uploadDocument(file);
        setDocumentId(upload.document_id);

        setStep("running_ocr");
        const ocr: OcrResponse = await runOcr(upload.document_id);
        setOcrResult(ocr);

        setStep("extracting");
        const extraction: ExtractionResponse = await runExtraction(
          upload.document_id,
        );
        setExtractionResult(extraction);

        setStep("detecting_layout");
        const layout: LayoutDetectionResponse = await runLayout(
          upload.document_id,
        );
        setLayoutResult(layout);

        setStep("done");
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong. Please try again.",
        );
        setStep("error");
      }
    },
    [],
  );

  const reset = useCallback(() => {
    setFile(null);
    setDocumentId(null);
    setStep("idle");
    setError(null);
    setOcrResult(null);
    setExtractionResult(null);
    setLayoutResult(null);
  }, []);

  const hasResult =
    (step === "done" || step === "error") &&
    (ocrResult || extractionResult);

  return (
    <div className="flex min-h-screen flex-col">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 border-b border-border bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-[15px] font-semibold tracking-tight text-foreground">
              KhmerDoc<span className="text-primary">AI</span>
            </Link>
            <div className="hidden items-center gap-1 sm:flex">
              <Link
                href="/"
                className="rounded-md bg-primary-bg px-2.5 py-1 text-[13px] font-medium text-primary"
              >
                Upload
              </Link>
              <Link
                href="/documents"
                className="rounded-md px-2.5 py-1 text-[13px] font-medium text-muted-foreground hover:text-foreground"
              >
                Documents
              </Link>
              <Link
                href="/evaluation"
                className="rounded-md px-2.5 py-1 text-[13px] font-medium text-muted-foreground hover:text-foreground"
              >
                Evaluation
              </Link>
            </div>
          </div>
          {hasResult && (
            <button
              onClick={reset}
              className="rounded-lg bg-primary px-3.5 py-1.5 text-[13px] font-medium text-white hover:bg-primary-hover active:opacity-90"
            >
              New Upload
            </button>
          )}
        </div>
      </nav>

      {/* Main content */}
      <main className="mx-auto w-full max-w-5xl flex-1 px-6">
        {step === "idle" && !hasResult && (
          <div className="mx-auto max-w-lg pt-20 pb-16">
            <div className="mb-10 text-center">
              <h1 className="text-2xl font-bold text-foreground">
                Understand Khmer documents with AI
              </h1>
              <p className="mt-2 text-[15px] text-muted-foreground">
                Upload invoices, receipts, quotations, and forms.
              </p>
            </div>
            <FileUpload onFileSelected={process} />
          </div>
        )}

        <LoadingState step={step} />

        {error && !hasResult && (
          <div className="mx-auto max-w-lg pt-20">
            <ErrorMessage message={error} />
          </div>
        )}

        {hasResult && (
          <div className="grid grid-cols-1 gap-8 pb-12 pt-8 lg:grid-cols-2">
            {/* Left column */}
            <div className="flex flex-col gap-6">
              {file && documentId && (
                <DocumentPreview
                  file={file}
                  documentId={documentId}
                  layoutRegions={layoutResult?.regions}
                  imageWidth={layoutResult?.image_width}
                  imageHeight={layoutResult?.image_height}
                />
              )}
              {layoutResult && layoutResult.regions.length > 0 && (
                <LayoutRegionList regions={layoutResult.regions} />
              )}
              {ocrResult && <OcrTextPanel text={ocrResult.text} />}
            </div>

            {/* Right column */}
            <div className="flex flex-col gap-6">
              {extractionResult && (
                <ExtractionJsonPanel
                  extraction={extractionResult.extraction}
                />
              )}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-6 text-center text-[13px] text-muted-foreground">
        KhmerDoc AI &mdash; Khmer document understanding
      </footer>
    </div>
  );
}