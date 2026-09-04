import { Message } from "./api";

export const CATCH_UP_PAGE_SIZE = 100;
export const MAX_CATCH_UP_PAGES = 10;
export const CATCH_UP_RETRY_ATTEMPTS = 2;

type FetchMessagePage = (afterSequence: number, limit: number) => Promise<Message[]>;

/**
 * Reconcile durable HTTP history with best-effort live events without duplicating
 * a message or regressing conversation sequence order.
 */
export function mergeConversationMessages(current: Message[], catchUp: Message[]): Message[] {
  const messages = new Map(current.map(message => [message.id, message]));
  for (const message of catchUp) messages.set(message.id, message);
  return [...messages.values()].sort(
    (left, right) => left.sequence_number - right.sequence_number,
  );
}

export function latestSequence(messages: Message[]): number {
  return messages.reduce(
    (latest, message) => Math.max(latest, message.sequence_number),
    0,
  );
}

async function fetchWithRetry(
  fetchPage: FetchMessagePage,
  afterSequence: number,
  limit: number,
): Promise<Message[]> {
  let lastError: unknown;
  for (let attempt = 0; attempt < CATCH_UP_RETRY_ATTEMPTS; attempt += 1) {
    try {
      return await fetchPage(afterSequence, limit);
    } catch (reason) {
      lastError = reason;
    }
  }
  throw lastError;
}

/**
 * Fetch ascending pages until the server reports the end of the gap. Every
 * request and the total reconnect workload are bounded. Reaching the cap is an
 * explicit error rather than silently presenting an incomplete thread.
 */
export async function catchUpConversationMessages(
  current: Message[],
  fetchPage: FetchMessagePage,
): Promise<Message[]> {
  let merged = current;
  let cursor = latestSequence(merged);
  for (let pageNumber = 0; pageNumber < MAX_CATCH_UP_PAGES; pageNumber += 1) {
    const page = await fetchWithRetry(fetchPage, cursor, CATCH_UP_PAGE_SIZE);
    const next = mergeConversationMessages(merged, page);
    const nextCursor = latestSequence(next);
    if (page.length > 0 && nextCursor <= cursor) {
      throw new Error("Realtime catch-up did not advance the message sequence.");
    }
    merged = next;
    cursor = nextCursor;
    if (page.length < CATCH_UP_PAGE_SIZE) return merged;
  }
  throw new Error("Realtime catch-up safety limit reached; reopen the conversation.");
}
