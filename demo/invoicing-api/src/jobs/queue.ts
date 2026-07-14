// The background job queue. PDF rendering and nightly reconciliation run here so
// they never block a request. In production the jobs are pushed to Redis and
// drained by a worker process; in this build the worker is in-process.

export type Job = () => Promise<void>;

export class JobQueue {
  private readonly pending: Job[] = [];
  private draining = false;
  private idlePromise: Promise<void> = Promise.resolve();

  enqueue(job: Job): void {
    this.pending.push(job);
    if (!this.draining) {
      this.idlePromise = this.drain();
    }
  }

  /** Resolves once the queue has drained. Used by the worker's shutdown hook. */
  async idle(): Promise<void> {
    await this.idlePromise;
  }

  private async drain(): Promise<void> {
    this.draining = true;
    try {
      for (let job = this.pending.shift(); job; job = this.pending.shift()) {
        try {
          await job();
        } catch (err) {
          console.error("job failed", err);
        }
      }
    } finally {
      this.draining = false;
    }
  }
}

export const jobQueue = new JobQueue();
