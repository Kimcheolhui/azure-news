<script lang="ts">
	import { page } from '$app/state';
	import { getUpdate, getReport, type UpdateDetail, type ReportDetail } from '$lib/api/client';
	import { marked } from 'marked';

	let update: UpdateDetail | null = $state(null);
	let report: ReportDetail | null = $state(null);
	let loading = $state(true);
	let error = $state('');
	let lang: 'ko' | 'en' = $state('ko');

	let renderedBody = $derived.by(() => {
		const raw = lang === 'ko' ? report?.body_ko : report?.body_en;
		if (!raw) return '';
		return marked.parse(raw, { async: false }) as string;
	});

	const id = $derived(page.params.id!);

	async function loadData() {
		loading = true;
		error = '';
		try {
			update = await getUpdate(id);
			if (update.report) {
				report = await getReport(update.report.id);
			}
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to load data';
		} finally {
			loading = false;
		}
	}

	function formatDate(dateStr: string | null): string {
		if (!dateStr) return '-';
		return new Date(dateStr).toLocaleDateString('ko-KR', {
			year: 'numeric',
			month: 'long',
			day: 'numeric'
		});
	}

	function typeLabel(type: string): string {
		const labels: Record<string, string> = {
			new_feature: '🆕 New Feature',
			retirement: '🔴 Retirement',
			preview: '🔵 Preview',
			ga: '🟢 GA',
			update: '🔄 Update',
			security: '🔒 Security',
			pricing: '💰 Pricing',
			deprecation: '⚠️ Deprecation',
			guide: '📖 Guide',
			case_study: '💡 Case Study',
			announcement: '📢 Announcement',
			event: '🎪 Event'
		};
		return labels[type] ?? type;
	}

	function typeBadgeClass(type: string): string {
		const classes: Record<string, string> = {
			new_feature: 'bg-emerald-100 text-emerald-800',
			retirement: 'bg-red-100 text-red-800',
			preview: 'bg-blue-100 text-blue-800',
			ga: 'bg-green-100 text-green-800',
			update: 'bg-amber-100 text-amber-800',
			security: 'bg-purple-100 text-purple-800',
			pricing: 'bg-orange-100 text-orange-800',
			deprecation: 'bg-rose-100 text-rose-800',
			guide: 'bg-cyan-100 text-cyan-800',
			case_study: 'bg-teal-100 text-teal-800',
			announcement: 'bg-indigo-100 text-indigo-800',
			event: 'bg-pink-100 text-pink-800'
		};
		return classes[type] ?? 'bg-gray-100 text-gray-800';
	}

	function categoryLabel(s: string): string {
		const labels: Record<string, string> = {
			compute: 'Compute', database: 'Database', ai_ml: 'AI/ML',
			networking: 'Networking', storage: 'Storage', security: 'Security',
			devtools: 'DevTools', analytics: 'Analytics', integration: 'Integration',
			management: 'Management', iot: 'IoT', mixed_reality: 'Mixed Reality', other: 'Other'
		};
		return labels[s] ?? s;
	}

	function statusLabel(status: string): string {
		const labels: Record<string, string> = {
			completed: '✅ 완료',
			pending: '⏳ 대기',
			failed: '❌ 실패',
			in_progress: '🔄 진행 중'
		};
		return labels[status] ?? status;
	}

	$effect(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>{update?.title ?? 'Loading...'} — Azure News</title>
</svelte:head>

{#if loading}
	<div class="flex justify-center py-16">
		<div class="h-8 w-8 animate-spin rounded-full border-4 border-[var(--color-primary)] border-t-transparent"></div>
	</div>
{:else if error}
	<div class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
		{error}
	</div>
{:else if update}
	<!-- Back link -->
	<a href="/" class="inline-flex items-center gap-1.5 text-sm text-[var(--color-text-muted)] hover:text-[var(--color-primary)] mb-6 transition-colors">
		<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
		목록으로 돌아가기
	</a>

	<!-- Update header -->
	<div class="rounded-xl bg-[var(--color-surface)] p-8 mb-6" style="box-shadow: 0 1px 6px rgba(0,0,0,0.1);">
		<!-- Type badges -->
		{#if update.update_type && update.update_type.length > 0}
			<div class="flex flex-wrap gap-2 mb-4">
				{#each update.update_type as type}
					<span class="rounded-full px-3 py-1 text-xs font-semibold {typeBadgeClass(type)}">
						{typeLabel(type)}
					</span>
				{/each}
			</div>
		{/if}

		<h1 class="text-2xl font-bold text-[var(--color-text)] leading-tight">{update.title_ko || update.title}</h1>
		{#if update.title_ko}
			<p class="mt-2 text-sm text-[var(--color-text-muted)]">{update.title}</p>
		{/if}

		{#if update.summary_ko || update.summary}
			<p class="mt-4 text-[var(--color-text-muted)] leading-relaxed">{update.summary_ko || update.summary}</p>
		{/if}

		<!-- Meta info -->
		<div class="mt-6 flex flex-wrap items-center gap-x-6 gap-y-2 pt-5 border-t border-[var(--color-border)]">
			<div class="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
				{formatDate(update.published_date)}
			</div>
			{#if update.categories && update.categories.length > 0}
				<div class="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a4 4 0 014-4z"/></svg>
					{update.categories.map(c => categoryLabel(c)).join(', ')}
				</div>
			{/if}
			{#if update.source_url}
				<a href={update.source_url} target="_blank" rel="noopener"
					class="flex items-center gap-1.5 text-sm text-[var(--color-primary)] hover:underline ml-auto">
					원문 보기
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
				</a>
			{/if}
		</div>
	</div>

	<!-- Services affected -->
	{#if update.services_affected && update.services_affected.length > 0}
		<div class="mb-6">
			<h3 class="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)] mb-3">영향 받는 서비스</h3>
			<div class="flex flex-wrap gap-2">
				{#each update.services_affected as service}
					<span class="rounded-lg bg-blue-50 px-3 py-1.5 text-sm font-medium text-blue-700"
						style="box-shadow: 0 1px 3px rgba(0,0,0,0.06);">
						{service}
					</span>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Report section -->
	{#if report}
		<!-- Language toggle -->
		<div class="flex items-center gap-2 mb-4">
			<h3 class="text-xs font-semibold uppercase tracking-wider text-[var(--color-text-muted)] mr-2">분석 리포트</h3>
			<button
				onclick={() => lang = 'ko'}
				class="rounded-lg px-4 py-2 text-sm font-medium transition-colors
					{lang === 'ko' ? 'bg-[var(--color-primary)] text-white' : 'text-[var(--color-text-muted)] hover:bg-gray-100'}"
				style={lang === 'ko' ? 'box-shadow: 0 1px 4px rgba(0,120,212,0.3);' : ''}
			>
				🇰🇷 한국어
			</button>
			<button
				onclick={() => lang = 'en'}
				class="rounded-lg px-4 py-2 text-sm font-medium transition-colors
					{lang === 'en' ? 'bg-[var(--color-primary)] text-white' : 'text-[var(--color-text-muted)] hover:bg-gray-100'}"
				style={lang === 'en' ? 'box-shadow: 0 1px 4px rgba(0,120,212,0.3);' : ''}
			>
				🇺🇸 English
			</button>
			<span class="ml-auto text-xs text-[var(--color-text-muted)]">
				{statusLabel(report.status)}
				{#if report.model_used}
					· {report.model_used}
				{/if}
			</span>
		</div>

		<!-- Report content -->
		<div class="rounded-xl bg-[var(--color-surface)] p-8" style="box-shadow: 0 1px 6px rgba(0,0,0,0.1);">
			<h2 class="text-xl font-bold text-[var(--color-text)] mb-3">
				{lang === 'ko' ? report.title_ko : report.title_en}
			</h2>
			<p class="text-[var(--color-text-muted)] mb-6 text-sm leading-relaxed">
				{lang === 'ko' ? report.summary_ko : report.summary_en}
			</p>

			{#if report.affected_services && Array.isArray(report.affected_services) && report.affected_services.length > 0}
				<div class="mb-6 flex flex-wrap gap-2">
					{#each report.affected_services as service}
						<span class="rounded-lg bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
							{service}
						</span>
					{/each}
				</div>
			{/if}

			<div class="prose prose-sm max-w-none text-[var(--color-text)] leading-relaxed">
				{@html renderedBody}
			</div>
		</div>

	{:else}
		<div class="rounded-xl bg-amber-50 p-6 text-sm text-amber-700" style="box-shadow: 0 1px 4px rgba(0,0,0,0.06);">
			이 업데이트에 대한 분석 리포트가 아직 생성되지 않았습니다.
		</div>
	{/if}
{/if}