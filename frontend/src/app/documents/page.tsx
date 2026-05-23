"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { DocumentRecord } from "@/lib/types";
import { listDocuments } from "@/lib/api";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listDocuments()
      .then((data) => setDocuments(data.documents ?? []))
      .catch((err) => setError(err.message || "Failed to load documents"))
      .finally(() => setLoading(false));
  }, []);

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
                className="rounded-md bg-primary-bg px-2.5 py-1 text-[13px] font-medium text-primary"
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
          <Link
            href="/"
            className="rounded-lg bg-primary px-3.5 py-1.5 text-[13px] font-medium text-white hover:bg-primary-hover"
          >
            New Upload
          </Link>
        </div>
      </nav>

      <main className="mx-auto w-full max-w-5xl flex-1 px-6 pt-10 pb-16">
        <h1 className="text-2xl font-bold text-foreground">Documents</h1>
        <p className="mt-1 text-[15px] text-muted-foreground">
          All uploaded documents and their processing status.
        </p>

        {loading && (
          <div className="mt-10 flex justify-center">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-muted border-t-primary" />
          </div>
        )}

        {error && (
          <div className="mt-10 rounded-2xl border border-error-border bg-error-bg p-5">
            <p className="text-[13px] font-medium text-error-text">{error}</p>
          </div>
        )}

        {!loading && !error && documents.length === 0 && (
          <div className="mt-10 rounded-2xl border border-border bg-card p-12 text-center">
            <p className="text-[15px] font-medium text-foreground">No documents yet</p>
            <p className="mt-1 text-[13px] text-muted-foreground">
              Upload a document to get started.
            </p>
            <Link
              href="/"
              className="mt-4 inline-block rounded-lg bg-primary px-4 py-2 text-[13px] font-medium text-white hover:bg-primary-hover"
            >
              Upload Document
            </Link>
          </div>
        )}

        {!loading && !error && documents.length > 0 && (
          <div className="mt-6 overflow-hidden rounded-2xl border border-border bg-card">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/50">
                  <th className="px-5 py-3 text-left text-[12px] font-semibold uppercase tracking-wide text-muted-foreground">
                    Filename
                  </th>
                  <th className="px-5 py-3 text-left text-[12px] font-semibold uppercase tracking-wide text-muted-foreground">
                    ID
                  </th>
                  <th className="px-5 py-3 text-left text-[12px] font-semibold uppercase tracking-wide text-muted-foreground">
                    Type
                  </th>
                  <th className="px-5 py-3 text-left text-[12px] font-semibold uppercase tracking-wide text-muted-foreground">
                    Size
                  </th>
                  <th className="px-5 py-3 text-left text-[12px] font-semibold uppercase tracking-wide text-muted-foreground">
                    Uploaded
                  </th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr
                    key={doc.document_id}
                    className="border-b border-border/50 last:border-b-0"
                  >
                    <td className="px-5 py-3 text-sm font-medium text-foreground">
                      {doc.original_filename}
                    </td>
                    <td className="px-5 py-3 text-[13px] font-mono text-muted-foreground">
                      {doc.document_id.slice(0, 8)}...
                    </td>
                    <td className="px-5 py-3 text-[13px] text-muted-foreground">
                      {doc.content_type}
                    </td>
                    <td className="px-5 py-3 text-[13px] text-muted-foreground">
                      {doc.size_bytes < 1024 * 1024
                        ? `${(doc.size_bytes / 1024).toFixed(1)} KB`
                        : `${(doc.size_bytes / (1024 * 1024)).toFixed(1)} MB`}
                    </td>
                    <td className="px-5 py-3 text-[13px] text-muted-foreground">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      <footer className="border-t border-border py-6 text-center text-[13px] text-muted-foreground">
        KhmerDoc AI &mdash; Khmer document understanding
      </footer>
    </div>
  );
}