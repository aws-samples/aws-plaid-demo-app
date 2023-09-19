import boto3
from botocore.exceptions import ClientError
from reportlab.pdfgen import canvas

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import navy, black
from reportlab.pdfbase.pdfmetrics import stringWidth

client = boto3.client('ses',region_name="us-east-1")


# Custom objects
class policyholder:
    def __init__(self, name, address, email, phoneNumber, isPrimary):
        self.name = name
        self.address = address
        self.email = email
        self.phoneNumber = phoneNumber
        self.isPriary = isPrimary

class vehicle:
    def __init__(self, year, make, model, vin, coverages):
        self.year = year
        self.make = make
        self.model = model
        self.vin = vin
        self.coverages = coverages

class coverage:
    def __init__(self, type, premium, deductible, occurrence):
        self.type = type
        self.premium = premium
        self.deductible = deductible
        self.occurrence = occurrence

def createPolicyHolder(policyHolderInfo):
    name = policyHolderInfo.name.full
    address = ""
    for line in policyHolderInfo.address:
        address += line + " "
    email = policyHolderInfo.email_addresses[0]
    phoneNumber = policyHolderInfo.phone_numbers[0].number
    isPrimary = policyHolderInfo.is_primary
    return policyholder(name, email, phoneNumber, isPrimary)

def createVehicle(vehicle):
    year = vehicle.year
    make = vehicle.make
    model = vehicle.model
    vin = vehicle.vin
    coverages = []
    if vehicle.coverages.uninsured_property:
        coverages.append(coverage("Uninsured Property", vehicle.uninsured_property.premium.value, vehicle.coverages.uninsured_property.deductible, vehicle.coverages.uninsured_property.limits.occurrence.value))
    if vehicle.coverages.underinsured_property:
        coverages.append(coverage("Underinsured Property", vehicle.underinsured_property.premium.value, vehicle.coverages.underinsured_property.deductible, vehicle.coverages.underinsured_property.limits.occurrence.value))
    if vehicle.coverages.personal_injury_protection:
        coverages.append(coverage("Personal Injury Protection", vehicle.coverages.personal_injury_protection.premium.value, vehicle.coverages.personal_injury_protection.deductible, vehicle.coverages.personal_injury_protection.limits.occurrence.value))
    if vehicle.coverages.bodily_injury:
        coverages.append(coverage("Bodily Injury", vehicle.coverages.bodily_injury.premium.value, vehicle.coverages.bodily_injury.deductible, vehicle.coverages.bodily_injury.limits.occurrence.value))
        
    return vehicle(year, make, model, vin, coverages)


def createCoviePdf(pdf, width, height, item):
    # basic policy info
    maskedPolicyNumber = item.masked_number
    policyInceptionDate = item.inception_date
    policyExpirationDate = item.expiration_date
    policyPremiumValue = item.premium.value

    # policy holder info
    policyHolders = []
    for policyHolder in item.policyholders:
        policyHolders.append(createPolicyHolder(policyHolder))

    # vehicle info
    vehicles = []
    for vehicle in item.vehicles:
        vehicles.append(createVehicle(vehicle))
    

    format_covie_pdf(pdf, width, height, maskedPolicyNumber, policyInceptionDate, policyExpirationDate, policyPremiumValue, policyHolders, vehicles)

    pdf.showPage()
    pdf.save()

