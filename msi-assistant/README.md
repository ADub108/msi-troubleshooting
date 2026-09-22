# MSI Assistant (AI chatbot for the troubleshooting site)

Three parts:
- `worker.js` — the chat API, a Cloudflare Worker. Holds the knowledge (all four troubleshooters plus
  machinesolutions.com content) and calls Claude. Your API key stays here, never in the web page.
- `assistant.js` — the chat button and panel. Already included in the site package under `/assistant/`.
- `build_knowledge.py` — rebuilds `worker.js` when troubleshooter content changes or a new app is added.

## Deploy the API (one time, in the Cloudflare dashboard)
1. Anthropic Console (console.anthropic.com), on a company account: create an API key and set a monthly spend limit.
2. Cloudflare > Workers & Pages > Create > Create Worker. Name it **msi-assistant** > Deploy.
3. Edit code > replace everything with the contents of `worker.js` > Deploy.
   (Command-line alternative: `npx wrangler deploy worker.js --name msi-assistant --compatibility-date 2026-09-01`)
4. Worker > Settings > Variables and Secrets > Add: type **Secret**, name `ANTHROPIC_API_KEY`, value = the key. Deploy.
5. Check https://msi-assistant.adam-wade.workers.dev/health shows `"ok":true`.
6. Upload the new site package to the **msi** project as usual.

If you name the Worker something else, change `ENDPOINT` at the top of `assistant/assistant.js`.
The API only answers requests from msi.adam-wade.workers.dev and msitroubleshooting.com (edit `DEFAULT_ORIGINS`
in worker.js, or set an `ALLOWED_ORIGINS` variable, if the site moves). Optional variable `MODEL` switches models.

## Updating what it knows
After the troubleshooters change (or a new one is added to the site):
    python build_knowledge.py ../site           # troubleshooters + website_content.json
    python build_knowledge.py ../site --crawl   # also pulls every page on machinesolutions.com (needs internet)
Then paste the new `worker.js` into the Worker and Deploy. New apps also need a line in `APPS` at the top of build_knowledge.py.

## Guardrails built in
- Answers only from the troubleshooting guides and website content; says so when it doesn't know.
- Service-technician-level repairs are never described, only who to contact; internal source references are excluded.
- Never advises bypassing guards or interlocks; includes the guides' safety notes with the steps it gives.
- Commercial questions go to sales@machinesolutions.com; it does not quote prices or commit to repairs.
- Links answers to the exact troubleshooter page. Knows which app, model and symptom the user is looking at.
- Basic per-visitor rate limit. For stronger protection add a Cloudflare rate-limiting rule on /chat.
