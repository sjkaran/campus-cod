// The only import views use for data. Swapping mock for real API happens here.
import { CONFIG } from '../config.js';
import { mockService } from './mockService.js';
import { apiService } from './apiService.js';

export const api = CONFIG.USE_MOCK ? mockService : apiService;
