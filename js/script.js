(function () {
    const form = document.getElementById("rsvp-form");
    const nameInput = document.getElementById("guest-name");
    const button = document.getElementById("rsvp-btn");
    const status = document.getElementById("rsvp-status");
    const turnstileBox = document.getElementById("turnstile-box");
    const storageKey = "babyBossInviteReceived";

    if (!form || !nameInput || !button || !status) {
        return;
    }

    let config = {
        notifyUrl: "/api/notify",
        telegramUsername: "",
        turnstileSiteKey: "",
    };
    let turnstileWidgetId = null;

    if (localStorage.getItem(storageKey) === "1") {
        markAsSent();
    }

    loadConfig().finally(function () {
        setupTurnstile();
        form.addEventListener("submit", onSubmit);
    });

    async function loadConfig() {
        try {
            const response = await fetch("config.json", { cache: "no-store" });
            if (!response.ok) {
                return;
            }
            const data = await response.json();
            config = Object.assign({}, config, data || {});
        } catch (error) {
            // Keep defaults if config.json is missing.
        }
    }

    function setupTurnstile() {
        const siteKey = String(config.turnstileSiteKey || "").trim();
        if (!siteKey || !turnstileBox) {
            return;
        }

        turnstileBox.hidden = false;

        function renderWidget() {
            if (!window.turnstile || turnstileWidgetId !== null) {
                return;
            }
            turnstileWidgetId = window.turnstile.render(turnstileBox, {
                sitekey: siteKey,
                theme: "light",
            });
        }

        if (window.turnstile) {
            renderWidget();
            return;
        }

        let attempts = 0;
        const timer = setInterval(function () {
            attempts += 1;
            if (window.turnstile) {
                clearInterval(timer);
                renderWidget();
            } else if (attempts > 40) {
                clearInterval(timer);
            }
        }, 250);
    }

    function getTurnstileToken() {
        if (!config.turnstileSiteKey) {
            return "";
        }
        if (!window.turnstile || turnstileWidgetId === null) {
            return "";
        }
        return window.turnstile.getResponse(turnstileWidgetId) || "";
    }

    function resetTurnstile() {
        if (window.turnstile && turnstileWidgetId !== null) {
            window.turnstile.reset(turnstileWidgetId);
        }
    }

    async function onSubmit(event) {
        event.preventDefault();

        const guestName = nameInput.value.trim();
        if (!guestName) {
            setStatus("Пожалуйста, введите имя.", "error");
            nameInput.focus();
            return;
        }

        if (config.turnstileSiteKey && !getTurnstileToken()) {
            setStatus("Подтвердите, что вы не робот.", "error");
            return;
        }

        button.disabled = true;
        setStatus("Отправляем уведомление Боссу...", "");

        try {
            await sendNotify(guestName);
            localStorage.setItem(storageKey, "1");
            markAsSent();
            setStatus("Готово! Босс уже знает, что вы получили приглашение.", "ok");
        } catch (error) {
            resetTurnstile();
            const openedTelegram = openTelegramFallback(guestName);
            if (openedTelegram) {
                button.disabled = false;
                setStatus(
                    "Автоуведомление недоступно. Откройте Telegram и нажмите Send, затем можно повторить попытку.",
                    "error"
                );
                return;
            }

            button.disabled = false;
            setStatus(
                error.message || "Ошибка сети. Попробуйте ещё раз.",
                "error"
            );
        }
    }

    async function sendNotify(guestName) {
        const payload = {
            guestName: guestName,
        };
        const turnstileToken = getTurnstileToken();
        if (turnstileToken) {
            payload.turnstileToken = turnstileToken;
        }

        const response = await fetch(config.notifyUrl || "/api/notify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json().catch(function () {
            return {};
        });

        if (!response.ok || !data.ok) {
            throw new Error(data.error || "Не удалось отправить уведомление.");
        }
    }

    function openTelegramFallback(guestName) {
        const username = String(config.telegramUsername || "").replace(/^@/, "");
        if (!username) {
            return false;
        }

        const text =
            "Я получил(а) приглашение на 1 год Михаила (Baby Boss).\n" +
            "Меня зовут: " +
            guestName;

        const url =
            "https://t.me/" +
            encodeURIComponent(username) +
            "?text=" +
            encodeURIComponent(text);

        window.open(url, "_blank", "noopener,noreferrer");
        return true;
    }

    function markAsSent() {
        button.disabled = true;
        button.textContent = "Приглашение получено";
        if (!status.textContent) {
            setStatus("Спасибо! Уведомление уже отправлено.", "ok");
        }
    }

    function setStatus(message, type) {
        status.textContent = message;
        status.classList.remove("is-ok", "is-error");
        if (type === "ok") {
            status.classList.add("is-ok");
        }
        if (type === "error") {
            status.classList.add("is-error");
        }
    }
})();
