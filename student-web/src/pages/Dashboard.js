import { h } from '../utils/dom.js';
import { icon } from '../utils/icons.js';
import { greetingForNow } from '../utils/formatting.js';
import { ROUTES } from '../utils/constants.js';
import { getAttendanceSummary } from '../services/attendanceService.js';
import { getGatePassSummaryCounts } from '../services/gatePassService.js';
import { getNotifications, markNotificationAsRead } from '../services/notificationService.js';
import { StatCard } from '../components/StatCard.js';
import { ProgressRing } from '../components/ProgressRing.js';
import { NotificationCard } from '../components/NotificationCard.js';
import { LoadingState, ErrorState, EmptyState } from '../components/DataState.js';

/**
 * @param {import('../models/models.js').Student} student
 * @param {(route:string)=>void} navigate
 */
export function DashboardPage(student, navigate) {
  const root = h('div', { class: 'page' });

  const welcome = h('section', { class: 'welcome-block' }, [
    h('h2', { class: 'welcome-block__title' }, `${greetingForNow()}, ${student.name.split(' ')[0]}.`),
    h('p', { class: 'welcome-block__subtitle' }, "Here's your campus overview."),
  ]);

  const attendanceSlot = h('div', { class: 'panel panel--attendance' }, LoadingState('Loading attendance…'));
  const gatepassSlot = h('div', { class: 'panel panel--gatepass' }, LoadingState('Loading gate passes…'));
  const notificationsSlot = h('div', { class: 'panel panel--notifications' }, LoadingState('Loading notifications…'));

  const quickActions = h('section', { class: 'quick-actions' }, [
    h('button', { class: 'quick-action', onClick: () => navigate(ROUTES.ATTENDANCE) }, [icon('check-circle', { size: 20 }), 'View Attendance']),
    h('button', { class: 'quick-action', onClick: () => navigate(ROUTES.GATEPASS) }, [icon('plus', { size: 20 }), 'Apply for Gate Pass']),
    h('button', { class: 'quick-action', onClick: () => navigate(ROUTES.NOTIFICATIONS) }, [icon('bell', { size: 20 }), 'View Notifications']),
  ]);

  root.append(
    welcome,
    h('div', { class: 'dashboard-grid' }, [attendanceSlot, gatepassSlot]),
    notificationsSlot,
    quickActions,
  );

  loadAttendance();
  loadGatePasses();
  loadNotifications();

  async function loadAttendance() {
    try {
      const summary = await getAttendanceSummary();
      attendanceSlot.replaceChildren(
        h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Overall Attendance')),
        h('div', { class: 'attendance-summary' }, [
          ProgressRing(summary.percentage, summary.threshold),
          h('div', { class: 'attendance-summary__stats' }, [
            h('p', { class: 'attendance-summary__line' }, [h('strong', {}, String(summary.present)), ` Present / ${summary.totalClasses} Classes`]),
            h('p', { class: 'attendance-summary__line attendance-summary__line--muted' }, `${summary.absent} classes missed`),
          ]),
        ]),
      );
    } catch {
      attendanceSlot.replaceChildren(h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Overall Attendance')), ErrorState('Unable to load attendance data. Please try again.', loadAttendance));
    }
  }

  async function loadGatePasses() {
    try {
      const counts = await getGatePassSummaryCounts();
      gatepassSlot.replaceChildren(
        h('div', { class: 'panel__head' }, [
          h('h3', { class: 'panel__title' }, 'Gate Pass Status'),
          h('button', { class: 'link-button', onClick: () => navigate(ROUTES.GATEPASS) }, 'Apply now'),
        ]),
        h('div', { class: 'gatepass-summary' }, [
          StatCard({ label: 'Pending', value: String(counts.pending), tone: 'warning', iconName: 'clock' }),
          StatCard({ label: 'Approved', value: String(counts.approved), tone: 'good', iconName: 'check-circle' }),
          StatCard({ label: 'Rejected', value: String(counts.rejected), tone: 'bad', iconName: 'warning' }),
        ]),
      );
    } catch {
      gatepassSlot.replaceChildren(h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Gate Pass Status')), ErrorState('Unable to load gate pass data. Please try again.', loadGatePasses));
    }
  }

  async function loadNotifications() {
    try {
      const all = await getNotifications();
      const recent = all.slice(0, 4);
      notificationsSlot.replaceChildren(
        h('div', { class: 'panel__head' }, [
          h('h3', { class: 'panel__title' }, 'Recent Notifications'),
          h('button', { class: 'link-button', onClick: () => navigate(ROUTES.NOTIFICATIONS) }, 'View all notifications'),
        ]),
        recent.length
          ? h('div', { class: 'notification-list notification-list--compact' }, recent.map((n) => NotificationCard(n, handleMarkRead, true)))
          : EmptyState('No new notifications.', 'inbox'),
      );
    } catch {
      notificationsSlot.replaceChildren(h('div', { class: 'panel__head' }, h('h3', { class: 'panel__title' }, 'Recent Notifications')), ErrorState('Unable to load notifications. Please try again.', loadNotifications));
    }
  }

  async function handleMarkRead(id) {
    await markNotificationAsRead(id);
    loadNotifications();
  }

  return root;
}
