import { describe, expect, it } from "vitest";

import { Message } from "./api";
import {
  CATCH_UP_PAGE_SIZE,
  MAX_CATCH_UP_PAGES,
  catchUpConversationMessages,
  mergeConversationMessages,
} from "./realtimeSync";

function message(id: string, sequence: number, body = id): Message {
  return {
    id,
    conversation_id: "conversation",
    sender_user_id: "sender",
    client_message_id: `client-${id}`,
    sequence_number: sequence,
    body,
    created_at: "2026-09-04T00:00:00Z",
    expires_at: "2026-12-03T00:00:00Z",
    read_by_user_ids: [],
  };
}

describe("mergeConversationMessages", () => {
  it("fills a reconnect gap and restores sequence order", () => {
    expect(
      mergeConversationMessages(
        [message("three", 3)],
        [message("two", 2), message("one", 1)],
      ).map(item => item.id),
    ).toEqual(["one", "two", "three"]);
  });

  it("deduplicates by server id and accepts authoritative catch-up updates", () => {
    const merged = mergeConversationMessages(
      [message("one", 1, "old"), message("three", 3)],
      [message("one", 1, "redacted"), message("two", 2)],
    );

    expect(merged).toHaveLength(3);
    expect(merged.map(item => item.sequence_number)).toEqual([1, 2, 3]);
    expect(merged[0]?.body).toBe("redacted");
  });

  it("paginates through a disconnect gap larger than one history page", async () => {
    const missed = Array.from({ length: 205 }, (_, index) =>
      message(`message-${index + 2}`, index + 2),
    );
    const requests: number[] = [];

    const merged = await catchUpConversationMessages([message("message-1", 1)], async after => {
      requests.push(after);
      return missed
        .filter(item => item.sequence_number > after)
        .slice(0, CATCH_UP_PAGE_SIZE);
    });

    expect(requests).toEqual([1, 101, 201]);
    expect(merged).toHaveLength(206);
    expect(merged.at(-1)?.sequence_number).toBe(206);
  });

  it("retries a failed catch-up request before succeeding", async () => {
    let attempts = 0;
    const merged = await catchUpConversationMessages([], async () => {
      attempts += 1;
      if (attempts === 1) throw new Error("temporary network failure");
      return [message("one", 1)];
    });

    expect(attempts).toBe(2);
    expect(merged.map(item => item.id)).toEqual(["one"]);
  });

  it("fails visibly instead of silently truncating an excessive gap", async () => {
    await expect(
      catchUpConversationMessages([], async after =>
        Array.from({ length: CATCH_UP_PAGE_SIZE }, (_, index) =>
          message(`message-${after + index + 1}`, after + index + 1),
        ),
      ),
    ).rejects.toThrow("safety limit");
    expect(MAX_CATCH_UP_PAGES * CATCH_UP_PAGE_SIZE).toBe(1000);
  });
});
