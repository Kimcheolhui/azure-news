<script lang="ts">
	import flatpickr from 'flatpickr';
	import { Korean } from 'flatpickr/dist/l10n/ko.js';
	import 'flatpickr/dist/flatpickr.min.css';
	import { onMount } from 'svelte';

	interface Props {
		dateFrom: string;
		dateTo: string;
		onchange: (from: string, to: string) => void;
	}

	let { dateFrom, dateTo, onchange }: Props = $props();

	let inputEl: HTMLInputElement;
	let fp: flatpickr.Instance;
	let selectedMonth = $state('');

	function buildMonthOptions() {
		const now = new Date();
		const options: { label: string; from: string; to: string }[] = [];
		for (let i = 0; i < 12; i++) {
			const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
			const year = d.getFullYear();
			const month = d.getMonth();
			const from = `${year}-${String(month + 1).padStart(2, '0')}-01`;
			const lastDay = new Date(year, month + 1, 0).getDate();
			const to = `${year}-${String(month + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
			const label = `${year}년 ${month + 1}월`;
			options.push({ label, from, to });
		}
		return options;
	}

	const monthOptions = buildMonthOptions();

	function handleMonthSelect(e: Event) {
		const value = (e.target as HTMLSelectElement).value;
		if (!value) {
			fp?.clear();
			onchange('', '');
			return;
		}
		const opt = monthOptions.find((o) => o.from === value);
		if (opt) {
			fp?.setDate([opt.from, opt.to], true);
			onchange(opt.from, opt.to);
		}
	}

	function fmt(d: Date): string {
		const y = d.getFullYear();
		const m = String(d.getMonth() + 1).padStart(2, '0');
		const day = String(d.getDate()).padStart(2, '0');
		return `${y}-${m}-${day}`;
	}

	onMount(() => {
		fp = flatpickr(inputEl, {
			mode: 'range',
			locale: Korean,
			dateFormat: 'Y-m-d',
			allowInput: true,
			defaultDate: dateFrom && dateTo ? [dateFrom, dateTo] : undefined,
			onChange(selectedDates) {
				if (selectedDates.length === 2) {
					const from = fmt(selectedDates[0]);
					const to = fmt(selectedDates[1]);
					onchange(from, to);
					// Check if this matches a month option
					const match = monthOptions.find((o) => o.from === from && o.to === to);
					selectedMonth = match ? match.from : '';
				} else if (selectedDates.length === 0) {
					onchange('', '');
					selectedMonth = '';
				}
			}
		});

		return () => fp?.destroy();
	});

	export function clear() {
		fp?.clear();
		selectedMonth = '';
	}
</script>

<div class="flex items-center gap-1.5">
	<select
		bind:value={selectedMonth}
		onchange={handleMonthSelect}
		class="rounded-lg border border-[var(--color-border)] px-2 py-2 text-sm bg-white
			focus:border-[var(--color-primary)] focus:outline-none w-[120px]"
	>
		<option value="">월 선택</option>
		{#each monthOptions as opt}
			<option value={opt.from}>{opt.label}</option>
		{/each}
	</select>
	<input
		bind:this={inputEl}
		type="text"
		placeholder="날짜 범위"
		readonly
		class="rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm bg-white cursor-pointer
			focus:border-[var(--color-primary)] focus:outline-none w-[200px]"
	/>
</div>

<style>
	:global(.flatpickr-calendar) {
		font-size: 13px;
	}
</style>
