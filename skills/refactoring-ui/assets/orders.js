// Local sample data. Reloading restores these values.
const orders = [
  { id: 1048, customer: 'Harbor Supply', status: 'Packing', total: 248.50 },
  { id: 1047, customer: 'Mora Studio', status: 'Queued', total: 86 },
  { id: 1046, customer: 'Northline Goods', status: 'Shipped', total: 412 },
  { id: 1045, customer: 'Field Notes Co.', status: 'Packing', total: 134.25 },
  { id: 1044, customer: 'Alder Workshop', status: 'Shipped', total: 59.90 },
  { id: 1043, customer: 'Juniper Market', status: 'Queued', total: 173 },
];

const currency = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });
const filters = document.querySelector('#filters');
const search = document.querySelector('#search');
const statusFilter = document.querySelector('#status-filter');
const tableBlock = document.querySelector('#table-block');
const rows = document.querySelector('#order-rows');
const rowTemplate = document.querySelector('#order-row');
const resultCount = document.querySelector('#result-count');
const emptyResults = document.querySelector('#empty-results');

const editor = document.querySelector('#order-form');
const editorTitle = document.querySelector('#editor-title');
const customer = document.querySelector('#customer');
const status = document.querySelector('#order-status');
const total = document.querySelector('#order-total');
const review = document.querySelector('#review-order');
const saveResult = document.querySelector('#save-result');
const dialog = document.querySelector('#confirm-order');
const confirmTitle = document.querySelector('#confirm-title');
const confirmDescription = document.querySelector('#confirm-description');

let selectedId;
let pendingOrder;

function renderOrders() {
  const query = search.value.trim().toLowerCase();
  const matchingOrders = orders.filter((order) => (
    (!statusFilter.value || order.status === statusFilter.value)
    && `#${order.id} ${order.customer}`.toLowerCase().includes(query)
  ));

  const content = document.createDocumentFragment();
  for (const order of matchingOrders) {
    const row = rowTemplate.content.cloneNode(true);
    row.querySelector('[data-order]').textContent = `#${order.id}`;
    row.querySelector('[data-customer]').textContent = order.customer;
    const badge = row.querySelector('[data-status]');
    badge.dataset.status = order.status;
    badge.textContent = order.status;
    row.querySelector('[data-total]').textContent = currency.format(order.total);

    const edit = row.querySelector('button');
    edit.setAttribute('aria-label', `Edit order #${order.id}`);
    edit.addEventListener('click', () => openEditor(order, true));
    content.append(row);
  }

  rows.replaceChildren(content);
  tableBlock.hidden = matchingOrders.length === 0;
  emptyResults.hidden = matchingOrders.length !== 0;
  resultCount.textContent = `${matchingOrders.length} of ${orders.length} orders`;
}

function setFieldError(field, visible) {
  const message = document.getElementById(field.getAttribute('aria-describedby'));
  message.hidden = !visible;
  if (visible) field.setAttribute('aria-invalid', 'true');
  else field.removeAttribute('aria-invalid');
}

function openEditor(order, moveFocus = false) {
  selectedId = order?.id;
  editorTitle.textContent = order ? `Edit order #${order.id}` : 'New order';
  customer.value = order?.customer ?? '';
  status.value = order?.status ?? 'Queued';
  total.value = order ? order.total.toFixed(2) : '';
  saveResult.textContent = '';
  setFieldError(customer, false);
  setFieldError(total, false);
  if (moveFocus) customer.focus();
}

filters.addEventListener('submit', (event) => event.preventDefault());
search.addEventListener('input', renderOrders);
statusFilter.addEventListener('change', renderOrders);
document.querySelector('#clear-filters').addEventListener('click', () => {
  filters.reset();
  search.focus();
  renderOrders();
});
document.querySelector('#new-order').addEventListener('click', () => openEditor(null, true));

for (const field of [customer, total]) {
  field.addEventListener('invalid', () => setFieldError(field, true));
  field.addEventListener('input', () => {
    if (field.validity.valid) setFieldError(field, false);
  });
}

editor.addEventListener('submit', (event) => {
  event.preventDefault();
  // Capture the draft before making the background form inert.
  pendingOrder = {
    id: selectedId ?? orders[0].id + 1,
    customer: customer.value.trim(),
    status: status.value,
    total: total.valueAsNumber,
  };
  confirmTitle.textContent = selectedId ? 'Save order changes?' : 'Create this order?';
  confirmDescription.textContent =
    `Order #${pendingOrder.id} · ${pendingOrder.customer} · ${pendingOrder.status} · ${currency.format(pendingOrder.total)}`;

  // Pointer clicks may leave focus elsewhere. Give showModal() a stable return target.
  review.focus();
  dialog.showModal();
});

dialog.querySelector('form').addEventListener('submit', (event) => {
  if (event.submitter?.value !== 'confirm' || !pendingOrder) return;

  // Handle confirmation before a queued close event could mix two openings.
  // Cancel uses the form's default behavior. Escape closes without submitting.
  event.preventDefault();
  const order = pendingOrder;
  pendingOrder = undefined;
  dialog.close();

  const existing = orders.find((item) => item.id === order.id);
  if (existing) Object.assign(existing, order);
  else orders.unshift(order);

  openEditor(order);
  renderOrders();
  saveResult.textContent = `Order #${order.id} saved.`;
});

const themeToggle = document.querySelector('#dark-theme');
const systemTheme = matchMedia('(prefers-color-scheme: dark)');
themeToggle.checked = systemTheme.matches;
systemTheme.addEventListener('change', (event) => {
  if (!document.documentElement.dataset.theme) themeToggle.checked = event.matches;
});
themeToggle.addEventListener('change', () => {
  document.documentElement.dataset.theme = themeToggle.checked ? 'dark' : 'light';
});

openEditor(orders[0]);
renderOrders();
