// The database handle the data-access layer talks to.
//
// In production this is a `pg` Pool against the Postgres instance at
// config.dbUrl. Here it is an in-memory store that speaks the same
// query(sql, params) interface, so the service runs with no database. It
// matches on the SQL the data-access layer sends and counts every round trip.

export interface Row {
  [column: string]: unknown;
}

export interface Db {
  query(sql: string, params?: unknown[]): Promise<Row[]>;
  /** Round trips served since boot. The pg Pool exposes the same counter. */
  readonly queryCount: number;
}

export interface InvoiceRow extends Row {
  id: string;
  customer: string;
  status: string;
  currency: string;
  created_at: string;
  paid_at: string | null;
}

export interface LineItemRow extends Row {
  id: string;
  invoice_id: string;
  description: string;
  amount_cents: number;
  taxable: boolean;
}

const invoices: InvoiceRow[] = [
  {
    id: "inv_41",
    customer: "Northwind Traders",
    status: "paid",
    currency: "USD",
    created_at: "2026-05-02T09:14:00.000Z",
    paid_at: "2026-05-09T11:02:00.000Z",
  },
  {
    id: "inv_42",
    customer: "Contoso Ltd",
    status: "open",
    currency: "USD",
    created_at: "2026-05-14T16:40:00.000Z",
    paid_at: null,
  },
  {
    id: "inv_43",
    customer: "Fabrikam Inc",
    status: "open",
    currency: "USD",
    created_at: "2026-05-21T08:05:00.000Z",
    paid_at: null,
  },
  {
    id: "inv_44",
    customer: "Tailspin Toys",
    status: "open",
    currency: "USD",
    created_at: "2026-06-01T13:27:00.000Z",
    paid_at: null,
  },
];

const lineItems: LineItemRow[] = [
  { id: "li_1", invoice_id: "inv_41", description: "Platform licence, May", amount_cents: 49900, taxable: true },
  { id: "li_2", invoice_id: "inv_41", description: "Onboarding credit", amount_cents: -5000, taxable: false },
  { id: "li_3", invoice_id: "inv_42", description: "Platform licence, May", amount_cents: 49900, taxable: true },
  { id: "li_4", invoice_id: "inv_42", description: "Overage, 1.2M API calls", amount_cents: 18400, taxable: true },
  { id: "li_5", invoice_id: "inv_43", description: "Platform licence, May", amount_cents: 99900, taxable: true },
  { id: "li_6", invoice_id: "inv_43", description: "Support retainer", amount_cents: 25000, taxable: false },
  { id: "li_7", invoice_id: "inv_44", description: "Enterprise licence, Q2", amount_cents: 100017, taxable: true },
  { id: "li_8", invoice_id: "inv_44", description: "Training day", amount_cents: 120000, taxable: false },
];

/** The store hands out copies, exactly as a real driver hands out fresh rows. */
const clone = <T extends Row>(row: T): T => ({ ...row });

const normalize = (sql: string): string => sql.replace(/\s+/gu, " ").trim();

class InMemoryDb implements Db {
  private served = 0;

  get queryCount(): number {
    return this.served;
  }

  async query(sql: string, params: unknown[] = []): Promise<Row[]> {
    this.served += 1;

    switch (normalize(sql)) {
      case "SELECT * FROM invoices WHERE id = $1":
        return invoices.filter((inv) => inv.id === params[0]).map(clone);

      case "SELECT * FROM invoices WHERE status = $1 ORDER BY created_at DESC":
        return invoices
          .filter((inv) => inv.status === params[0])
          .sort((a, b) => b.created_at.localeCompare(a.created_at))
          .map(clone);

      case "SELECT * FROM line_items WHERE invoice_id = $1":
        return lineItems.filter((li) => li.invoice_id === params[0]).map(clone);

      case "UPDATE invoices SET status = $1, paid_at = now() WHERE id = $2 RETURNING *": {
        const target = invoices.find((inv) => inv.id === params[1]);
        if (!target) return [];
        target.status = String(params[0]);
        target.paid_at = new Date().toISOString();
        return [clone(target)];
      }

      default:
        throw new Error(`in-memory store has no handler for: ${normalize(sql)}`);
    }
  }
}

export const db: Db = new InMemoryDb();
