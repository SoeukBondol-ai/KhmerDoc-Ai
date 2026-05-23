import Link from "next/link";

export default function EvaluationPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <nav className="sticky top-0 z-50 border-b border-border bg-white/80 backdrop-blur-xl">
        <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-6">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-[15px] font-semibold tracking-tight text-foreground">
              KhmerDoc<span className="text-primary">AI</span>
            </Link>
            <div className="hidden items-center gap-1 sm:flex">
              <Link
                href="/"
                className="rounded-md px-2.5 py-1 text-[13px] font-medium text-muted-foreground hover:text-foreground"
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
                className="rounded-md bg-primary-bg px-2.5 py-1 text-[13px] font-medium text-primary"
              >
                Evaluation
              </Link>
            </div>
          </div>
          <Link
            href="/"
            className="rounded-lg bg-primary px-3.5 py-1.5 text-[13px] font-medium text-white hover:bg-primary-hover"
          >
            New Upload
          </Link>
        </div>
      </nav>

      <main className="mx-auto w-full max-w-5xl flex-1 px-6 pt-10 pb-16">
        <h1 className="text-2xl font-bold text-foreground">Evaluation</h1>
        <p className="mt-1 text-[15px] text-muted-foreground">
          Evaluate extraction accuracy against ground-truth data.
        </p>

        <div className="mt-10 rounded-2xl border border-border bg-card p-12 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-muted">
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
                d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z"
              />
            </svg>
          </div>
          <p className="text-[15px] font-medium text-foreground">
            Coming soon
          </p>
          <p className="mt-1 text-[13px] text-muted-foreground">
            Evaluation metrics and benchmarking tools are being built.
          </p>
        </div>
      </main>

      <footer className="border-t border-border py-6 text-center text-[13px] text-muted-foreground">
        KhmerDoc AI &mdash; Khmer document understanding
      </footer>
    </div>
  );
}