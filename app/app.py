import os, json, time
from flask import Flask, request, redirect, render_template, send_from_directory, Response, Markup
from werkzeug import secure_filename
import worker 
import rq
from rq.registry import StartedJobRegistry
from db.db import * 
from os import listdir
from os.path import isfile, join


# Folder Structure
# ----------------------------------------------------------------------------------------------
dir_path                    = os.path.dirname(os.path.realpath(__file__))
print('dir_path: ', dir_path)  


# Start Flask
# ----------------------------------------------------------------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="files", static_url_path="/files")
worker.rq.init_app(app)

# Main Page
# ----------------------------------------------------------------------------------------------
@app.route('/', methods=['GET'])
def index(): 
    try:
        default_queue = rq.get_queue()
        print('default_queue: ', default_queue)
    except:
        pass

    return render_template('index.html')

# Ajax for Main Page
# ----------------------------------------------------------------------------------------------
@app.route('/last_5_jobs', methods=['GET'])
def last_5_jobs():
    table = '''
        <table class="table table-bordered" style="font-size:12px">
        <thead>
            <tr>
                <th scope="col">pdf_id</th>
                <th scope="col">filename</th>
                <th scope="col">status</th>
                <th scope="col">job_id</th>
                <th scope="col">received_at</th>
                <th scope="col">enqueued_at</th>
                <th scope="col">processed_at</th>
                <th scope="col">img_count</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    sql = '''
        select pdf_id
            , filename
            , status
            , job_id
            , created_at
            , enqueued_at
            , processed_at
            , created_at - processed_at as processing_time
            ,(select count(1) from imgs where imgs.pdf_id = pdfs.pdf_id) as img_count
        from pdfs
        order by created_at desc
        limit 5
    '''
    data = select(sql)

    for pdf_id, filename, status, job_id, created_at, enqueued_at, processed_at, processing_time, img_count in data:
        table += '''
            <tr>
                <th scope="row">'''+str(pdf_id)+'''</th>
                <td>'''+str(filename)+'''</td>
                <td>'''+str(status)+'''</td>
                <td>'''+str(job_id)+'''</td>
                <td>'''+str(created_at)+'''</td>
                <td>'''+str(enqueued_at)+'''</td>
                <td>'''+str(processed_at)+'''</td>
                <td>'''+str(img_count)+'''</td>
            </tr>
            <tr>
        '''   
    table += '''
    </tbody>
    </table>
    '''
    return table

@app.route('/queue_count', methods=['GET'])
def queue_count():
    return str(str(len(joblist)))

@app.route('/queue_list', methods=['GET'])
def queue_list():
    print('queue_list')
    q = worker.rq.get_queue()
    jobs = q.get_job_ids()
    for job_id in jobs:
        print(i)
        job = rq.worker.Job.fetch(job_id, connection=worker.rq.connection)
        object = job
        object_methods = [method_name for method_name in dir(object) if callable(getattr(object, method_name))]
        return(str(object_methods))

    return str(jobs)


# Helper Functions for Development
# ----------------------------------------------------------------------------------------------
@app.route('/reset', methods=['GET'])
def reset(): 
    try:
        for folder in ['/app/files/pdfs/', '/app/files/imgs/']: 
            print('folder: ', folder)
            for file in [f for f in listdir(folder) if isfile(join(folder, f))]:  os.remove(os.path.join(folder, file))
        
        for table in ['pdfs', 'imgs', 'api_keys']: 
            print('table: ', table)
            delete('''drop table '''+table+'''; ''')
    
        sql_tables = open ('/app/db/tables.sql', "r").read().split(';')
        for sql in sql_tables: 
            print(sql)
            insert(sql)

        return app.response_class(response=json.dumps({"OK": "200 - Everything was reset"}),status=200,mimetype='application/json')
    except Exception as e:
        return app.response_class(response=json.dumps({"error":"500  - Internal Server Error "}),status=500,mimetype='application/json')

@app.route('/folder/', methods=['GET'])
@app.route('/folder/<folder>', methods=['GET'])
def folder(folder=''):
    path = '/app/files/'+str(folder)
    files_in_folder = [f for f in listdir(path) if isfile(join(path, f))]
    return str(files_in_folder)

@app.route('/job_info/<job_id>', methods=['GET'])
def job_info(job_id):
    try:
        job = rq.worker.Job.fetch(job_id, connection=worker.rq.connection)
        return str(job)
    except Exception as e:
        return str(e)

@app.route('/delete_job/<job_id>', methods=['GET'])
def delete_job(job_id):
    try:
        job = rq.job.Job.fetch(job_id, connection=jobs.rq.connection)
        job.delete()  
    except Exception as e:
        return str(e)


# API 
# ----------------------------------------------------------------------------------------------
@app.route('/documents',methods = ['POST'])
@app.route('/documents/<document_id>',methods = ['GET'])
@app.route('/documents/<document_id>/pages/<number>',methods = ['GET'])
def documents(document_id='', number=''):
    print('\n[+] new_request')
    print('----------------------------')
    print('document_id: ', document_id)
    print('number: ', document_id)
    print('headers: ', request.headers)
    print('ip address: ', request.remote_addr)
    print('args: ',         request.args)

    api_key = ''
    if 'api-key' in request.headers:
        api_key = request.headers['api-key']
    else:
        if 'api-key' in request.args:
            api_key = request.args['api-key']
        else:
            json_data = {"error":"401 - Unauthorized - API Key not received in Header or as URL parameter"}
            return app.response_class(response=json.dumps(json_data),status=401,mimetype='application/json')

    if api_key != '':
        sql = '''select api_key from api_keys where api_key = '''+br(api_key)+''';'''
        data = select(sql)
        if data ==[]:
            print('API Key is not Ok')
            json_data = {"error":"401 - Unauthorized - API Key is not valid"}
            return app.response_class(response=json.dumps(json_data),status=401,mimetype='application/json')
        else:
            print('API Key is Ok')
            if request.method == 'POST':
                print('request.method POST')
                print('data: ', request.data)
                print('files: ',request.files)
                print('len: ',len(request.files))
                print('keys: ',request.files.keys())

                # Check how many files were passed
                if len(request.files) > 1: 
                    json_data = {"error":"400 - Bad Request - more than one file is not permitted at this moment"}
                    return app.response_class(response=json.dumps(json_data),status=400,mimetype='application/json')
                
                # Make sure key 'file' is inside
                if 'file' not in request.files.keys():
                    json_data = {"error":"400 - Bad Request - Key 'file' is missing "}
                    return app.response_class(response=json.dumps(json_data),status=400,mimetype='application/json')
                   
                # Make sure it is a PDF
                print('files: ',request.files['file'].filename)
                print(request.files['file'].filename[-4:])

                if request.files['file'].filename[-4:].lower() != '.pdf':
                    json_data = {"error":"400 - Bad Request - API can only process PDF's at this moment "}
                    return app.response_class(response=json.dumps(json_data),status=400,mimetype='application/json')

                # Insert into DB
                pdf_id = ''
                try:
                    sql = '''insert into pdfs (ip_address, filename, status) values ('''+br(request.remote_addr)+''', '''+br(request.files['file'].filename)+''', '''+br('processing')+''');'''
                    pdf_id = insert(sql)
                except Excetion as e:
                    json_data = {"error":"500  - Internal Server Error "}
                    return app.response_class(response=json.dumps(json_data),status=500,mimetype='application/json')


                # Save the PDF file 
                print('pdf_id: ', pdf_id)
                if pdf_id == '':

                    json_data = {"error":"500  - Internal Server Error "}
                    return app.response_class(response=json.dumps(json_data),status=500,mimetype='application/json')
                else:

                    print('\n FILE SAVING ', request.files['file'])
                    request.files['file'].save(f'/app/files/pdfs/{pdf_id}.pdf')

                    # # Add to Redis Processing Queue and Saving the information
                    job = worker.background_job.queue(pdf_id)

                    sql = '''
                    update pdfs set 
                    enqueued_at ='''+br(job.enqueued_at)+''', 
                    job_id = '''+br(job.id)+''' 
                    where pdf_id = '''+br(pdf_id)+'''
                    '''
                    update(sql)

                    # return the Value 

                    json_data = {"id": str(pdf_id)}
                    return app.response_class(response=json.dumps(json_data),status=200,mimetype='application/json')

                return Response("Accepted", status=202  )
            elif request.method == 'GET':
                print('request.method GET')
                print('document_id: ', document_id)
                print('number: ', number)
                if document_id == '':
                    json_data = {"error":"400 - Missing Document ID"}
                    return app.response_class(response=json.dumps(json_data),status=400,mimetype='application/json')
                else:
                    if number =='':
                        sql = '''
                            select status
                                    ,(select count(1) from imgs where imgs.pdf_id = pdfs.pdf_id) as img_count
                            from pdfs
                            where pdf_id = '''+br(document_id)+'''
                        '''
                        data = select(sql)
                        if data ==[]:
                            json_data = {"error":"400 - Document ID not found"}
                            return app.response_class(response=json.dumps(json_data),status=400,mimetype='application/json')
                        else:
                            status, img_count = data[0][0], data[0][1]
                            json_data =  {'status': status, 'n_pages': img_count}
                            return app.response_class(response=json.dumps(json_data),status=200,mimetype='application/json')
                    else:
                        img_path = f'/app/files/imgs/{document_id}_{number}.png'
                        if not os.path.isfile(img_path):
                            json_data = {"error":"400 - Page not Found"}
                            return app.response_class(response=json.dumps(json_data),status=400,mimetype='application/json')
                        else:
                            img_path = f'/files/imgs/{document_id}_{number}.png'
                            return render_template('img.html', img_path = img_path)
            else:
                json_data = {"error":"400 - Bad Request"}
                return app.response_class(response=json.dumps(json_data),status=400,mimetype='application/json')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=80)