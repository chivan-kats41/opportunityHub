/* ══ PRICING ENGINE ══════════════════════════════ */
const UGX_RATE = 3710;

const plans = {
  jobseeker: {
    pro:   { monthly_usd: 5,   yearly_usd: 48,   monthly_ugx: 18500,  yearly_ugx: 178000  },
    elite: { monthly_usd: 12,  yearly_usd: 115,  monthly_ugx: 44500,  yearly_ugx: 427000  },
  },
  employer: {
    starter: { monthly_usd: 19,  yearly_usd: 182,  monthly_ugx: 70000,  yearly_ugx: 672000  },
    growth:  { monthly_usd: 49,  yearly_usd: 470,  monthly_ugx: 182000, yearly_ugx: 1747000 },
    ent:     { monthly_usd: 149, yearly_usd: 1430, monthly_ugx: 553000, yearly_ugx: 5309000 },
  }
};

let currentBilling  = 'monthly';
let currentCurrency = 'ugx';
let currentRole     = 'jobseeker';

function fmtUGX(n) {
  if (n >= 1000000) return 'UGX ' + (n / 1000000).toFixed(1).replace('.0', '') + 'M';
  return 'UGX ' + Math.round(n / 1000) + 'K';
}

function setCard(priceEl, cycleEl, ugxEl, savingEl, plan) {
  if (!plan || !priceEl) return;
  const isYearly = currentBilling === 'yearly';
  const isUSD    = currentCurrency === 'usd';
  const usdAmt   = isYearly ? plan.yearly_usd  : plan.monthly_usd;
  const ugxAmt   = isYearly ? plan.yearly_ugx  : plan.monthly_ugx;
  const cycleStr = isYearly ? 'per year, billed annually' : 'per month, billed monthly';

  if (isUSD) {
    priceEl.innerHTML = '<sup>$</sup>' + usdAmt;
    if (ugxEl) ugxEl.textContent = '≈ ' + fmtUGX(ugxAmt) + (isYearly ? ' / year' : ' / month');
  } else {
    priceEl.innerHTML = fmtUGX(ugxAmt);
    if (ugxEl) ugxEl.textContent = '≈ $' + usdAmt + (isYearly ? ' / year' : ' / month');
  }

  if (cycleEl) cycleEl.textContent = cycleStr;
  if (savingEl) savingEl.style.display = isYearly ? 'inline-block' : 'none';
}

function updatePrices() {
  setCard(
    document.getElementById('js-pro-price'),
    document.getElementById('js-pro-cycle'),
    document.getElementById('js-pro-ugx'),
    document.getElementById('js-pro-saving'),
    plans.jobseeker.pro
  );
  setCard(
    document.getElementById('js-elite-price'),
    document.getElementById('js-elite-cycle'),
    document.getElementById('js-elite-ugx'),
    document.getElementById('js-elite-saving'),
    plans.jobseeker.elite
  );
  setCard(
    document.getElementById('em-starter-price'),
    document.getElementById('em-starter-cycle'),
    document.getElementById('em-starter-ugx'),
    document.getElementById('em-starter-saving'),
    plans.employer.starter
  );
  setCard(
    document.getElementById('em-growth-price'),
    document.getElementById('em-growth-cycle'),
    document.getElementById('em-growth-ugx'),
    document.getElementById('em-growth-saving'),
    plans.employer.growth
  );
  setCard(
    document.getElementById('em-ent-price'),
    document.getElementById('em-ent-cycle'),
    document.getElementById('em-ent-ugx'),
    document.getElementById('em-ent-saving'),
    plans.employer.ent
  );
}

function setBilling(cycle) {
  currentBilling = cycle;
  const btnM = document.getElementById('btn-monthly');
  const btnY = document.getElementById('btn-yearly');
  if (btnM) btnM.classList.toggle('active', cycle === 'monthly');
  if (btnY) btnY.classList.toggle('active',  cycle === 'yearly');
  updatePrices();
}

function setCurrency(cur) {
  currentCurrency = cur;
  const ugx = document.getElementById('cur-ugx');
  const usd = document.getElementById('cur-usd');
  if (ugx) ugx.classList.toggle('active', cur === 'ugx');
  if (usd) usd.classList.toggle('active', cur === 'usd');
  updatePrices();
}

function setRole(role) {
  currentRole = role;
  const tabJS = document.getElementById('tab-jobseeker');
  const tabEM = document.getElementById('tab-employer');
  const plJS  = document.getElementById('plans-jobseeker');
  const plEM  = document.getElementById('plans-employer');
  if (tabJS) tabJS.classList.toggle('active', role === 'jobseeker');
  if (tabEM) tabEM.classList.toggle('active', role === 'employer');
  if (plJS)  plJS.style.display  = role === 'jobseeker' ? '' : 'none';
  if (plEM)  plEM.style.display  = role === 'employer'  ? '' : 'none';
}

// Initialise on DOM ready
document.addEventListener('DOMContentLoaded', updatePrices);