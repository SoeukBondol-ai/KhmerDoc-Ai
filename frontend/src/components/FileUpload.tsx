"use client";

import { useCallback, useRef, useState } from "react";

const ACCEPTED_TYPES = [
  "image/png",
  "image/jpeg",
  "image/jpg",
  "image/webp",
  "image/tiff",
  "application/pdf",
];

export default function FileUpload({
  onFileSelected,
}: {
  onFileSelected: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validate = useCallback(
    (file: File) => {
      if (!ACCEPTED_TYPES.includes(file.type)) {
        setError("Unsupported file type. Please upload an image or PDF.");
        return false;
      }
      setError(null);
      return true;
    },
    [],
  );

  const handleFile = useCallback(
    (file: File) => {
      if (validate(file)) onFileSelected(file);
    },
    [validate, onFileSelected],
  );

  return (
    <div className="flex flex-col items-center gap-4">
      <div
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const file = e.dataTransfer.files[0];
          if (file) handleFile(file);
        }}
        className={`flex w-full cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed py-14 transition-all ${
          dragOver
            ? "border-primary bg-primary-bg"
            : "border-border bg-card hover:border-primary/40 hover:bg-primary-bg/30"
        }`}
      >
        <div
          className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl ${
            dragOver ? "bg-primary/10" : "bg-muted"
          }`}
        >
          <svg
            className={`h-5 w-5 ${dragOver ? "text-primary" : "text-muted-foreground"}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 19.5 19.5H6.75Z"
            />
          </svg>
        </div>
        <p className="text-[15px] font-semibold text-foreground">
          Upload Khmer document
        </p>
        <p className="mt-1 text-[13px] text-muted-foreground">
          Drag and drop or choose a file
        </p>
        <button
          type="button"
          className="mt-5 rounded-lg bg-primary px-4 py-2 text-[13px] font-medium text-white hover:bg-primary-hover active:opacity-90"
          onClick={(e) => {
            e.stopPropagation();
            inputRef.current?.click();
          }}
        >
          Choose File
        </button>
        <p className="mt-3 text-[12px] text-muted-foreground/60">
          PNG, JPG, JPEG, PDF
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-error-border bg-error-bg px-4 py-2.5">
          <p className="text-[13px] font-medium text-error-text">{error}</p>
        </div>
      )}

      <input
        ref={inputRef}
        type="file"
        accept={ACCEPTED_TYPES.join(",")}
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />
    </div>
  );
}