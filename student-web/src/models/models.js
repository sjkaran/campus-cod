// ===== Shared data models =====
// Plain JSDoc typedefs (no TS build step) that describe the shapes every
// service must return. Both the mock implementation (Stage 1) and the
// future API implementation (Stage 2) conform to these shapes, so UI
// components never need to know which one is behind the service layer.

/**
 * @typedef {Object} Student
 * @property {string} id
 * @property {string} name
 * @property {string} rollNumber
 * @property {string} department
 * @property {number} semester
 * @property {string} section
 * @property {string} email
 * @property {string} phone
 * @property {string} admissionYear
 */

/**
 * @typedef {Object} Notification
 * @property {string} id
 * @property {string} title
 * @property {string} message
 * @property {string} publisher
 * @property {string} audience
 * @property {'low'|'normal'|'high'} priority
 * @property {string} createdAt ISO date string
 * @property {boolean} read
 */

/**
 * @typedef {Object} SubjectAttendance
 * @property {string} subject
 * @property {number} totalClasses
 * @property {number} present
 * @property {number} absent
 * @property {number} percentage
 */

/**
 * @typedef {Object} AttendanceRecord
 * @property {string} date ISO date string
 * @property {string} subject
 * @property {'Morning'|'Afternoon'|'Evening'} session
 * @property {'Present'|'Absent'} status
 */

/**
 * @typedef {Object} GatePass
 * @property {string} id
 * @property {string} destination
 * @property {string} reason
 * @property {string} remarks
 * @property {string} departureDate
 * @property {string} departureTime
 * @property {string} returnDate
 * @property {string} returnTime
 * @property {string} submittedAt ISO date string
 * @property {'PENDING'|'APPROVED'|'REJECTED'} status
 * @property {string|null} reviewedBy
 * @property {string|null} reviewRemarks
 * @property {string|null} reviewedAt
 */

export {};
