from django.shortcuts import render, redirect
from django.db import connection
from datetime import datetime
from datetime import date

# Create your views here.
def index(request):
    """Shows the main page"""

    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'delete':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM GPU_Listing WHERE Listingid = %s", [request.POST['id']])

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GPU_Listing ORDER BY Listingid")
        listings = cursor.fetchall()

    result_dict = {'records': listings}

    return render(request,'app/index.html',result_dict)

# Create your views here.
def view(request, id):
    """Shows the main page"""
    
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
        customer = cursor.fetchone()
    result_dict = {'cust': customer}

    return render(request,'app/view.html',result_dict)

# Create your views here.
def add(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [request.POST['customerid']])
            customer = cursor.fetchone()
            ## No customer with same id
            if customer == None:
                ##TODO: date validation
                cursor.execute("INSERT INTO customers VALUES (%s, %s, %s, %s, %s, %s, %s)"
                        , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                           request.POST['dob'] , request.POST['since'], request.POST['customerid'], request.POST['country'] ])
                return redirect('index')    
            else:
                status = 'Customer with ID %s already exists' % (request.POST['customerid'])


    context['status'] = status
 
    return render(request, "app/add.html", context)

# Create your views here.
def edit(request, id):
    """Shows the main page"""

    # dictionary for initial data with
    # field names as keys
    context ={}

    # fetch the object related to passed id
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
        obj = cursor.fetchone()

    status = ''
    # save the data from the form

    if request.POST:
        ##TODO: date validation
        with connection.cursor() as cursor:
            cursor.execute("UPDATE customers SET first_name = %s, last_name = %s, email = %s, dob = %s, since = %s, country = %s WHERE customerid = %s"
                    , [request.POST['first_name'], request.POST['last_name'], request.POST['email'],
                        request.POST['dob'] , request.POST['since'], request.POST['country'], id ])
            status = 'Customer edited successfully!'
            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [id])
            obj = cursor.fetchone()


    context["obj"] = obj
    context["status"] = status
 
    return render(request, "app/edit.html", context)

# Create your views here.
def listing(request):
    """Shows the main page"""

    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM GPU_Listing ORDER BY Listingid")
        listings = cursor.fetchall()

    result_dict = {'records': listings}

    return render(request,'app/listing.html',result_dict)


def rental(request, Listingid):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM GPU_Listing WHERE Listingid = %s", [Listingid])
            listing = cursor.fetchone()
            ## No customer with same id
            if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() >= listing[4] and datetime.strptime(request.POST['End_day'], '%Y-%m-%d').date() <= listing[5]):
                ##TODO: date validation
                cursor.execute("INSERT INTO Rental VALUES (%s, %s, %s, %s, %s, %s)"
                        , [request.POST['Borrower_id'], listing[1], listing[2],
                           int(Listingid) , request.POST['Start_day'], request.POST['End_day']])
                cursor.execute("DELETE FROM GPU_Listing WHERE Listingid = %s", [Listingid])
                cursor.execute("SELECT * FROM GPU_Listing g1 WHERE g1.listingid >= all (SELECT g2.listingid FROM GPU_Listing g2)")
                last_entry = cursor.fetchone()
                if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() == listing[4]):
                    cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                         request.POST['End_day'] + 1, listing[5], listing[6]])
                if (datetime.strptime(request.POST['Start_day'], '%Y-%m-%d').date() > listing[4]):
                    cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 1 ,listing[1], listing[2], listing[3], 
                                                                                         listing[4], request.POST['Start_day'] - 1, listing[6]])
                    cursor.execute("INSERT INTO GPU_Listing VALUES(%s, %s,%s,%s,%s,%s,%s)", [last_entry[0] + 2 ,listing[1], listing[2], listing[3], 
                                                                                         request.POST['End_day'] + 1, listing[5], listing[6]])
                return redirect('index')    
            else:
                status = 'Invalid Rental Dates'


    context['status'] = status
 
    return render(request, "app/rental.html", context)
