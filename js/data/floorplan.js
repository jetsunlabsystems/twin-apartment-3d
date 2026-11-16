// Architectural Floorplan Dataset - Unified Domain Re-export Barrel
import { ROOMS } from './rooms.js';
export { BOUNDS, ROOMS, R } from './rooms.js';
export { WALLS } from './walls.js';
export { WINS, DOORS, SLIDES } from './openings.js';
if (typeof window !== 'undefined') window.ROOMS = ROOMS;
