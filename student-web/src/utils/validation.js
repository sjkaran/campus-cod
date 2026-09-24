// ===== Validation utilities =====
// Pure functions so they're easy to unit test and reuse across forms.
// Every function returns an error string, or '' when the value is valid.

export function required(value, label = 'This field') {
  if (value === null || value === undefined || String(value).trim() === '') {
    return `${label} is required.`;
  }
  return '';
}

export function minLength(value, min, label = 'This field') {
  if (value && value.trim().length < min) {
    return `${label} must be at least ${min} characters.`;
  }
  return '';
}

export function isValidDate(value) {
  if (!value) return false;
  const d = new Date(value);
  return !Number.isNaN(d.getTime());
}

export function combineDateTime(dateStr, timeStr) {
  if (!dateStr || !timeStr) return null;
  const d = new Date(`${dateStr}T${timeStr}`);
  return Number.isNaN(d.getTime()) ? null : d;
}

/**
 * Validates the full gate-pass application form.
 * Returns an object keyed by field name -> error message (empty string if valid).
 */
export function validateGatePassForm(fields) {
  const errors = {};

  errors.destination = required(fields.destination, 'Destination');
  if (!errors.destination) {
    errors.destination = minLength(fields.destination, 3, 'Destination');
  }

  errors.reason = required(fields.reason, 'Reason');
  if (!errors.reason) {
    errors.reason = minLength(fields.reason, 10, 'Reason');
  }

  errors.departureDate = required(fields.departureDate, 'Departure date');
  errors.departureTime = required(fields.departureTime, 'Departure time');
  errors.returnDate = required(fields.returnDate, 'Return date');
  errors.returnTime = required(fields.returnTime, 'Return time');

  const departure = combineDateTime(fields.departureDate, fields.departureTime);
  const returnAt = combineDateTime(fields.returnDate, fields.returnTime);

  if (departure && returnAt && !errors.departureDate && !errors.returnDate) {
    if (returnAt.getTime() <= departure.getTime()) {
      errors.returnDate = 'Return must be after departure.';
    }
    const now = new Date();
    // Allow same-day requests but not departures clearly in the past.
    if (departure.getTime() < now.getTime() - 24 * 60 * 60 * 1000) {
      errors.departureDate = 'Departure date cannot be in the past.';
    }
  }

  const hasErrors = Object.values(errors).some((msg) => msg);
  return { errors, isValid: !hasErrors };
}

export function validateLoginForm(fields) {
  const errors = {};
  errors.username = required(fields.username, 'Student ID');
  errors.password = required(fields.password, 'Password');
  const hasErrors = Object.values(errors).some((msg) => msg);
  return { errors, isValid: !hasErrors };
}
