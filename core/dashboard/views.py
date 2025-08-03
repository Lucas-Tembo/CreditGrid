from django.shortcuts import render, redirect
from .models import borrower as Borrower, user_details
from .forms import borrowerForm, user_details_form
from django.contrib.auth.decorators import login_required
from django.db.models.functions import TruncMonth
from django.db.models import Sum
import json
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from collections import defaultdict
from django.db.models.functions import TruncMonth
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib import messages
from reportlab.lib.units import inch
from reportlab.lib import colors

@login_required(login_url= "/accounts/login")
def dashboard(request):
    borrowers = Borrower.objects.filter(author=request.user)
    if request.method == "POST":
       form = borrowerForm(request.POST)
       if form.is_valid():
           instance = form.save(commit=False)
           instance.author = request.user
           instance.save()
           return redirect('dashboard')
       else:
           print("Form errors:", form.errors)
           print( "POST data:", request.POST)
    else:
        form = borrowerForm()

    unpaid_borrowers = borrowers.filter(status='active')
    total_disbursed_amount= sum(b.amount for b in unpaid_borrowers)
    total_interest_earned = sum(b.interest_amount for b in unpaid_borrowers)
    total_outstanding_amount = sum(b.amount_due for b in unpaid_borrowers)
    active_loans = unpaid_borrowers.count()

     # Get borrowers whose payments are due today or in the future
    due_soon_borrowers = Borrower.objects.filter( author=request.user,
        date__gte=now().date(), status='active'
    ).order_by('date')[:5]  # Get the top 5 closest due dates

           # Prepare default empty values
    interest_amount_labels = []
    interest_amount_data = []
    unpaid_borrowers = [] 
        # Create a dict to group by month
    interest_amount_by_month = defaultdict(float)

    for b in borrowers:
        if b.date:
            # Group by year + month string like "2025-07"
            month_str = b.date.strftime('%Y-%m')
            interest_amount_by_month[month_str] += float(b.interest_amount)  # property

        interest_amount_labels = sorted(interest_amount_by_month.keys())
        interest_amount_data = [interest_amount_by_month[m] for m in interest_amount_labels]

    context = {
        'interest_amount_labels_json': json.dumps(interest_amount_labels),
        'interest_amount_data_json': json.dumps(interest_amount_data),
        # existing context
        'borrowers': borrowers,
        'unpaid_borrowers': unpaid_borrowers,
        'active_loans': active_loans,
        'form': form,
        'total_outstanding_amount': total_outstanding_amount,
        'total_interest_earned': total_interest_earned,
        'total_disbursed_amount': total_disbursed_amount,
        'due_soon_borrowers': due_soon_borrowers,
        }
    return render(request,'dashboard/dashboard.html', context)

def homepage(request):
    return render(request,'index.html')

@login_required(login_url= "/accounts/login")
def transactions(request):
     borrowers = Borrower.objects.filter(author=request.user, status='active')
     clients = borrowers.order_by('date')
     return render(request,'dashboard/transactions.html', {'clients': clients})
 
@login_required(login_url= "/accounts/login")
def analytics(request):
    borrowers = Borrower.objects.filter(author=request.user)
    clients = borrowers.order_by('date')
    total_outstanding_amount = sum(borrower.amount_due for borrower in clients)
    total_interest_earned = sum(borrower.interest_amount for borrower in clients)
    total_disbursed_amount = sum(borrower.amount for borrower in clients)
  
    # Get all borrowers for this user
    borrowers = Borrower.objects.filter(author=request.user)

    # Prepare default empty values
    interest_amount_labels = []
    interest_amount_data = []
    outstanding_labels = []
    outstanding_data = []
    disbursed_labels = []
    disbursed_data = []
    clients = []

    # Create a dict to group by month
    outstanding_by_month = defaultdict(float)

    # Loop manually to access the `.amount_due` property
    for b in borrowers:
        if b.date:
            # Group by year + month string like "2025-07"
            month_str = b.date.strftime('%Y-%m')
            outstanding_by_month[month_str] += float(b.amount_due)  # property

    # Now prepare sorted labels and values
    outstanding_labels = sorted(outstanding_by_month.keys())  # ['2025-05', '2025-06', ...]
    outstanding_data = [outstanding_by_month[month] for month in outstanding_labels]

    # Create a dict to group by month
    disbursed_by_month = defaultdict(float)

    for b in borrowers:
        if b.date:
            # Group by year + month string like "2025-07"
            month_str = b.date.strftime('%Y-%m')
            disbursed_by_month[month_str] += float(b.amount)  # property

    disbursed_labels = sorted(disbursed_by_month.keys())
    disbursed_data = [disbursed_by_month[m] for m in disbursed_labels]

      # Only process data if borrowers exist
    if borrowers.exists():
        # --- Interest over time ---
        interest_amount_by_month = defaultdict(float)
        for b in borrowers:
            if b.date:
                month_str = b.date.strftime('%Y-%m')
                interest_amount_by_month[month_str] += float(b.interest_amount)

        interest_amount_labels = sorted(interest_amount_by_month.keys())
        interest_amount_data = [interest_amount_by_month[m] for m in interest_amount_labels]

    context = {
        'interest_amount_labels_json': json.dumps(interest_amount_labels),
        'interest_amount_data_json': json.dumps(interest_amount_data),
        'outstanding_labels_json': json.dumps(outstanding_labels),
        'outstanding_data_json': json.dumps(outstanding_data),
        'disbursed_labels_json': json.dumps(disbursed_labels),
        'disbursed_data_json': json.dumps(disbursed_data),
        'borrowers': borrowers,
        'clients': clients,
        'total_outstanding_amount': total_outstanding_amount,
        'total_interest_earned': total_interest_earned,
        'total_disbursed_amount': total_disbursed_amount,}
    return render(request,'dashboard/analytics.html', context)

