// ===== Student service =====
// Stage 1: getCurrentStudent() -> mock/students.js
// Stage 2: getCurrentStudent() -> apiClient.get('/students/me')

import { MOCK_STUDENT } from '../mock/students.js';

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getCurrentStudent() {
  await delay(350);
  // ----- FUTURE API INTEGRATION -----
  // return apiClient.get('/students/me');
  return { ...MOCK_STUDENT };
}
