import {
  Activity,
  Bell,
  BookOpen,
  ClipboardList,
  Cpu,
  FlaskConical,
  GitCompare,
  LayoutDashboard,
  Map as MapIcon,
  ScrollText,
  Settings,
  Users,
  type LucideIcon,
} from 'lucide-react'

export interface StaffNavItem {
  id: string
  /** i18n key of the label. */
  label: string
  icon: LucideIcon
  /** Absent = the screen is built in a later phase: shown disabled with a "soon" tag, never a dead link. */
  to?: string
}

/** Reviewer console (spec 15.4). Only the queue exists in Phase 2; the rest arrive in Phases 8 and 10. */
export const REVIEWER_NAV: StaffNavItem[] = [
  { id: 'queue', label: 'staff.reviewer.queue', icon: ClipboardList, to: '/review' },
  { id: 'map', label: 'staff.reviewer.map', icon: MapIcon },
  { id: 'drafts', label: 'staff.reviewer.drafts', icon: Bell },
  { id: 'agreement', label: 'staff.reviewer.agreement', icon: GitCompare },
]

/** Admin console (spec 15.4). Only the dashboard exists in Phase 2. */
export const ADMIN_NAV: StaffNavItem[] = [
  { id: 'dashboard', label: 'staff.admin.dashboard', icon: LayoutDashboard, to: '/admin' },
  { id: 'users', label: 'staff.admin.users', icon: Users },
  { id: 'models', label: 'staff.admin.models', icon: Cpu },
  { id: 'settings', label: 'staff.admin.settings', icon: Settings },
  { id: 'kb', label: 'staff.admin.kb', icon: BookOpen },
  { id: 'simulation', label: 'staff.admin.simulation', icon: FlaskConical },
  { id: 'alerts', label: 'staff.admin.alerts', icon: Bell },
  { id: 'audit', label: 'staff.admin.audit', icon: ScrollText },
  { id: 'health', label: 'staff.admin.health', icon: Activity },
]

export type StaffArea = 'reviewer' | 'admin'

export function navFor(area: StaffArea): StaffNavItem[] {
  return area === 'admin' ? ADMIN_NAV : REVIEWER_NAV
}
