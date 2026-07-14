// Download links for rendered invoice PDFs.

import type { ObjectStore } from "./s3";

/** A time-limited URL the customer can use to fetch their latest invoice PDF. */
export const downloadUrl = (store: ObjectStore, id: string): string =>
  store.sign(`invoices/${id}/latest.pdf`);
