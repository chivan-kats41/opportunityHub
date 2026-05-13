/* ── Filter tabs ── */
document.querySelectorAll('.filter-tab').forEach(tab => {
  tab.addEventListener('click', e => {
    if (tab.getAttribute('href') === '#') {
      e.preventDefault();
      document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
    }
  });
});

/* ── Bookmark toggle ── */
document.querySelectorAll('.btn-save').forEach(btn => {
  btn.addEventListener('click', e => {
    e.preventDefault();
    e.stopPropagation();
    const icon = btn.querySelector('i');
    icon.classList.toggle('bi-bookmark');
    icon.classList.toggle('bi-bookmark-fill');
    btn.style.color = icon.classList.contains('bi-bookmark-fill') ? '#1A6BCC' : '';
    btn.style.borderColor = icon.classList.contains('bi-bookmark-fill') ? '#1A6BCC' : '';
  });
});

/* ── Salary slider ── */
const slider = document.querySelector('.salary-range');
const salaryVal = document.getElementById('salary-val');
if (slider && salaryVal) {
  slider.addEventListener('input', () => {
    const v = parseInt(slider.value);
    salaryVal.textContent = v >= 1000000
      ? 'UGX ' + Math.round(v / 1000000) + 'M'
      : 'UGX ' + Math.round(v / 1000) + 'K';
  });
}

/* ── Auto-dismiss flash messages after 5s ── */
setTimeout(() => {
  document.querySelectorAll('.alert.fade.show').forEach(el => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
    if (bsAlert) bsAlert.close();
  });
}, 5000);