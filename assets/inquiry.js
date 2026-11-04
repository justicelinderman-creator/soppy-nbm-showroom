/* Copies public contact details only. No submission, tracking or storage. */
(() => {
  'use strict';
  const box = document.getElementById('email-options');
  if (!box) return;
  const status = document.getElementById('inquiry-copy-status');
  box.querySelectorAll('button[data-copy-target]').forEach(button => {
    const field = document.getElementById(button.dataset.copyTarget);
    if (!field || !field.readOnly || !status) return;
    button.hidden = false;
    button.addEventListener('click', async () => {
      const name = button.dataset.copyName;
      try {
        if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(field.value);
        status.textContent = `${name} copied. Paste it into your email. Nothing has been sent.`;
      } catch (_) {
        field.focus();
        field.select();
        status.textContent = `Automatic copying is unavailable. The ${name.toLowerCase()} is selected above; copy it manually. Nothing has been sent.`;
      }
    });
  });
})();