def createPlaidPayrollPdf(pdf, width, height, item):
    # employer info
    employerName = item.payroll_income[0].pay_stubs[0].employer.name
    employerStreet = item.payroll_income[0].pay_stubs[0].employer.address.street
    employerTownAndZip = item.payroll_income[0].pay_stubs[0].employer.address.city + ", " + item.payroll_income[0].pay_stubs[0].employer.address.region + " " + item.payroll_income[0].pay_stubs[0].employer.address.postal_code

    # employee info
    employeeName = item.payroll_income[0].pay_stubs[0].employee.name
    employeeStreet = item.payroll_income[0].pay_stubs[0].employee.address.street
    employeeTownAndZip = item.payroll_income[0].pay_stubs[0].employee.address.city + ", " + item.payroll_income[0].pay_stubs[0].employee.address.region + " " + item.payroll_income[0].pay_stubs[0].employee.address.postal_code

    # pay period info
    payPeriodStart = item.payroll_income[0].pay_stubs[0].pay_period_details.start_date
    payPeriodEnd = item.payroll_income[0].pay_stubs[0].pay_period_details.end_date
    payDate = item.payroll_income[0].pay_stubs[0].pay_period_details.pay_date

    # payment summary info 
    grossEarnings = item.payroll_income[0].pay_stubs[0].pay_period_details.gross_earnings
    totalTaxesAndDeductions = item.payroll_income[0].pay_stubs[0].deductions.total.current_amount
    netPay = item.payroll_income[0].pay_stubs[0].net_pay.current_amount
    bankName = item.payroll_income[0].pay_stubs[0].pay_period_details.distribution_breakdown[0].bank_name
    bankMask = item.payroll_income[0].pay_stubs[0].pay_period_details.distribution_breakdown[0].mask

    # gross earnings info
    currentSalary = 0
    ytdSalary = 0
    currentSupplementalBonus = 0
    ytdSupplementalBonus = 0
    currentOvertime = 0
    ytdOvertime = 0
    currentCommission = 0
    ytdCommission = 0
    for breakdown in item.payroll_income[0].pay_stubs[0].earnings.breakdown:
        if breakdown.canonical_description == "REGULAR_PAY":
            currentSalary = breakdown.current_amount
            ytdSalary = breakdown.ytd_amount            
        if breakdown.canonical_description == "BONUS":
            currentSupplementalBonus = breakdown.current_amount
            ytdSupplementalBonus = breakdown.ytd_amount 
        if breakdown.canonical_description == "OVERTIME":
            currentOvertime = breakdown.current_amount
            ytdOvertime = breakdown.ytd_amount
        if breakdown.canonical_description == "COMMISSION":
            currentCommission = breakdown.current_amount
            ytdCommission = breakdown.ytd_amount
    currentTotalEarnings = currentSalary + currentSupplementalBonus + currentOvertime + currentCommission
    ytdTotalEarnings = ytdSalary + ytdSupplementalBonus + ytdOvertime + ytdCommission
 
    # taxes withheld info
    currentFederalIncomeTax = item.payroll_income[0].w2s[0].federal_income_tax_withheld
    currentSocialSecurity = item.payroll_income[0].w2s[0].social_security_wages
    currentMedicare = item.payroll_income[0].w2s[0].medicare_tax_withheld
    currentStateTax = item.payroll_income[0].w2s[0].state_and_local_wages[0].state_income_tax
    currentTotalTaxWithheld = item.payroll_income[0].pay_stubs[0].deductions.total.current_amount
    ytdTotalTaxWithheld = item.payroll_income[0].pay_stubs[0].deductions.total.ytd_amount

    format_plaid_income(pdf, width, height, employerName, employerStreet, employerTownAndZip,
                        employeeName, employeeStreet, employeeTownAndZip,
                        str(payPeriodStart), str(payPeriodEnd), str(payDate),
                        str(grossEarnings), str(totalTaxesAndDeductions), str(netPay), bankName, str(bankMask),
                        str(currentSalary), str(ytdSalary), str(currentSupplementalBonus), str(ytdSupplementalBonus), str(currentOvertime), str(ytdOvertime), str(currentCommission), str(ytdCommission), str(currentTotalEarnings), str(ytdTotalEarnings),
                        str(currentFederalIncomeTax), str(currentSocialSecurity), str(currentMedicare), str(currentStateTax), str(currentTotalTaxWithheld), str(ytdTotalTaxWithheld))
    pdf.showPage()
    pdf.save()