@login_required(login_url= "/accounts/login")
def borrower_detail(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk, author=request.user)
    return render(request, 'dashboard/borrower_detail.html', {'borrower': borrower})

@login_required(login_url='/accounts/login')
def mark_as_paid(request,pk):
     borrower = get_object_or_404(Borrower, pk=pk, author=request.user)
     borrower.mark_as_paid()
     messages.success(request, "Loan marked as paid.")
     return redirect('dashboard')

@login_required(login_url='/accounts/login')
def delete_borrower(request, pk):
    borrower = get_object_or_404(Borrower, pk=pk, author=request.user)

    if request.method == 'POST':
        borrower.delete()
        return redirect('dashboard')  # Or wherever your borrower list is

    # Optional: show confirmation page
    return render(request, 'dashboard/confirm_delete.html', {'borrower': borrower})

@login_required(login_url='/accounts/login')
def transaction_history_view(request):
    selected_month = request.GET.get('month')  # format: 'YYYY-MM'
    borrowers = Borrower.objects.filter(author=request.user).order_by('-date')

    if selected_month:
        year, month = map(int, selected_month.split('-'))
        borrowers = borrowers.filter(date__year=year, date__month=month)

    # Generate list of months to populate dropdown
    months = Borrower.objects.dates('date', 'month', order='DESC')

    context = {
        'borrowers': borrowers,
        'months': months,
        'selected_month': selected_month,
    }
    return render(request, 'dashboard/transaction_history.html', context)
 
@login_required(login_url='/accounts/login')
def download_transactions_pdf(request):
    selected_month = request.GET.get('month')  # Format: 'YYYY-MM'

    borrowers = Borrower.objects.filter(author=request.user).order_by('date')

    if selected_month:
        year, month = map(int, selected_month.split('-'))
        borrowers = borrowers.filter(date__year=year, date__month=month)

    # Create response
    response = HttpResponse(content_type='application/pdf')
    filename = f"Loan_Statement_{selected_month or 'All'}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Setup canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # === HEADER ===
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "CreditGrid Loan Statement")

    p.setFont("Helvetica", 10)
    p.drawString(50, height - 70, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    p.line(50, height - 75, width - 50, height - 75)

    # === USER INFO ===
    p.drawString(50, height - 100, f"User: {request.user.username}")
    p.drawString(50, height - 115, f"Email: {request.user.email}")

    # === COLUMN TITLES ===
    p.setFont("Helvetica-Bold", 11)
    y = height - 150
    p.drawString(50, y, "Name")
    p.drawString(200, y, "Amount")
    p.drawString(280, y, "Interest")
    p.drawString(360, y, "Amount Due")
    p.drawString(470, y, "Due Date")
    y -= 20

    # === DATA ROWS ===
    p.setFont("Helvetica", 10)

    total_disbursed = 0
    total_interest = 0
    total_due = 0

    for b in borrowers:
        if y < 100:  # Page break
            p.showPage()
            y = height - 100
            p.setFont("Helvetica-Bold", 11)
            p.drawString(50, y, "Name")
            p.drawString(200, y, "Amount")
            p.drawString(280, y, "Interest")
            p.drawString(360, y, "Amount Due")
            p.drawString(470, y, "Due Date")
            y -= 20
            p.setFont("Helvetica", 10)

        p.drawString(50, y, str(b.name))
        p.drawString(200, y, f"k{b.amount}")
        p.drawString(280, y, f"{b.interest}%")
        p.drawString(360, y, f"k{b.amount_due}")
        p.drawString(470, y, b.date.strftime("%Y-%m-%d"))
        y -= 18

        total_disbursed += float(b.amount)
        total_interest += float(b.interest_amount)
        total_due += float(b.amount_due)

    # === SUMMARY SECTION ===
    y -= 30
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Summary:")
    y -= 20
    p.setFont("Helvetica", 10) 
    p.drawString(60, y, f"Total Disbursed Amount: k{total_disbursed:.2f}")
    y -= 15
    p.drawString(60, y, f"Total Interest Earned: k{total_interest:.2f}")
    y -= 15
    p.drawString(60, y, f"Total Amount Due: k{total_due:.2f}")

    # Finish up
    p.showPage()
    p.save()
    return response
