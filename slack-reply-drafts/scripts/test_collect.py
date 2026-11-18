"""Checks old-thread discovery, deduplication and safe collection failure."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('collect', Path(__file__).with_name('collect.py'))
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
c.USER = 'UEXAMPLE01'

class CollectionTests(unittest.TestCase):
    def test_recent_reply_to_old_root_and_new_message_are_retained(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(c, 'ROOT', Path(tmp)):
            channel = {'id':'C1','name':'test'}
            root = {'ts':'10.0','text':'old question','reply_count':1,'latest_reply':'105.0','user':'OTHER'}
            reply = {'ts':'105.0','text':'reply','thread_ts':'10.0','user':c.USER}
            with patch.object(c,'pages',side_effect=[[root],[root,reply]]):
                row = c.collect(channel,100,110,True)
            self.assertEqual(row['sent'],1)
            self.assertEqual(row['pending'],0)
            new = {'ts':'115.0','text':'new question','user':'OTHER'}
            with patch.object(c,'pages',return_value=iter([new,root])) as pages:
                row = c.collect(channel,100,120,False)
                self.assertEqual(pages.call_count,1)
            self.assertEqual(row['pending'],1)
            self.assertEqual(c.read(Path(tmp)/'conversations/C1/pending.json',[])[0]['ts'],'115.0')

    def test_failed_collection_does_not_advance_seen(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(c,'ROOT',Path(tmp)):
            state = Path(tmp)/'conversations/C1/state.json'
            c.save(state,{'seen':['100.0']})
            with patch.object(c,'pages',side_effect=RuntimeError('denied')):
                with self.assertRaises(RuntimeError):
                    c.collect({'id':'C1'},100,120,False)
            self.assertEqual(c.read(state,{})['seen'],['100.0'])

    def test_recognized_credentials_are_redacted(self):
        self.assertEqual(c.redact('token xoxb-example.secret'), 'token [REDACTED CREDENTIAL]')
        self.assertEqual(c.redact('sk_example12345'), '[REDACTED CREDENTIAL]')
        self.assertEqual(c.redact('Hello <@U0123456789>!'), 'Hello <@U0123456789>!')

    def test_pagination_uses_cursor_and_rejects_incomplete_history(self):
        with patch.object(c,'api',side_effect=[{'messages':[{'ts':'1'}],'response_metadata':{'next_cursor':'next'}},{'messages':[{'ts':'2'}]}]) as api:
            self.assertEqual([m['ts'] for m in c.pages('conversations.history','messages',channel='C1')],['1','2'])
            self.assertEqual(api.call_args_list[1].kwargs['cursor'],'next')
        with patch.object(c,'api',return_value={'messages':[],'has_more':True}):
            with self.assertRaises(RuntimeError):
                list(c.pages('conversations.history','messages',channel='C1'))

if __name__ == '__main__':
    unittest.main()
