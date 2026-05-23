"use client";

export default function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="overflow-hidden rounded-2xl border border-error-border bg-error-bg p-5">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-error-border">
          <svg
            className="h-3 w-3 text-error-text"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z"
            />
          </svg>
        </div>
        <p className="text-[13px] font-medium text-error-text">{message}</p>
      </div>
    </div>
  );
}