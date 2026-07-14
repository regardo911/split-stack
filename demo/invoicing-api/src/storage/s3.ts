// Object storage for rendered invoice PDFs.
//
// In production this wraps the S3 SDK against config.s3Bucket. Here it keeps the
// objects in a Map and signs URLs that point back at this service's /files
// handler, so PDF export works with no cloud account.

import crypto from "crypto";
import { config } from "../config";

export interface ObjectStore {
  put(key: string, body: Buffer): Promise<void>;
  get(key: string): Promise<Buffer | null>;
  sign(key: string): string;
  keys(): string[];
}

export class InMemoryObjectStore implements ObjectStore {
  private readonly objects = new Map<string, Buffer>();

  constructor(
    private readonly bucket: string = config.s3Bucket,
    private readonly signingSecret: string = config.s3SigningSecret,
  ) {}

  async put(key: string, body: Buffer): Promise<void> {
    this.objects.set(key, Buffer.from(body));
  }

  async get(key: string): Promise<Buffer | null> {
    return this.objects.get(key) ?? null;
  }

  sign(key: string): string {
    const expires = Math.floor(Date.now() / 1000) + config.signedUrlTtlSeconds;
    const signature = crypto
      .createHmac("sha256", this.signingSecret)
      .update(`${this.bucket}/${key}:${expires}`)
      .digest("hex");

    const path = key.split("/").map(encodeURIComponent).join("/");
    return `${config.publicBaseUrl}/files/${path}?expires=${expires}&signature=${signature}`;
  }

  keys(): string[] {
    return [...this.objects.keys()];
  }
}

export const objectStore: ObjectStore = new InMemoryObjectStore();
