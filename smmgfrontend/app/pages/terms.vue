<script setup lang="ts">
useSeoMeta({
  title: 'Terms of Service | SMMG Healthcare',
  description: 'Terms for using SMMG accounts, appointment scheduling, and general AI health and first-aid information.',
})

const sections = [
  ['using', 'Using SMMG'], ['accounts', 'Accounts'], ['appointments', 'Appointments'], ['healthcare', 'Healthcare disclaimer'],
  ['ai', 'AI assistant'], ['acceptable-use', 'Acceptable use'], ['availability', 'Service availability'], ['limits', 'Reasonable limitations'], ['changes', 'Changes'],
]
</script>

<template>
  <div class="bg-white">
    <CommonLegalPageIntro eyebrow="Terms" title="Terms of Service" description="These project-level terms set practical expectations for using SMMG. They are provided for clarity and are not presented as lawyer-reviewed legal advice." />
    <div class="mx-auto grid max-w-6xl gap-12 px-4 py-12 sm:px-6 lg:grid-cols-[220px_minmax(0,1fr)] lg:px-8 lg:py-16">
      <aside class="lg:sticky lg:top-28 lg:self-start"><h2 class="text-sm font-semibold text-gray-900">On this page</h2><nav class="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm lg:flex-col" aria-label="Terms contents"><a v-for="section in sections" :key="section[0]" :href="`#${section[0]}`" class="rounded text-gray-600 hover:text-primary-700">{{ section[1] }}</a></nav></aside>
      <article class="legal-content max-w-3xl">
        <section id="using"><h2>Using SMMG</h2><p>SMMG is an appointment management application with public doctor and service directories and a general health-information assistant. By using it, you agree to provide accurate information, follow the appointment rules shown in the application, and use the service lawfully and respectfully.</p></section>
        <section id="accounts"><h2>User accounts and responsibility</h2><p>You are responsible for the accuracy of your account information, protecting your password, and activity performed through your account. Do not share credentials or attempt to access another user’s account. Some features require a verified, authenticated account and are available according to the role assigned in SMMG.</p></section>
        <section id="appointments"><h2>Appointment scheduling</h2><p>An appointment request depends on the doctor schedules and services currently available in the application. Availability may change, and SMMG does not guarantee that a particular doctor, service, date, or time will remain available.</p><p>Use the appointment controls provided in your account to review, cancel, or reschedule when those actions are permitted. Appointment status and schedule constraints shown in SMMG apply to those changes. Contact the relevant healthcare provider through established channels if a time-sensitive scheduling issue cannot be handled in the application.</p></section>
        <section id="healthcare"><h2>Healthcare and emergency disclaimer</h2><div class="notice"><LucideTriangleAlert class="mt-0.5 h-5 w-5 shrink-0 text-amber-700" /><p>SMMG manages appointments and provides general informational tools. It does not provide emergency medical services, replace licensed healthcare professionals, or guarantee any medical outcome.</p></div><p>Information shown in SMMG should not be treated as a medical diagnosis, prescription, or individualized treatment plan. For medical decisions, consult an appropriate licensed professional. In an emergency or potentially life-threatening situation, contact the appropriate emergency medical services immediately rather than relying on SMMG.</p></section>
        <section id="ai"><h2>AI Health & First-Aid Assistant</h2><p>The AI assistant can provide general health information and basic first-aid guidance. It does not diagnose conditions, prescribe treatment or medication, or replace professional medical care. AI-generated responses may be incomplete, inaccurate, or unsuitable for your circumstances; use appropriate judgment and seek professional help when needed.</p></section>
        <section id="acceptable-use"><h2>Acceptable use</h2><p>Do not misuse SMMG, interfere with its operation, submit unlawful or harmful content, impersonate another person, probe for security weaknesses, automate abusive traffic, or use appointment functions fraudulently. Access may be suspended or deactivated where application controls allow when an account is misused or creates a risk to the service or other users.</p></section>
        <section id="availability"><h2>Service availability</h2><p>SMMG may occasionally be unavailable because of maintenance, technical problems, provider outages, or changes to the project. Features, listed doctors, services, and schedules may be updated over time. Continuous or error-free availability is not guaranteed.</p></section>
        <section id="limits"><h2>Reasonable limitations</h2><p>Use of SMMG is at your discretion. To the extent reasonably applicable, SMMG is not responsible for decisions made solely from general informational content, missed care caused by information entered incorrectly by a user, or interruptions outside the application’s reasonable control. Nothing in these terms is intended to misrepresent the responsibilities of healthcare professionals providing care.</p></section>
        <section id="changes"><h2>Changes to these terms</h2><p>These terms may be updated when SMMG features or operating practices change. The “Last updated” date identifies the terms currently displayed by the application. Continuing to use the service after an update means the revised terms apply to future use.</p></section>
      </article>
    </div>
  </div>
</template>
