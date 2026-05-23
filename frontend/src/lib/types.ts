export type ExtractedField = {
  value: string | null;
  confidence: number;
  source: string;
};

export type DocumentExtraction = {
  document_id: string;
  document_type: ExtractedField;
  company_name: ExtractedField;
  phone: ExtractedField;
  date: ExtractedField;
  invoice_number: ExtractedField;
  total_amount: ExtractedField;
  currency: ExtractedField;
  raw_text_preview?: string | null;
};

export type LayoutRegion = {
  id: string;
  label: string;
  bbox: [number, number, number, number];
  confidence: number;
  source: string;
  display_color: string;
  normalized_bbox?: number[] | null;
};

export type LayoutDetectionResponse = {
  document_id: string;
  regions: LayoutRegion[];
  image_width?: number | null;
  image_height?: number | null;
  mode: string;
};

export type UploadResponse = {
  document_id: string;
  filename: string;
  content_type?: string;
  size_bytes?: number;
  saved_path?: string;
  created_at?: string;
};

export type OcrResponse = {
  document_id: string;
  text: string;
  language?: string | null;
  source?: string | null;
  created_at?: string;
};

export type ExtractionResponse = {
  document_id: string;
  extraction: DocumentExtraction;
};

export type DocumentRecord = {
  document_id: string;
  original_filename: string;
  stored_filename: string;
  content_type: string;
  size_bytes: number;
  saved_path: string;
  created_at: string;
  ocr_output_path?: string | null;
};

export type ProcessingStep =
  | "idle"
  | "uploading"
  | "running_ocr"
  | "extracting"
  | "detecting_layout"
  | "done"
  | "error";