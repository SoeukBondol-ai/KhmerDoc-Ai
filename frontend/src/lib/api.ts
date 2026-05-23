const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json();
}

export async function uploadDocument(file: File) {
  const form = new FormData();
  form.append("file", file);
  return request<import("./types").UploadResponse>("/documents/upload", {
    method: "POST",
    body: form,
  });
}

export async function runOcr(documentId: string) {
  return request<import("./types").OcrResponse>(
    `/documents/${documentId}/ocr`,
    { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" },
  );
}

export async function runExtraction(documentId: string) {
  return request<import("./types").ExtractionResponse>(
    `/documents/${documentId}/extract`,
    { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" },
  );
}

export async function runLayout(documentId: string) {
  return request<import("./types").LayoutDetectionResponse>(
    `/documents/${documentId}/layout`,
    { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" },
  );
}

export async function getLayout(documentId: string) {
  return request<import("./types").LayoutDetectionResponse>(
    `/documents/${documentId}/layout`,
  );
}

export async function getDocument(documentId: string) {
  return request<{
    document: import("./types").DocumentRecord;
    ocr: import("./types").OcrResponse | null;
    extraction: import("./types").ExtractionResponse | null;
    layout: import("./types").LayoutDetectionResponse | null;
  }>(`/documents/${documentId}`);
}

export async function listDocuments() {
  return request<{ documents: import("./types").DocumentRecord[] }>("/documents");
}