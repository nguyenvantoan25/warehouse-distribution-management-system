import 'vue-router'
import type { Portal } from '../app/portals'
declare module 'vue-router' {
  interface RouteMeta {
    portal?: Portal
    access?: string
  }
}