def format_covie_pdf(pdf, width, height, maskedPolicyNumber, policyInceptionDate, policyExpirationDate, policyPremiumValue, policyHolders, vehicles):

    heightTracker = 0.75

    # Add CaseSwift Header
    headerString = "CaseSwift Income Verification Statement"
    pdf.setFont("Helvetica-Bold", 10)
    pdf.setFillColor(navy)
    headerStringWidth = stringWidth(headerString, "Helvetica-Bold", 10)
    pdf.drawString((width - headerStringWidth)/2, height-(heightTracker*inch), headerString)
    heightTracker += 0.1
    pdf.line((width/2)-(headerStringWidth/2), height-(inch*heightTracker), (width/2)+(headerStringWidth/2), height-(inch*heightTracker))

    # Draw Basic Policy Info
    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.35
    pdf.drawString((inch*1.1), height-(1.2*inch), "Basic Coverage Info:")
    pdf.setFont("Helvetica", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Masked Policy Number: " + maskedPolicyNumber)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Inception Date: " + policyInceptionDate)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Expiration Date: " + policyExpirationDate)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Premium Value: " + policyPremiumValue)

    # Box Basic Policy Info
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-(heightTracker*inch), width-(1.8*inch), inch*1.5)

    # Draw Policy Holder Info
    heightTracker += 0.35

    for policyHolder in policyHolders:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Holder Name: ")
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), policyHolder.name)
        heightTracker += 0.2
        
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Holder Address: ")
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), policyHolder.address)
        heightTracker += 0.2

        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Holder Email: ")
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), policyHolder.email)
        heightTracker += 0.2

        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Holder Phone Number: ")
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), policyHolder.phoneNumber)
        heightTracker += 0.2

        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Policy Holder Primary Status: ")
        pdf.setFont("Helvetica", 10)
        pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), policyHolder.isPrimary)
        heightTracker += 0.2
    
    # Box Policy Holder Info
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-heightTracker*inch), width-(1.8*inch), inch*(1*len(policyHolders))

    # Draw Vehicle Info

    heightTracker += 0.7
    vehicleBoxHeightCounter = 0.1
    for vehicle in vehicles:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Vehicle Info: ")
        pdf.setFont("Helvetica", 10)
        basicVehicleInfo = vehicle.make + " " + vehicle.model + " " + vehicle.year
        pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), basicVehicleInfo)
        heightTracker += 0.2

        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Vehicle VIN: ")
        pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), vehicle.vin)
        heightTracker += 0.2

        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString((inch*1.1), height-(heightTracker*inch), "Vehicle Coverages: ")
        pdf.setFont("Helvetica", 10)
        heightTracker += 0.2

        vehicleBoxHeightCounter += 0.6

        for coverage in vehicle.coverages:
            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawString((inch*1.1), height-(heightTracker*inch), "Coverage Type: ")
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), coverage.type)
            heightTracker += 0.2

            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawString((inch*1.1), height-(heightTracker*inch), "Coverage Premium: ")
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), coverage.premium)
            heightTracker += 0.2

            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawString((inch*1.1), height-(heightTracker*inch), "Coverage Deductible: ")
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), coverage.deductible)
            heightTracker += 0.2

            pdf.setFont("Helvetica-Bold", 8)
            pdf.drawString((inch*1.1), height-(heightTracker*inch), "Coverage Occurrence: ")
            pdf.setFont("Helvetica", 8)
            pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), coverage.occurrence)
            heightTracker += 0.2

            vehicleBoxHeightCounter += 0.8
    
    # Box Vehicle Info
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-heightTracker*inch), width-(1.8*inch), inch*(1*vehicleBoxHeightCounter)




