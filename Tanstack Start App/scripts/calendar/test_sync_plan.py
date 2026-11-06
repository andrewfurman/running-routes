import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('sync_plan', Path(__file__).with_name('sync_plan.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RestoreCalendarPlan(unittest.TestCase):
    def test_restores_only_matching_cancelled_event(self):
        body = {'id': 'run123', 'summary': 'Hillcrest · 3.0 mi', 'extendedProperties': {'private': {'runningRoutesTarget': 'street-id'}}}
        old = dict(body, status='cancelled')
        with patch.object(module, 'gws', side_effect=[subprocess.CalledProcessError(1, ['gws']), old, {'id': 'run123'}]) as call:
            self.assertEqual(module.insert_or_restore({'calendarId': 'primary', 'sendUpdates': 'none'}, body)['id'], 'run123')
            self.assertEqual(call.call_args.args[0], 'patch')
            self.assertEqual(call.call_args.args[2]['status'], 'confirmed')
            self.assertNotIn('id', call.call_args.args[2])

    def test_refuses_active_or_unrelated_events(self):
        body = {'id': 'run123', 'extendedProperties': {'private': {'runningRoutesTarget': 'street-id'}}}
        for old in [dict(body, status='confirmed'), {'status': 'cancelled', 'extendedProperties': {'private': {'runningRoutesTarget': 'other-street'}}}]:
            with patch.object(module, 'gws', side_effect=[subprocess.CalledProcessError(1, ['gws']), old]) as call:
                with self.assertRaises(RuntimeError): module.insert_or_restore({'calendarId': 'primary'}, body)
                self.assertEqual(call.call_count, 2)

if __name__ == '__main__': unittest.main()
