---
applyTo: "frontend/**/*.svelte,frontend/**/*.ts"
---

# Frontend Conventions (SvelteKit + Tailwind)

## Svelte 5 Runes Mode

This project uses Svelte 5 runes. NEVER use legacy reactive syntax.

```svelte
<!-- CORRECT -->
let count = $state(0);
let doubled = $derived(count * 2);
$effect(() => { console.log(count); });

<!-- WRONG — do NOT use these -->
$: doubled = count * 2;
export let prop;
```

Use `$state`, `$derived`, `$effect`, `$props()` — not `let`, `$:`, or `export let`.

## Styling

- Tailwind CSS 4 utility classes inline
- No separate CSS files (except `routes/layout.css` for global layout)
- `@tailwindcss/typography` available for prose content

## Project Structure

- `src/lib/api/client.ts` — All backend API calls
- `src/lib/components/` — Reusable components (FilterSelect, DateRangePicker)
- `src/routes/` — SvelteKit file-based routing
  - `+page.svelte` — Page component
  - `+page.ts` — Load function (client-side data fetching)
  - `+layout.svelte` — Layout wrapper

## API Integration

- Backend runs at `http://localhost:8000`
- API client in `src/lib/api/client.ts`
- Fetch in `+page.ts` load functions, not in components

## Dependencies

- Install: `cd frontend && npm install`
- Dev server: `npm run dev`
- Type check: `npm run check`
