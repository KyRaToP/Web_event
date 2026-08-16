/**
 * Cloudflare Worker: Telegram notify for Baby Boss invitation.
 *
 * Security:
 * - CORS allowlist (GitHub Pages + local dev)
 * - Cloudflare Turnstile verification (when TURNSTILE_SECRET_KEY is set)
 * - Soft rate limit via Cache API (per client IP)
 *
 * Secrets (Cloudflare Dashboard → Settings → Variables / Secrets):
 * - TELEGRAM_BOT_TOKEN
 * - TELEGRAM_CHAT_ID
 * - TURNSTILE_SECRET_KEY (optional but recommended)
 */

const MAX_GUEST_NAME_LENGTH = 60;
const RATE_LIMIT_MAX = 8;
const RATE_LIMIT_WINDOW_SECONDS = 3600;

const DEFAULT_ALLOWED_ORIGINS = [
  "https://kyratop.github.io",
  "http://127.0.0.1:8000",
  "http://localhost:8000",
];

function normalizeGuestName(raw) {
  return String(raw || "")
    .replace(/[\u0000-\u001F\u007F]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, MAX_GUEST_NAME_LENGTH);
}

function getAllowedOrigins(env) {
  const fromEnv = String(env.ALLOWED_ORIGINS || "")
    .split(",")
    .map(function (item) {
      return item.trim();
    })
    .filter(Boolean);
  return fromEnv.length > 0 ? fromEnv : DEFAULT_ALLOWED_ORIGINS;
}

function corsHeadersFor(request, env) {
  const origin = request.headers.get("Origin") || "";
  const allowed = getAllowedOrigins(env);
  const headers = {
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
  if (allowed.includes(origin)) {
    headers["Access-Control-Allow-Origin"] = origin;
  }
  return headers;
}

function clientIp(request) {
  return (
    request.headers.get("CF-Connecting-IP") ||
    request.headers.get("X-Forwarded-For") ||
    "unknown"
  );
}

async function isRateLimited(request) {
  const ip = clientIp(request);
  const cache = caches.default;
  const cacheKey = new Request(
    "https://baby-boss-rate-limit.internal/" + encodeURIComponent(ip)
  );

  let count = 0;
  const cached = await cache.match(cacheKey);
  if (cached) {
    count = parseInt(await cached.text(), 10) || 0;
  }

  if (count >= RATE_LIMIT_MAX) {
    return true;
  }

  await cache.put(
    cacheKey,
    new Response(String(count + 1), {
      headers: {
        "Cache-Control": "max-age=" + RATE_LIMIT_WINDOW_SECONDS,
        "Content-Type": "text/plain",
      },
    })
  );
  return false;
}

async function verifyTurnstile(token, secret, request) {
  if (!secret) {
    return { ok: true, skipped: true };
  }
  if (!token) {
    return { ok: false, error: "Подтвердите, что вы не робот (Turnstile)." };
  }

  const form = new FormData();
  form.append("secret", secret);
  form.append("response", token);
  form.append("remoteip", clientIp(request));

  const response = await fetch(
    "https://challenges.cloudflare.com/turnstile/v0/siteverify",
    {
      method: "POST",
      body: form,
    }
  );
  const data = await response.json().catch(function () {
    return {};
  });

  if (!data.success) {
    return { ok: false, error: "Проверка Turnstile не пройдена." };
  }
  return { ok: true };
}

export default {
  async fetch(request, env) {
    const cors = corsHeadersFor(request, env);

    if (request.method === "OPTIONS") {
      const origin = request.headers.get("Origin") || "";
      if (!getAllowedOrigins(env).includes(origin)) {
        return new Response(null, { status: 403 });
      }
      return new Response(null, {
        status: 204,
        headers: cors,
      });
    }

    if (request.method !== "POST") {
      return jsonResponse(
        { ok: false, error: "Method not allowed. Use POST." },
        405,
        cors
      );
    }

    const origin = request.headers.get("Origin") || "";
    // Browsers send Origin; direct curl may omit it — still rate-limit + Turnstile.
    if (origin && !getAllowedOrigins(env).includes(origin)) {
      return jsonResponse(
        { ok: false, error: "Origin not allowed." },
        403,
        cors
      );
    }

    if (await isRateLimited(request)) {
      return jsonResponse(
        {
          ok: false,
          error: "Слишком много запросов. Попробуйте позже.",
        },
        429,
        cors
      );
    }

    let guestName = "";
    let turnstileToken = "";
    try {
      const data = await request.json();
      guestName = normalizeGuestName(data.guestName);
      turnstileToken = String(data.turnstileToken || "").trim();
    } catch (error) {
      return jsonResponse({ ok: false, error: "Некорректный JSON." }, 400, cors);
    }

    if (!guestName) {
      return jsonResponse({ ok: false, error: "Укажите имя гостя." }, 400, cors);
    }

    const turnstileSecret = String(env.TURNSTILE_SECRET_KEY || "").trim();
    try {
      const turnstile = await verifyTurnstile(
        turnstileToken,
        turnstileSecret,
        request
      );
      if (!turnstile.ok) {
        return jsonResponse(
          { ok: false, error: turnstile.error || "Turnstile failed." },
          403,
          cors
        );
      }
    } catch (error) {
      return jsonResponse(
        { ok: false, error: "Не удалось проверить Turnstile." },
        502,
        cors
      );
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
        503,
        cors
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
        502,
        cors
      );
    }

    const tgData = await tgResponse.json().catch(function () {
      return {};
    });

    if (!tgResponse.ok || !tgData.ok) {
      return jsonResponse(
        {
          ok: false,
          error: "Telegram API error",
        },
        502,
        cors
      );
    }

    return jsonResponse({ ok: true }, 200, cors);
  },
};

function jsonResponse(payload, status, corsHeaders) {
  return new Response(JSON.stringify(payload), {
    status: status,
    headers: Object.assign(
      {
        "Content-Type": "application/json; charset=utf-8",
      },
      corsHeaders || {}
    ),
  });
}
