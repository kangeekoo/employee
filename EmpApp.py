from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    contact = request.form['contact']
    location = request.form['location']
    position = request.form['position']
    pri_skill = request.form['pri_skill']
    hire_date = request.form['hire_date']
    payscale = request.form['payscale']
    emp_image_file = request.files['emp_img_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, email, contact, location, position, pri_skill, hire_date, payscale))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/fetchdata", methods=['POST'])
def GetEmp():
    emp_id = request.form['emp_id']

    # fetch employee data from MySQL database
    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql, (emp_id,))
    emp_data = cursor.fetchone()
    cursor.close()

    if emp_data is None:
        return "Employee not found"

    first_name = emp_data[1]
    last_name = emp_data[2]
    email = emp_data[3]
    contact = emp_data[4]
    location = emp_data[5]
    position = emp_data[6]
    pri_skill = emp_data[7]
    hire_date = emp_data[8]
    payscale = emp_data[9]

    # fetch employee image file from S3 bucket
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    s3 = boto3.resource('s3')
    try:
        emp_image_file = s3.Bucket(custombucket).Object(emp_image_file_name_in_s3).get()['Body'].read()
    except s3.meta.client.exceptions.NoSuchKey:
        return "Employee image file not found in S3"

    # render template with employee data
    emp_name = "" + first_name + " " + last_name
    return render_template('GetEmpOutput.html', name=emp_name, email=email, contact=contact, location=location, position=position, pri_skill=pri_skill, hire_date=hire_date, payscale=payscale, emp_image_file=emp_image_file)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
