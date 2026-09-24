import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { loginStudent } from '../services/authService.js';
import { validateLoginForm } from '../utils/validation.js';
import { MOCK_CREDENTIALS } from '../mock/students.js';

/**
 * @param {(session:Object)=>void} onLoginSuccess
 */
export function LoginPage(onLoginSuccess) {
  const state = { username: '', password: '', showPassword: false, loading: false, errors: {}, formError: '' };

  const root = h('div', { class: 'auth-screen' });

  function render() {
    const passwordFieldType = state.showPassword ? 'text' : 'password';

    const form = h('form', { class: 'auth-card', onSubmit: handleSubmit }, [
      h('div', { class: 'auth-card__brand' }, [
        h('span', { class: 'auth-card__brand-mark' }, 'SC'),
        h('div', {}, [
          h('p', { class: 'auth-card__brand-name' }, 'Smart Campus'),
          h('p', { class: 'auth-card__brand-sub' }, 'Student Portal'),
        ]),
      ]),
      h('h1', { class: 'auth-card__title' }, 'Welcome back'),
      h('p', { class: 'auth-card__subtitle' }, 'Sign in with your Student ID to continue.'),

      state.formError ? h('div', { class: 'form-alert' }, [icon('warning', { size: 16 }), state.formError]) : null,

      h('div', { class: 'field' }, [
        h('label', { for: 'username', class: 'field-label' }, 'Student ID'),
        h('input', {
          id: 'username', class: `field-input ${state.errors.username ? 'field-input--error' : ''}`,
          type: 'text', placeholder: 'e.g. STU-2026-001', value: state.username, autocomplete: 'username',
          onInput: (e) => { state.username = e.target.value; },
        }),
        state.errors.username ? h('span', { class: 'field-error' }, state.errors.username) : null,
      ]),

      h('div', { class: 'field' }, [
        h('label', { for: 'password', class: 'field-label' }, 'Password'),
        h('div', { class: 'field-input-group' }, [
          h('input', {
            id: 'password', class: `field-input ${state.errors.password ? 'field-input--error' : ''}`,
            type: passwordFieldType, placeholder: 'Enter your password', value: state.password, autocomplete: 'current-password',
            onInput: (e) => { state.password = e.target.value; },
          }),
          h('button', {
            type: 'button', class: 'field-input-group__toggle', 'aria-label': 'Toggle password visibility',
            onClick: () => { state.showPassword = !state.showPassword; render(); },
          }, icon(state.showPassword ? 'eyeOff' : 'eye', { size: 18 })),
        ]),
        state.errors.password ? h('span', { class: 'field-error' }, state.errors.password) : null,
      ]),

      h('button', { class: 'btn btn--primary btn--block', type: 'submit', disabled: state.loading }, [
        state.loading ? h('span', { class: 'spinner spinner--small' }) : null,
        state.loading ? 'Signing in…' : 'Sign in',
      ]),

      h('p', { class: 'auth-card__hint' }, [
        'Demo credentials — Student ID: ',
        h('code', {}, MOCK_CREDENTIALS.username),
        ', Password: ',
        h('code', {}, MOCK_CREDENTIALS.password),
      ]),
    ]);

    root.replaceChildren(
      h('div', { class: 'auth-screen__aside' }, [
        h('div', { class: 'auth-screen__aside-inner' }, [
          h('p', { class: 'auth-screen__eyebrow-free' }, 'Smart Campus Management System'),
          h('h2', { class: 'auth-screen__headline' }, 'One portal for attendance, notices, and campus movement.'),
          h('p', { class: 'auth-screen__copy' }, 'Check your attendance, catch up on campus notices, and request gate passes — all from one place.'),
        ]),
      ]),
      form,
    );
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const { errors, isValid } = validateLoginForm(state);
    state.errors = errors;
    state.formError = '';
    if (!isValid) { render(); return; }

    state.loading = true;
    render();
    try {
      const session = await loginStudent(state.username, state.password);
      onLoginSuccess(session);
    } catch (err) {
      state.formError = err.message || 'Unable to sign in. Please try again.';
      state.loading = false;
      render();
    }
  }

  render();
  return root;
}