def format_plaid_income(pdf, width, height, employerName, employerStreet, employerTownAndZip,
                        employeeName, employeeStreet, employeeTownAndZip,
                        payPeriodStart, payPeriodEnd, payDate,
                        grossEarnings, totalTaxesAndDeductions, netPay, bankName, bankMask,
                        currentSalary, ytdSalary, currentSupplementalBonus, ytdSupplementalBonus, currentOvertime, ytdOvertime, currentCommission, ytdCommission, currentTotalEarnings, ytdTotalEarnings,
                        currentFederalIncomeTax, currentSocialSecurity, currentMedicare, currentStateTax, currentTotalTaxWithheld, ytdTotalTaxWithheld):
    
    heightTracker = 0.75
    
    # Add CaseSwift Header
    headerString = "CaseSwift Income Verification Statement"
    pdf.setFont("Helvetica-Bold", 10)
    pdf.setFillColor(navy)
    headerStringWidth = stringWidth(headerString, "Helvetica-Bold", 10)
    pdf.drawString((width - headerStringWidth)/2, height-(heightTracker*inch), headerString)
    heightTracker += 0.1
    pdf.line((width/2)-(headerStringWidth/2), height-(inch*heightTracker), (width/2)+(headerStringWidth/2), height-(inch*heightTracker))

    # Draw Employer and Employee Information
    pdf.setFillColor(black)
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.35
    pdf.drawString((inch*1.1), height-(1.2*inch), "Employer:")
    pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), "Employee:")
    pdf.setFont("Helvetica", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), employerName)
    pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), employeeName)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), employerStreet)
    pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), employeeStreet)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), employerTownAndZip)
    pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), employeeTownAndZip)

    # Box Employer/Employee
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-(heightTracker*inch), width-(1.8*inch), inch*1.3)

    # Draw Pay Period Information
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.7
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Pay Period Start: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), payPeriodStart)

    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Pay Period End: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), payPeriodEnd)

    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Pay Date: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString(width-(inch*1.1), height-(heightTracker*inch), payDate)

    #Box Pay Period Information
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-(heightTracker*inch), (width-(1.8*inch)), inch*0.7)

    # Draw Payment Summary Information
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    paymentSummaryStringWidth = stringWidth("Payment Summary", "Helvetica-Bold", 10)
    pdf.drawString((width - paymentSummaryStringWidth)/2, height-(heightTracker*inch), "Payment Summary")

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Gross Earnings: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), grossEarnings)

    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Total Taxes and Deductions: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), totalTaxesAndDeductions)

    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Net Pay: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), netPay)

    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Direct Deposit To: ")
    pdf.setFont("Helvetica", 10)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), bankName + "-" + bankMask)

    # Box Payment Summary Information
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-(heightTracker*inch), width-(1.8*inch), inch*1.1)

    # Draw Gross Earnings Section
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    grossEarningsSummaryWidth = stringWidth("Gross Earnings", "Helvetica-Bold", 10)
    pdf.drawString((width - grossEarningsSummaryWidth)/2, height-(heightTracker*inch), "Gross Earnings")
    
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Description")
    currentStringWidth = stringWidth("Current", "Helvetica-Bold", 10)
    pdf.drawString((width-currentStringWidth)/2, height-(heightTracker*inch), "Current")
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), "YTD")

    pdf.setFont("Helvetica", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Salary")
    currentSalaryWidth = stringWidth(currentSalary, "Helvetica", 10)
    pdf.drawString((width-currentSalaryWidth)/2, height-(heightTracker*inch), currentSalary)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), ytdSalary)

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Supplemental pay: Bonus")
    currentSupplementalBonusWidth = stringWidth(currentSupplementalBonus, "Helvetica", 10)
    pdf.drawString((width-currentSupplementalBonusWidth)/2, height-(heightTracker*inch), currentSupplementalBonus)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), ytdSupplementalBonus)

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Supplemental Pay: Overtime")
    currentSupplementalOvertimeWidth = stringWidth(currentOvertime, "Helvetica", 10)
    pdf.drawString((width-currentSupplementalOvertimeWidth)/2, height-(heightTracker*inch), currentOvertime)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), ytdOvertime)

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Supplemental Pay: Commission")
    currentCommissionWidth = stringWidth(currentCommission, "Helvetica", 10)
    pdf.drawString((width-currentCommissionWidth)/2, height-(heightTracker*inch), currentCommission)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), ytdCommission)

    heightTracker += 0.1
    pdf.line((inch*1.1), height-(heightTracker*inch), width-(inch*1.1), height-(heightTracker*inch))

    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Gross Earnings Totals")
    currentTotalWidth = stringWidth(currentTotalEarnings, "Helvetica-Bold", 10)
    pdf.drawString((width-currentTotalWidth)/2, height-(heightTracker*inch), currentTotalEarnings)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), ytdTotalEarnings)

    # Box Gross Earnings Section
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-(heightTracker*inch), width-(1.8*inch), inch*1.6)

    # Draw Taxes Withheld Section
    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    taxesWithheldWidth = stringWidth("Taxes Withheld", "Helvetica-Bold", 10)
    pdf.drawString((width - taxesWithheldWidth)/2, height-(heightTracker*inch), "Taxes Withheld")

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Description")
    currentStringWidth = stringWidth("Current", "Helvetica-Bold", 10)
    pdf.drawString((width-currentStringWidth)/2, height-(heightTracker*inch), "Current")
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), "YTD")

    pdf.setFont("Helvetica", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Federal Income Tax")
    currentFederalIncomeTaxWidth = stringWidth(currentFederalIncomeTax, "Helvetica", 10)
    pdf.drawString((width-currentFederalIncomeTaxWidth)/2, height-(heightTracker*inch), currentFederalIncomeTax)

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Social Security")
    currentSocialSecurityWidth = stringWidth(currentSocialSecurity, "Helvetica", 10)
    pdf.drawString((width-currentSocialSecurityWidth)/2, height-(heightTracker*inch), currentSocialSecurity)

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Medicare")
    currentMedicareWidth = stringWidth(currentMedicare, "Helvetica", 10)
    pdf.drawString((width-currentMedicareWidth)/2, height-(heightTracker*inch), currentMedicare)

    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "State Income Tax")
    currentStateTaxWidth = stringWidth(currentStateTax, "Helvetica", 10)
    pdf.drawString((width-currentStateTaxWidth)/2, height-(heightTracker*inch), currentStateTax)

    heightTracker += 0.1
    pdf.line((inch*1.1), height-(heightTracker*inch), width-(inch*1.1), height-(heightTracker*inch))

    pdf.setFont("Helvetica-Bold", 10)
    heightTracker += 0.2
    pdf.drawString((inch*1.1), height-(heightTracker*inch), "Taxes Withheld Totals")
    currentTotalTaxesWidth = stringWidth(currentTotalTaxWithheld, "Helvetica-Bold", 10)
    pdf.drawString((width-currentTotalTaxesWidth)/2, height-(heightTracker*inch), currentTotalTaxWithheld)
    pdf.drawRightString((width-(inch*1.1)), height-(heightTracker*inch), ytdTotalTaxWithheld)

    # Box Taxes Withheld Section
    pdf.setFont("Helvetica-Bold", 6)
    heightTracker += 0.1
    pdf.rect(0.9*inch, height-(heightTracker*inch), width-(1.8*inch), inch*1.6)

    pdf.setFillColor(navy)
    heightTracker += 3.6
    footerMessage = "Information Provided by CaseSwift: The GOAT PI SAAS Platform"
    footerLength = stringWidth(footerMessage, "Helvetica-Bold", 6)
    currentStringWidth = stringWidth("Current", "Helvetica-Bold", 10)
    pdf.drawString((width-footerLength)/2, height-(10.5*inch), footerMessage)

