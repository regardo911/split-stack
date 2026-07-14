// The payment provider's charge API.
//
// In production this is an HTTPS client against the provider. Here it is a stub
// that keeps a ledger in memory and reproduces the provider's documented
// behaviour: a charge is captured the moment it is accepted, an idempotency key
// makes a repeat of the same charge a no-op, and a charge can settle on the
// provider's side after the client has already given up waiting for the reply.

export interface Charge {
  id: string;
  amountCents: number;
}

export interface ChargeResult {
  ok: boolean;
}

export interface Provider {
  charge(charge: Charge, idempotencyKey?: string): Promise<ChargeResult>;
}

export class StubProvider implements Provider {
  /** Every charge the provider captured, in order. Money moved for each entry. */
  readonly ledger: Charge[] = [];

  private readonly keys = new Set<string>();

  /** Charge ids whose first attempt settles on our side but times out on the client. */
  constructor(private readonly slowCharges: Set<string> = new Set()) {}

  async charge(charge: Charge, idempotencyKey?: string): Promise<ChargeResult> {
    if (idempotencyKey !== undefined && this.keys.has(idempotencyKey)) {
      return { ok: true };
    }

    const attempt = this.ledger.filter((entry) => entry.id === charge.id).length + 1;

    this.ledger.push({ ...charge });
    if (idempotencyKey !== undefined) {
      this.keys.add(idempotencyKey);
    }

    if (attempt === 1 && this.slowCharges.has(charge.id)) {
      return { ok: false };
    }

    return { ok: true };
  }
}
