// Nightly reconciliation: settle every charge the ledger still shows as pending.
// Scheduled by the worker at 02:00 UTC.

import type { Charge, Provider } from "./provider";

export async function reconcile(provider: Provider, pending: Charge[]): Promise<void> {
  for (const charge of pending) {
    let result = await provider.charge(charge);

    if (!result.ok) {
      result = await provider.charge(charge);
    }

    if (!result.ok) {
      console.error(`reconcile: charge ${charge.id} failed twice, leaving pending`);
    }
  }
}
