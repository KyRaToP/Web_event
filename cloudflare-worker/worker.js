/**
 * Cloudflare Worker: Telegram notify for Baby Boss invitation.
 *
 * What it does:
 * - Accepts POST JSON: { "guestName": "Anna" }
 * - Sends a Telegram message via Bot API
 * - Allows CORS so GitHub Pages can call this Worker
 *
 * Required Worker secrets (Cloudflare Dashboard → Settings → Variables):
 * - TELEGRAM_BOT_TOKEN
 * - TELEGRAM_CHAT_ID
 */

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: CORS_HEADERS,
      });
    }

    if (request.method !== "POST") {
      return jsonResponse(
        { ok: false, error: "Method not allowed. Use POST." },
        405
      );
    }

    let guestName = "";
    try {
      const data = await request.json();
      guestName = String(data.guestName || "").trim();
    } catch (error) {
      return jsonResponse({ ok: false, error: "Некорректный JSON." }, 400);
    }

    if (!guestName) {
      return jsonResponse({ ok: false, error: "Укажите имя гостя." }, 400);
    }

    const token = String(env.TELEGRAM_BOT_TOKEN || "").trim();
    const chatId = String(env.TELEGRAM_CHAT_ID || "").trim();

    if (!token || !chatId) {
      return jsonResponse(
        {
          ok: false,
          error:
            "Telegram secrets not configured on Worker (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID).",
        },
        503
      );
    }

    const text =
      "Baby Boss Invite\n\n" +
      "Гость получил приглашение: " +
      guestName +
      "\n" +
      "Событие: 1 год Михаила";

    let tgResponse;
    try {
      tgResponse = await fetch(
        "https://api.telegram.org/bot" + token + "/sendMessage",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            chat_id: chatId,
            text: text,
            disable_web_page_preview: true,
          }),
        }
      );
    } catch (error) {
      return jsonResponse(
        { ok: false, error: "Network error while calling Telegram API." },
        502
      );
    }

    const tgData = await tgResponse.json().catch(function () {
      return {};
    });

    if (!tgResponse.ok || !tgData.ok) {
      return jsonResponse(
        {
          ok: false,
          error: tgData.description || "Telegram API error",
        },
        502
      );
    }

    return jsonResponse({ ok: true }, 200);
  },
};

function jsonResponse(payload, status) {
  return new Response(JSON.stringify(payload), {
    status: status,
    headers: Object.assign(
      {
        "Content-Type": "application/json; charset=utf-8",
      },
      CORS_HEADERS
    ),
  });
}
