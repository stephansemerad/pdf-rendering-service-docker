import time, sys
from flask_rq2 import RQ
from rq import get_current_job
from datetime import datetime
from PIL import Image
from pdf2image import convert_from_path
sys.path.append('..')
from db.db import *

rq = RQ()
rq.redis_url = 'redis://redis:6379/0'

@rq.job(timeout=180)
def background_job(pdf_id):
    print('/n/n/n [background_task]')
    print('*********************************')
    print('pdf_id: ', pdf_id)
    time.sleep(10)
    try:
        data = select('''select filename, status from pdfs where pdf_id = '''+br(pdf_id)+''' -- and status ='processing' ;''')
        for filename, status in data:
            images = convert_from_path(f'/app/files/pdfs/{pdf_id}.pdf')
            
            img_counter = 0
            for img in images:
                img_counter += 1
                filename    = str(pdf_id) + '_' + str(img_counter) + '.png'
                # file_path   = f'/app/files/pdfs/{pdf_id}.pdf'
                img_path    = f'/app/files/imgs/{filename}'
                img.thumbnail((1200,1600), Image.ANTIALIAS)
                img.save(img_path, quality=100)
                height, width = (img.size)

                sql ='''
                insert into imgs (pdf_id, pdf_page,filename, width, height) 
                select '''+br(pdf_id)+''', '''+br(img_counter)+''', '''+br(filename)+''', '''+br(height)+''', '''+br(width)+'''
                where not exists ( select * from imgs where filename = '''+br(filename)+''');
                '''
                insert(sql)

                update('''update pdfs set status ='done', processed_at='''+br(datetime.now())+''' where pdf_id='''+br(pdf_id)+''';''')
    except Exception as e:
        update('''update pdfs set status ='failed', processed_at='''+br(datetime.now())+''' where pdf_id='''+br(pdf_id)+''';''')
