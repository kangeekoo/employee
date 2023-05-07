from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime, timedelta

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


@app.route("/about")
def about():
    return render_template('portfolio.html')

@app.route("/aboutKE")
def aboutke():
    return render_template('portfolioKangee.html')

@app.route("/aboutJK")
def aboutjk():
    return render_template('portfolioJiekee.html')

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

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

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

            cursor.execute(insert_sql, (emp_id, first_name, last_name, email, contact, location, position, pri_skill, hire_date, payscale, object_url))
            db_conn.commit()

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('outputAdd.html', name=emp_name)

@app.route("/fetchdata", methods=['POST'])
def SearchEmp():
    emp_id = request.form['emp_id']

    # fetch employee data from MySQL database
    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql, (emp_id,))
    emp_data = cursor.fetchone()
    cursor.close()

    if emp_data is None:
        return render_template('notFound.html', emp_id=emp_id)

    first_name = emp_data[1]
    last_name = emp_data[2]
    email = emp_data[3]
    contact = emp_data[4]
    location = emp_data[5]
    position = emp_data[6]
    pri_skill = emp_data[7]
    hire_date = emp_data[8]
    payscale = emp_data[9]
    img_src = emp_data[10]

    # render template with employee data
    emp_name = "" + first_name + " " + last_name
    return render_template('outputSearch.html', emp_id= emp_id, name=emp_name, email=email, contact=contact, location=location, position=position, pri_skill=pri_skill, hire_date=hire_date, payscale=payscale, img_src=img_src)

@app.route("/updateemp", methods=['POST'])
def UpdateEmp():
    emp_id = request.form['emp_id']

    # fetch employee data from MySQL database
    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql, (emp_id,))
    emp_data = cursor.fetchone()
    cursor.close()

    if emp_data is None:
        return render_template('notFound.html', emp_id=emp_id)

    first_name = emp_data[1]
    last_name = emp_data[2]
    email = emp_data[3]
    contact = emp_data[4]
    location = emp_data[5]
    position = emp_data[6]
    pri_skill = emp_data[7]
    hire_date = emp_data[8]
    payscale = emp_data[9]
    img_src = emp_data[10]

    # render template with employee data for updating
    emp_name = "" + first_name + " " + last_name
    return render_template('formUpdate.html', emp_id= emp_id, name=emp_name, email=email, contact=contact, location=location, position=position, pri_skill=pri_skill, hire_date=hire_date, payscale=payscale, img_src=img_src)

@app.route("/updatedata", methods=['POST'])
def UpdateEmpData():
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

    update_sql = "UPDATE employee SET first_name=%s, last_name=%s, email=%s, contact=%s, location=%s, position=%s, pri_skill=%s, hire_date=%s, payscale=%s WHERE emp_id=%s"
    cursor = db_conn.cursor()

    if emp_image_file.filename != "":
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Uploading image to S3...")
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

    try:
        cursor.execute(update_sql, (first_name, last_name, email, contact, location, position, pri_skill, hire_date, payscale, emp_id))
        db_conn.commit()
    except:
        db_conn.rollback()


    print("Employee record updated...")
    emp_name = "" + first_name + " " + last_name
    return render_template('outputUpdate.html', emp_id= emp_id, name=emp_name, email=email, contact=contact, location=location, position=position, pri_skill=pri_skill, hire_date=hire_date, payscale=payscale, img_src=object_url)

@app.route("/deleteemp", methods=['POST'])
def DeleteEmp():
    emp_id = request.form['emp_id']

    select_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(select_sql, (emp_id,))
    emp_data = cursor.fetchone()
    cursor.close()

    if emp_data is None:
        return render_template('notFound.html', emp_id=emp_id)

    first_name = emp_data[1]
    last_name = emp_data[2]

    delete_sql = "DELETE FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(delete_sql, (emp_id,))
        db_conn.commit()
        print("Data deleted from MySQL RDS...")

        # Delete image file from S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        try:
            print("Deleting image file from S3...")
            s3.Object(custombucket, emp_image_file_name_in_s3).delete()
        except Exception as e:
            return str(e)

    except Exception as e:
        return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    emp_name = "" + first_name + " " + last_name
    return render_template('outputDelete.html', name=emp_name)

# define route for attendance form
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    emp_id = None
    date = None
    clock_in = None
    clock_out = None
    duration = None
    if request.method == 'POST':
        emp_id = request.form['emp_id']

        # fetch employee data from MySQL database
        select_sql = "SELECT * FROM employee WHERE emp_id = %s"
        cursor = db_conn.cursor()
        cursor.execute(select_sql, (emp_id,))
        emp_data = cursor.fetchone()
        cursor.close()

        if emp_data is None:
            return render_template('notFound.html', emp_id=emp_id)

        date = request.form['date']
        clock_in = datetime.strptime(request.form['clock_in'], '%H:%M').time()
        clock_out = datetime.strptime(request.form['clock_out'], '%H:%M').time()
        
        # calculate duration
        duration = timedelta(hours=clock_out.hour, minutes=clock_out.minute) - timedelta(hours=clock_in.hour, minutes=clock_in.minute)
        
        # insert attendance data into MySQL database
        cursor = db_conn.cursor()
        sql = "INSERT INTO attendance (emp_id, date, clock_in, clock_out, duration) VALUES (%s, %s, %s, %s, %s)"
        val = (emp_id, date, clock_in, clock_out, duration)
        cursor.execute(sql, val)
        db_conn.commit()
        
    return render_template('attendance.html', emp_id = emp_id, date=date, clock_in=clock_in, clock_out=clock_out, duration = duration)

@app.route("/payroll", methods=['POST'])
def payroll():
    emp_id = request.form['emp_id']

    # fetch employee data from MySQL database
    select_sql_attendance = "SELECT * FROM attendance WHERE emp_id = %s"
    select_sql_employee = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    # execute the attendance query
    cursor.execute(select_sql_attendance, (emp_id,))
    emp_data_attendance = cursor.fetchall()

    # execute the employee query
    cursor.execute(select_sql_employee, (emp_id,))
    emp_data_employee = cursor.fetchone()

    cursor.close()

    if emp_data_attendance is None or emp_data_employee is None:
        return render_template('notFound.html', emp_id=emp_id)

    first_name = emp_data_employee[1]
    last_name = emp_data_employee[2]
    email = emp_data_employee[3]
    contact = emp_data_employee[4]
    position = emp_data_employee[6]
    payscale = emp_data_employee[9]

    total_duration = timedelta()

    # loop through all attendance data for the employee and sum up the duration
    for attendance_data in emp_data_attendance:
        duration_str = str(attendance_data[4])
        duration = datetime.strptime(duration_str, "%H:%M:%S").time()
        total_duration += timedelta(hours=duration.hour, minutes=duration.minute, seconds=duration.second)

    # calculate total duration in hours
    total_seconds = total_duration.total_seconds()
    total_duration_hours = round(total_seconds / 3600, 2)

    # calculate salary based on total duration in hours
    salary = calculate_salary(payscale, total_duration_hours)

    emp_name = "" + first_name + " " + last_name
    return render_template('payroll.html', emp_id= emp_id, name=emp_name, email=email, contact=contact, position=position, payscale=payscale, duration=total_duration, salary=salary)

def calculate_salary(payscale, total_duration_hours):
    # Calculate basic salary based on payscale
    total_salary = total_duration_hours * payscale

    return total_salary

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
