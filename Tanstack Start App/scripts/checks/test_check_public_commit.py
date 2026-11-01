"""Exercise the public credential gate against a disposable Git index."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

CHECK = pathlib.Path(__file__).with_name('check_public_commit.py')

class PublicCommitTests(unittest.TestCase):
    def scan(self, filename, contents):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            subprocess.run(['git', 'init', '-q', directory], check=True)
            path = root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents)
            subprocess.run(['git', 'add', filename], cwd=root, check=True)
            return subprocess.run([sys.executable, str(CHECK), '--all'], cwd=root, capture_output=True, text=True)

    def test_blank_root_sample_is_allowed(self):
        self.assertEqual(self.scan('sample.env', '# Public template\nGOOGLE_MAPS_API_KEY=\nSTRAVA_WEB_COOKIE=\n').returncode, 0)

    def test_populated_sample_is_blocked_without_echoing_value(self):
        result = self.scan('sample.env', 'CLOUDFLARE_API_TOKEN=example-private-value\n')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('example-private-value', result.stderr)

    def test_real_or_nested_environment_files_remain_blocked(self):
        for filename in ['.env', '.env.production', 'app/sample.env', '.dev.vars']:
            with self.subTest(filename=filename):
                self.assertNotEqual(self.scan(filename, 'TOKEN=\n').returncode, 0)

    def test_credential_in_sample_comment_is_blocked(self):
        fake_key = 'AI' + 'za' + 'x' * 35
        self.assertNotEqual(self.scan('sample.env', '# ' + fake_key + '\nTOKEN=\n').returncode, 0)

if __name__ == '__main__':
    unittest.main()
