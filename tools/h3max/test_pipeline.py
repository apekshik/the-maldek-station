import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import pipeline

class PipelineTests(unittest.TestCase):
    def test_blank_key_fails_without_disclosure(self):
        with tempfile.TemporaryDirectory() as temp, patch.dict('os.environ',{'FAL_KEY':''}):
            path=Path(temp)/'.env';path.write_text('FAL_KEY=\n')
            with self.assertRaises(ValueError):pipeline.load_key(path)

    def test_existing_job_cannot_resubmit(self):
        with tempfile.TemporaryDirectory() as temp, patch('urllib.request.urlopen') as http:
            with self.assertRaises(FileExistsError):pipeline.generate({}, {}, 'test-secret', Path(temp))
            http.assert_not_called()

    def test_uncertain_request_is_recorded_without_retry_or_secret(self):
        with tempfile.TemporaryDirectory() as temp, patch('urllib.request.urlopen',side_effect=TimeoutError('test-secret')) as http:
            job=Path(temp)/'job'
            with self.assertRaises(RuntimeError) as error:pipeline.generate({}, {}, 'test-secret',job)
            self.assertEqual(http.call_count,1)
            self.assertNotIn('test-secret',str(error.exception))
            text=(job/'job.json').read_text()
            self.assertNotIn('test-secret',text)
            self.assertEqual(json.loads(text)['status'],'uncertain_check_fal_dashboard')

    def test_mp4_is_video_mime(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'test.mp4';path.write_bytes(b'\x00\x00\x00\x20ftypisom00000000')
            self.assertTrue(pipeline.uri(path).startswith('data:video/mp4;base64,'))

    def test_old_scene_capture_is_rejected(self):
        old=Path(__file__).resolve().parents[2]/'art/blender/h3max/outputs/exterior-eevee-02'
        if not (old/'capture.json').exists():self.skipTest('Old local fixture not available')
        with self.assertRaisesRegex(ValueError,'different or changed Blender source'):
            pipeline.prepare(pipeline.HERE/'maldek.json',old,'exterior')

    def test_plan_uses_motion_and_style_with_no_network(self):
        captures=Path(__file__).resolve().parents[2]/'art/blender/h3max/outputs/refined-exterior-eevee-01'
        if not (captures/'capture.json').exists():self.skipTest('Local capture still rendering')
        with patch('urllib.request.urlopen') as http:
            payload,summary=pipeline.prepare(pipeline.HERE/'maldek.json',captures,'exterior')
            http.assert_not_called()
            self.assertEqual(len(payload['reference_video_urls']),1)
            self.assertNotIn('reference_image_urls',payload)
            self.assertEqual(payload['prompt_expansion_mode'],'quality')
            self.assertEqual(summary['requests'],1)
            self.assertNotIn('base64',json.dumps(summary))

if __name__=='__main__':unittest.main()
