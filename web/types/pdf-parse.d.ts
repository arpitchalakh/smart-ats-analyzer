declare module 'pdf-parse' {
  type Result = { text: string };
  export default function pdfParse(data: Buffer | Uint8Array): Promise<Result>;
}
