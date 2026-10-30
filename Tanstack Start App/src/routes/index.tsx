import { createFileRoute } from '@tanstack/react-router'
import { RunRoutesApp } from '../components/RunRoutesApp'
import '../styles.css'
export const Route = createFileRoute('/')({ component: RunRoutesApp })
