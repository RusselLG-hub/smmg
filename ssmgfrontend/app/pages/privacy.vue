<script setup lang="ts">
useSeoMeta({
  title: 'Privacy Policy | SSMG Healthcare',
  description: 'Learn what information SSMG handles when you use accounts, appointments, uploads, email features, and the AI assistant.',
})

const sections = [
  ['information', 'Information we handle'], ['use', 'How information is used'], ['storage', 'Storage and service providers'],
  ['ai', 'AI assistant data'], ['choices', 'Your choices'], ['retention', 'Retention and security'], ['changes', 'Changes to this policy'],
]
</script>

<template>
  <div class="bg-white">
    <CommonLegalPageIntro eyebrow="Privacy" title="Privacy Policy" description="This policy explains, in plain language, the information SSMG handles and why it is needed to provide appointment and health-information features." />
    <div class="mx-auto grid max-w-6xl gap-12 px-4 py-12 sm:px-6 lg:grid-cols-[220px_minmax(0,1fr)] lg:px-8 lg:py-16">
      <aside class="lg:sticky lg:top-28 lg:self-start">
        <h2 class="text-sm font-semibold text-gray-900">On this page</h2>
        <nav class="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-sm lg:flex-col" aria-label="Privacy policy contents">
          <a v-for="section in sections" :key="section[0]" :href="`#${section[0]}`" class="rounded text-gray-600 hover:text-primary-700">{{ section[1] }}</a>
        </nav>
      </aside>

      <article class="legal-content max-w-3xl">
        <section id="information"><h2>Information we handle</h2><p>SSMG handles information you provide when creating and using an account, including your name, email address, account role, and authentication-related records such as email verification status. Patient profiles may contain contact and profile information needed for the application.</p><p>When you schedule care, SSMG stores appointment details such as the selected doctor, service, date, time, status, and information needed to manage that appointment. Profile images you choose to upload are also handled by the application.</p><p>If you use the AI Health & First-Aid Assistant, your messages and conversation history may be stored so the conversation can function and be shown in the application.</p></section>
        <section id="use"><h2>How information is used</h2><p>Information is used to create and secure accounts, verify email addresses, show doctor and service information, schedule and manage appointments, display relevant dashboards, and operate the AI assistant. SSMG may send transactional emails for email verification and appointment-related updates. It does not describe promotional marketing features.</p></section>
        <section id="storage"><h2>Storage and service providers</h2><p>Application and appointment records are stored in the configured PostgreSQL database. Uploaded files, including profile images, may be stored in the configured MinIO object storage service.</p><p>SSMG also relies on external providers to deliver specific functions. The configured email provider processes the information needed to send verification and transactional appointment emails. These providers handle data according to their own terms and privacy practices.</p></section>
        <section id="ai"><h2>AI assistant data</h2><p>Messages submitted to the AI assistant may be sent to the configured external AI provider so it can generate a response. Avoid including information that is not needed for your question.</p><div class="notice"><LucideInfo class="mt-0.5 h-5 w-5 shrink-0 text-primary-700" /><p>The assistant provides general health information and basic first-aid guidance. Its conversations are not used by SSMG to diagnose you, and its responses do not replace care from a licensed healthcare professional.</p></div></section>
        <section id="choices"><h2>Your choices</h2><p>You can choose whether to upload a profile image or use the AI assistant. You are responsible for keeping account details accurate and for deciding what information to include in free-text messages. Account changes or deactivation may be available based on your role and the controls provided in the application.</p></section>
        <section id="retention"><h2>Retention and security</h2><p>SSMG retains information as needed to provide its account, appointment, and conversation-history features. Reasonable application safeguards are used, but no online service or storage system can guarantee absolute security. Do not share your password, and sign out when using a shared device.</p></section>
        <section id="changes"><h2>Changes to this policy</h2><p>This policy may be updated when SSMG features or data practices change. The “Last updated” date at the top indicates the current version presented in the application.</p></section>
      </article>
    </div>
  </div>
</template>
