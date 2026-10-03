const file = document.querySelector('#pdf');
const status = document.querySelector('#status');
const review = document.querySelector('#review');
const editor = document.querySelector('#invoice');
const result = document.querySelector('#result');
const preview = document.querySelector('#preview');

function parsedInvoice() { return JSON.parse(editor.value); }
function showResult(value) { result.textContent = JSON.stringify(value, null, 2); }

document.querySelector('#extract').addEventListener('click', async () => {
  if (!file.files[0]) { status.textContent = 'Izvēlieties PDF failu.'; return; }
  status.textContent = 'Notiek apstrāde…'; result.textContent = '';
  const form = new FormData(); form.append('file', file.files[0]);
  const response = await fetch('/api/invoices/extract', { method: 'POST', body: form });
  const data = await response.json();
  if (!response.ok) { status.textContent = data.detail || 'Apstrāde neizdevās.'; return; }
  editor.value = JSON.stringify(data, null, 2);
  review.classList.remove('hidden');
  const recipientId = data.customer?.endpoint_id;
  const recipientScheme = data.customer?.endpoint_scheme;
  status.textContent = recipientId && recipientScheme
    ? `Izmantots parsers: ${data.extractor}. Saņēmēja Peppol ID kandidāts: ${recipientScheme}:${recipientId}. Pirms nosūtīšanas pārbaudiet to pie saņēmēja vai viņa pakalpojuma sniedzēja.`
    : `Izmantots parsers: ${data.extractor}. Saņēmēja Peppol ID nav atrasts — aizpildiet customer.endpoint_id un customer.endpoint_scheme.`;
  preview.textContent = 'Tiek sagatavots priekšskatījums…';
  const previewForm = new FormData(); previewForm.append('file', file.files[0]);
  const previewResponse = await fetch('/api/invoices/preview', { method: 'POST', body: previewForm });
  const previewData = await previewResponse.json();
  if (!previewResponse.ok) { preview.textContent = previewData.detail || 'Priekšskatījumu nevarēja izveidot.'; return; }
  preview.replaceChildren(...previewData.pages.map((source, index) => {
    const image = document.createElement('img');
    image.src = source; image.alt = `Rēķina lapa ${index + 1}`; image.className = 'pdf-page';
    return image;
  }));
  if (previewData.truncated) preview.insertAdjacentText('beforeend', 'Tiek parādītas pirmās 10 lapas.');
});

document.querySelector('#validate').addEventListener('click', async () => {
  try {
    const response = await fetch('/api/invoices/validate', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(parsedInvoice())});
    showResult(await response.json());
  } catch { result.textContent = 'JSON formāts nav derīgs.'; }
});

document.querySelector('#xml').addEventListener('click', async () => {
  try {
    if (!file.files[0]) { result.textContent = 'Vispirms augšupielādējiet PDF failu.'; return; }
    const form = new FormData();
    form.append('invoice_json', JSON.stringify(parsedInvoice()));
    form.append('file', file.files[0]);
    const response = await fetch('/api/invoices/xml-with-pdf', {method:'POST', body:form});
    if (!response.ok) { showResult(await response.json()); return; }
    const blob = await response.blob(); const link = document.createElement('a');
    link.href = URL.createObjectURL(blob); link.download = 'e-rekins.xml'; link.click(); URL.revokeObjectURL(link.href);
    result.textContent = 'XML ar iekļautu oriģinālo PDF ir izveidots un lejupielādēts.';
  } catch { result.textContent = 'JSON formāts nav derīgs.'; }
});
