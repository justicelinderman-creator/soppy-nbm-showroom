'use strict';
(() => {
  const get = id => document.getElementById(id);
  const recipient = 'justice.linderman@gmail.com';
  const fields = ['failure', 'issue', 'expected', 'environment', 'deadline'].map(get);
  const subject = get('subject');
  const message = get('message');
  const open = get('open-email');
  const copy = get('copy-email');
  const status = get('status');
  function update() {
    subject.value = 'n8n repair brief — ' + get('failure').value;
    message.value = [
      'Hello Cosie,', '',
      "I'd like to discuss the $200 USD n8n workflow repair pilot.", '',
      'Failure class: ' + get('failure').value, '',
      'Workflow and reproducible failure:', get('issue').value.trim() || '[Describe one reproducible failure]', '',
      'Expected behavior:', get('expected').value.trim() || '[Describe the result you need]', '',
      'Environment: ' + (get('environment').value.trim() || 'To be confirmed'),
      'Preferred timing: ' + (get('deadline').value.trim() || 'Flexible / to be agreed'), '',
      'Please confirm fit, scope, acceptance checks, delivery date, total price and payment/refund terms before any work or payment.'
    ].join('\n');
    open.href = 'mailto:' + recipient + '?subject=' + encodeURIComponent(subject.value) + '&body=' + encodeURIComponent(message.value);
  }
  fields.forEach(field => {
    field.addEventListener('input', () => { field.setCustomValidity(''); update(); });
    field.addEventListener('change', update);
  });
  open.addEventListener('click', event => {
    for (const id of ['issue', 'expected']) {
      const field = get(id);
      field.setCustomValidity(field.value.trim() ? '' : 'Please add this detail to your brief.');
      if (!field.reportValidity()) { event.preventDefault(); return; }
    }
    update();
  });
  copy.addEventListener('click', async () => {
    update();
    const text = 'To: ' + recipient + '\nSubject: ' + subject.value + '\n\n' + message.value;
    try {
      await navigator.clipboard.writeText(text);
      status.textContent = 'Email details copied. Review and send them in your email app.';
    } catch (_) {
      message.focus(); message.select();
      status.textContent = 'Copy is unavailable here. The message is selected; copy it and the subject into your email app.';
    }
  });
  update(); open.hidden = false; copy.hidden = false;
})();
