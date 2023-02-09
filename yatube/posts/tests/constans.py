from django.core.files.uploadedfile import SimpleUploadedFile

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
IMAGE = SimpleUploadedFile(
    name='small.gif',
    content=SMALL_GIF,
    content_type='image/gif'
)

TITLE = 'Тестовый заголовок группы'
SLUG = 'test_slug'
DESCRIPTION = 'Тестовое описание'
TITLE1 = 'Тестовый заголовок группы 1'
SLUG1 = 'test_slug1'
DESCRIPTION1 = 'Тестовое описание 1'

TEXT = 'Тестовый текст'
USERNAME = 'TestName'
EMAIL = 'test@yandex.ru'
PASSWORD = 'test_password123'
ID = '1'

TEXT1 = 'Тестовый текст 1'
USERNAME1 = 'TestName1'
EMAIL1 = 'test1@yandex.ru'
PASSWORD1 = 'test1_password123'
ID1 = '2'

AUTHOR = 'Автор'
GROUP = 'Группа'