def send_email(sender, recipient, plaidResponseObject):
    msg = MIMEMultipart()
    msg['Subject'] = 'Your Requested Documents from CaseSwift'
    msg['From'] = sender
    msg['To'] = recipient

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'CaseSwift Documents.\n'

    # the message body
    part = MIMEText('Howdy -- here are your requested Documents')
    msg.attach(part)

    counter = 1
    for item in plaidResponseObject.items:
        pdfName = "plaid_income_verification" + str(counter) + ".pdf"
        plaidFinancialInformationPdf = canvas.Canvas("/tmp/" + pdfName, pagesize=letter)
        width, height = letter
        createPlaidPayrollPdf(plaidFinancialInformationPdf, width, height, item)
        part = MIMEApplication(open("/tmp/"+ pdfName, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=pdfName)
        msg.attach(part)
        counter+=1

    # and send the message
    try: 

        response = client.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']],
            RawMessage={
            'Data': msg.as_string()
        },)

    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def send_covie_email(sender, recipient, covieResponsesArray):
    msg = MIMEMultipart()
    msg['Subject'] = 'Your Requested Documents from CaseSwift'
    msg['From'] = sender
    msg['To'] = recipient

    logger.info('here')
    logger.info('response')
    # what a recipient sees if they don't use an email reader
    msg.preamble = 'CaseSwift Documents.\n'

    # the message body
    part = MIMEText('Howdy -- here are your requested Documents')
    msg.attach(part)
    
    counter = 1
    for item in covieResponsesArray:
        pdfName = "covie_auto_verification" + str(counter) + ".pdf"
        covieAutoInfoPdf = canvas.Canvas("/tmp/" + pdfName, pagesize=letter)
        width, height = letter
        createCoviePdf(covieAutoInfoPdf, width, height, item)
        part = MIMEApplication(open("/tmp/"+ pdfName, 'rb').read())
        part.add_header('Content-Disposition', 'attachment', filename=pdfName)
        msg.attach(part)
        counter+=1

    # and send the message
    response = client.send_raw_email(
        Source=msg['From'],
        Destinations=[msg['To']],
        RawMessage={
            'Data': covieResponsesArray.join(", ")
        },)

    logger.info('here')
    logger.info('response')
