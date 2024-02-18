from flask import url_for

from moments.core.extensions import db
from moments.models import User, Photo, Comment, Notification, Tag
from tests import BaseTestCase
from moments.core.extensions import db


class MainTestCase(BaseTestCase):

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Join Now', data)

        self.login()
        response = self.client.get('/index')
        data = response.get_data(as_text=True)
        self.assertNotIn('Join Now', data)
        self.assertIn('My Home', data)

    def test_explore_page(self):
        response = self.client.get('/explore')
        data = response.get_data(as_text=True)
        self.assertIn('Change', data)

    def test_search(self):
        response = self.client.get('/search?q=', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Enter keyword about photo, user or tag.', data)

        response = self.client.get('/search?q=normal')
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about photo, user or tag.', data)
        self.assertIn('No results.', data)

        response = self.client.get('/search?q=normal&category=tag')
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about photo, user or tag.', data)
        self.assertIn('No results.', data)

        response = self.client.get('/search?q=normal&category=user')
        data = response.get_data(as_text=True)
        self.assertNotIn('Enter keyword about photo, user or tag.', data)
        self.assertNotIn('No results.', data)
        self.assertIn('Normal User', data)

    def test_show_notifications(self):
        user = db.session.get(User, 2)
        notification1 = Notification(message='test 1', is_read=True, receiver=user)
        notification2 = Notification(message='test 2', is_read=False, receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login()
        response = self.client.get('/notifications')
        data = response.get_data(as_text=True)
        self.assertIn('test 1', data)
        self.assertIn('test 2', data)

        response = self.client.get('/notifications?filter=unread')
        data = response.get_data(as_text=True)
        self.assertNotIn('test 1', data)
        self.assertIn('test 2', data)

    def test_read_notification(self):
        user = db.session.get(User, 2)
        notification1 = Notification(message='test 1', receiver=user)
        notification2 = Notification(message='test 2', receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login(email='admin@helloflask.com', password='123')
        response = self.client.post('/notifications/read/1')
        self.assertEqual(response.status_code, 403)

        self.logout()
        self.login()

        response = self.client.post('/notifications/read/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Notification archived.', data)

        self.assertTrue(db.session.get(Notification, 1).is_read)

    def test_read_all_notification(self):
        user = db.session.get(User, 2)
        notification1 = Notification(message='test 1', receiver=user)
        notification2 = Notification(message='test 2', receiver=user)
        db.session.add_all([notification1, notification2])
        db.session.commit()

        self.login()

        response = self.client.post('/notifications/read/all', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('All notifications archived.', data)

        self.assertTrue(db.session.get(Notification, 1).is_read)
        self.assertTrue(db.session.get(Notification, 2).is_read)

    def test_show_photo(self):
        response = self.client.get('/photo/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Delete', data)
        self.assertIn('test tag', data)
        self.assertIn('test comment body', data)

        self.login(email='admin@helloflask.com', password='123')
        response = self.client.get('/photo/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Delete', data)

    def test_photo_next(self):
        user = db.session.get(User, 1)
        photo2 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 2', author=user)
        photo3 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 3', author=user)
        photo4 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 4', author=user)
        db.session.add_all([photo2, photo3, photo4])
        db.session.commit()

        response = self.client.get('/photo/n/5', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 3', data)

        response = self.client.get('/photo/n/4', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 2', data)

        response = self.client.get('/photo/n/3', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 1', data)

        response = self.client.get('/photo/n/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This is already the last one.', data)

    def test_photo_prev(self):
        user = db.session.get(User, 1)
        photo2 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 2', author=user)
        photo3 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 3', author=user)
        photo4 = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                       description='Photo 4', author=user)
        db.session.add_all([photo2, photo3, photo4])
        db.session.commit()

        response = self.client.get('/photo/p/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 2', data)

        response = self.client.get('/photo/p/3', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 3', data)

        response = self.client.get('/photo/p/4', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo 4', data)

        response = self.client.get('/photo/p/5', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('This is already the first one.', data)

    def test_collect(self):
        photo = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg',
                      description='Photo 3', author=db.session.get(User, 2))
        db.session.add(photo)
        db.session.commit()
        self.assertEqual(db.session.get(Photo, 3).collectors, [])

        self.login()
        response = self.client.post('/collect/3', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo collected.', data)

        self.assertEqual(db.session.get(Photo, 3).collectors[0].collector.name, 'Normal User')

        response = self.client.post('/collect/3', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Already collected.', data)

    def test_uncollect(self):
        self.login()
        self.client.post('/collect/1', follow_redirects=True)

        response = self.client.post('/uncollect/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo uncollected.', data)

        response = self.client.post('/uncollect/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Not collect yet.', data)

    def test_report_comment(self):
        self.assertEqual(db.session.get(Comment, 1).flag, 0)

        self.login()
        response = self.client.post('/report/comment/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment reported.', data)
        self.assertEqual(db.session.get(Comment, 1).flag, 1)

    def test_report_photo(self):
        self.assertEqual(db.session.get(Photo, 1).flag, 0)

        self.login()
        response = self.client.post('/report/photo/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo reported.', data)
        self.assertEqual(db.session.get(Photo, 1).flag, 1)

    def test_show_collectors(self):
        user = db.session.get(User, 2)
        user.collect(db.session.get(Photo, 1))
        response = self.client.get('/photo/1/collectors', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('1 Collectors', data)
        self.assertIn('Normal User', data)

    def test_edit_description(self):
        self.assertEqual(db.session.get(Photo, 2).description, 'Photo 2')

        self.login()
        response = self.client.post('/photo/2/description', data=dict(
            description='test description.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Description updated.', data)
        self.assertEqual(db.session.get(Photo, 2).description, 'test description.')

    def test_new_comment(self):
        self.login()
        response = self.client.post('/photo/1/comment/new', data=dict(
            body='test comment from normal user.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertEqual(db.session.get(Photo, 1).comments[1].body, 'test comment from normal user.')

    def test_new_tag(self):
        self.login(email='admin@helloflask.com', password='123')

        response = self.client.post('/photo/1/tag/new', data=dict(
            tag='hello dog pet happy'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Tag added.', data)
        self.assertEqual(db.session.get(Photo, 1).tags[1].name, 'hello')
        self.assertEqual(db.session.get(Photo, 1).tags[2].name, 'dog')
        self.assertEqual(db.session.get(Photo, 1).tags[3].name, 'pet')
        self.assertEqual(db.session.get(Photo, 1).tags[4].name, 'happy')

    def test_set_comment(self):
        self.login()
        response = self.client.post('/set-comment/1', follow_redirects=True)
        self.assertEqual(response.status_code, 403)

        self.logout()
        self.login(email='admin@helloflask.com', password='123')
        response = self.client.post('/set-comment/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comment disabled', data)
        self.assertFalse(db.session.get(Photo, 1).can_comment)

        response = self.client.post('/set-comment/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Comment enabled', data)
        self.assertTrue(db.session.get(Photo, 1).can_comment)

    def test_reply_comment(self):
        self.login()
        response = self.client.get('/reply/comment/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Reply to', data)

    def test_delete_photo(self):
        self.login()
        response = self.client.post('/delete/photo/2', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Photo deleted.', data)
        self.assertIn('Normal User', data)

    def test_delete_comment(self):
        self.login()
        response = self.client.post('/delete/comment/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment deleted.', data)

    def test_show_tag(self):
        response = self.client.get('/tag/1')
        data = response.get_data(as_text=True)
        self.assertIn('Order by time', data)

        response = self.client.get('/tag/1/by_collects')
        data = response.get_data(as_text=True)
        self.assertIn('Order by collects', data)

    def test_delete_tag(self):
        photo = db.session.get(Photo, 2)
        tag = Tag(name='test')
        photo.tags.append(tag)
        db.session.commit()

        self.login()
        response = self.client.post('/delete/tag/2/2', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Tag deleted.', data)

        self.assertEqual(photo.tags, [])
        self.assertIsNone(db.session.get(Tag, 2))
