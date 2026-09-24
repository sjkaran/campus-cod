import { h, mount, clear } from './utils/dom.js';
import { ROUTES } from './utils/constants.js';
import { getSession, logoutStudent, isAuthenticated } from './services/authService.js';
import { getCurrentStudent } from './services/studentService.js';
import { Sidebar } from './components/Sidebar.js';
import { Navbar } from './components/Navbar.js';
import { LoginPage } from './pages/Login.js';
import { DashboardPage } from './pages/Dashboard.js';
import { NotificationsPage } from './pages/Notifications.js';
import { AttendancePage } from './pages/Attendance.js';
import { GatePassPage } from './pages/GatePass.js';
import { GatePassDetailsPage } from './pages/GatePassDetails.js';
import { ProfilePage } from './pages/Profile.js';
import { openModal } from './components/Modal.js';
import { showToast } from './components/Toast.js';

const PAGE_TITLES = {
  [ROUTES.DASHBOARD]: 'Dashboard',
  [ROUTES.NOTIFICATIONS]: 'Notifications',
  [ROUTES.ATTENDANCE]: 'Attendance',
  [ROUTES.GATEPASS]: 'Gate Pass',
  [ROUTES.GATEPASS_DETAILS]: 'Gate Pass Details',
  [ROUTES.PROFILE]: 'Profile',
};

const appRoot = document.getElementById('app-root');

const state = {
  student: null,
  route: ROUTES.DASHBOARD,
  routeParam: null,
  sidebarOpen: false,
};

function parseHash() {
  const raw = window.location.hash.replace('#/', '') || ROUTES.DASHBOARD;
  const [route, param] = raw.split('/');
  return { route: route || ROUTES.DASHBOARD, param };
}

function navigate(route, param) {
  window.location.hash = param ? `#/${route}/${param}` : `#/${route}`;
}

window.addEventListener('hashchange', () => {
  const { route, param } = parseHash();
  state.route = route;
  state.routeParam = param;
  state.sidebarOpen = false;
  renderApp();
});

async function boot() {
  if (!isAuthenticated()) {
    renderLogin();
    return;
  }
  await loadStudentAndRenderApp();
}

function renderLogin() {
  mount(appRoot, LoginPage(async () => {
    await loadStudentAndRenderApp();
  }));
}

async function loadStudentAndRenderApp() {
  mount(appRoot, h('div', { class: 'boot-loading' }, h('div', { class: 'spinner' })));
  try {
    state.student = await getCurrentStudent();
  } catch {
    state.student = null;
  }
  const { route, param } = parseHash();
  state.route = route;
  state.routeParam = param;
  renderApp();
}

function handleLogout() {
  openModal({
    title: 'Log out',
    body: 'Are you sure you want to log out of Smart Campus?',
    actions: [
      { label: 'Cancel', variant: 'secondary', onClick: (close) => close() },
      {
        label: 'Log out',
        variant: 'primary',
        onClick: (close) => {
          close();
          logoutStudent();
          state.student = null;
          window.location.hash = `#/${ROUTES.LOGIN}`;
          renderLogin();
        },
      },
    ],
  });
}

function renderPageContent() {
  switch (state.route) {
    case ROUTES.NOTIFICATIONS:
      return NotificationsPage();
    case ROUTES.ATTENDANCE:
      return AttendancePage();
    case ROUTES.GATEPASS:
      return GatePassPage((id) => navigate(ROUTES.GATEPASS_DETAILS, id));
    case ROUTES.GATEPASS_DETAILS:
      return GatePassDetailsPage(state.routeParam, state.student, () => navigate(ROUTES.GATEPASS));
    case ROUTES.PROFILE:
      return ProfilePage(state.student);
    case ROUTES.DASHBOARD:
    default:
      return DashboardPage(state.student, navigate);
  }
}

function renderApp() {
  if (!state.student) {
    mount(appRoot, h('div', { class: 'boot-loading' }, h('div', { class: 'spinner' })));
    return;
  }

  const shell = h('div', { class: `app-shell ${state.sidebarOpen ? 'app-shell--sidebar-open' : ''}` });
  const overlay = h('div', { class: 'sidebar-overlay', onClick: () => { state.sidebarOpen = false; refreshShellClass(); } });
  const sidebar = Sidebar(state.route, (route) => { navigate(route); }, handleLogout);
  const main = h('main', { class: 'main-column' }, [
    Navbar({
      pageTitle: PAGE_TITLES[state.route] || 'Smart Campus',
      student: state.student,
      onMenuToggle: () => { state.sidebarOpen = !state.sidebarOpen; refreshShellClass(); },
    }),
    h('div', { class: 'main-content' }, renderPageContent()),
  ]);

  shell.append(overlay, sidebar, main);
  mount(appRoot, shell);

  function refreshShellClass() {
    shell.classList.toggle('app-shell--sidebar-open', state.sidebarOpen);
  }
}

boot();

// Expose a tiny debug hook for the toast system used by pages.
window.__scShowToast = showToast;
